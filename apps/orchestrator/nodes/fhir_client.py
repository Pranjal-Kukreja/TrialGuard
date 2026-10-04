"""
FHIR R4 Client for auto-resupplying baseline patient demographics and clinical observations.
Converts FHIR R4 resources into the internal PatientData TypedDict representation.

Updated to synchronize with:
  - Strict sex normalization to 'female' / 'male' (conforming to state.py and baseline safety rules)
  - Custom Hackathon/TrialGuard coding systems alongside standard LOINC mappings
  - Extended observation routing (last_systemic_therapy_date, ecog_status, consent_capacity,
    pregnancy_test_result, days_since_PCI, days_since_acute_coronary_syndrome)
  - Extraction of trial_id, cohort, dob, and protocol ground facts
  - Graceful fallback to local synthetic fixtures (patients_expanded.json) when offline
"""

from datetime import date, datetime
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests

logger = logging.getLogger(__name__)

FHIR_BASE_URL = (
    os.getenv("FHIR_BASE_URL")
    or os.getenv("FHIR_SERVER_URL", "https://hapi.fhir.org/baseR4")
).rstrip("/")
FHIR_AUTH_TOKEN = os.getenv("FHIR_AUTH_TOKEN", "")
FHIR_TIMEOUT_SECONDS = float(os.getenv("FHIR_TIMEOUT_SECONDS", "4.0"))

CODE_SYSTEM = "https://techquest-hackathon.local/lab-codes"
TAG_SYSTEM = "https://techquest-hackathon.local/tags"

LOINC_MAP = {
    # --- LabResults ---
    "2160-0": ("lab_results", "serum_creatinine"),
    "38483-4": ("lab_results", "creatinine_clearance"),
    "33914-3": ("lab_results", "eGFR"),
    "48642-3": ("lab_results", "eGFR"),
    "48643-1": ("lab_results", "eGFR"),
    "1751-7": ("lab_results", "ALT"),
    "1920-8": ("lab_results", "AST"),
    "777-3": ("lab_results", "platelets"),
    "26515-7": ("lab_results", "platelets"),
    "718-7": ("lab_results", "hemoglobin"),
    "6301-6": ("lab_results", "INR"),
    "1975-2": ("lab_results", "total_bilirubin"),
    "26499-4": ("lab_results", "ANC"),
    "751-8": ("lab_results", "ANC"),
    # --- VitalSigns ---
    "8867-4": ("vital_signs", "heart_rate"),
    "8480-6": ("vital_signs", "blood_pressure_systolic"),
    "8462-4": ("vital_signs", "blood_pressure_diastolic"),
    # --- CardiacFunction ---
    "10230-1": ("cardiac_function", "LVEF"),
    "8806-2": ("cardiac_function", "LVEF"),
    "18485-3": ("cardiac_function", "QTc"),
    "48672-0": ("cardiac_function", "QTc"),
}

# Custom mapping for direct observations seeded in TrialGuard
CUSTOM_CODE_MAP = {
    # Labs
    "ALT": ("lab_results", "ALT"),
    "AST": ("lab_results", "AST"),
    "eGFR": ("lab_results", "eGFR"),
    "ANC": ("lab_results", "ANC"),
    "platelets": ("lab_results", "platelets"),
    "hemoglobin": ("lab_results", "hemoglobin"),
    "INR": ("lab_results", "INR"),
    "total_bilirubin": ("lab_results", "total_bilirubin"),
    "serum_creatinine": ("lab_results", "serum_creatinine"),
    "creatinine_clearance": ("lab_results", "creatinine_clearance"),
    # Vitals
    "heart_rate": ("vital_signs", "heart_rate"),
    "blood_pressure_systolic": ("vital_signs", "blood_pressure_systolic"),
    "blood_pressure_diastolic": ("vital_signs", "blood_pressure_diastolic"),
    # Cardiac
    "LVEF": ("cardiac_function", "LVEF"),
    "QTc": ("cardiac_function", "QTc"),
    # Demographics / Clinical status (root fields)
    "weight": (None, "weight"),
    "ecog_status": (None, "ecog_status"),
    "consent_capacity": (None, "consent_capacity"),
    "pregnancy_test_result": (None, "pregnancy_test_result"),
    "last_systemic_therapy_date": (None, "last_systemic_therapy_date"),
    "medical_history_narrative": (None, "medical_history_narrative"),
    # Protocol facts
    "oral_anticoagulation_required": ("protocol_facts", "oral_anticoagulation_required"),
    "planned_or_existing_oral_anticoagulation": ("protocol_facts", "oral_anticoagulation_required"),
    "acs_pathway": ("protocol_facts", "acs_pathway"),
    "days_since_acute_coronary_syndrome": ("protocol_facts", "days_since_acute_coronary_syndrome"),
    "pci_pathway": ("protocol_facts", "pci_pathway"),
    "days_since_PCI": ("protocol_facts", "days_since_PCI"),
    "planned_p2y12_duration": ("protocol_facts", "planned_p2y12_duration"),
    "history_of_intracranial_hemorrhage": ("protocol_facts", "history_of_intracranial_hemorrhage"),
    "prior_bleeding": ("protocol_facts", "history_of_intracranial_hemorrhage"),
    "ongoing_bleeding": ("protocol_facts", "ongoing_bleeding"),
    "known_coagulopathy": ("protocol_facts", "known_coagulopathy"),
    "cabg_for_index_acs": ("protocol_facts", "cabg_for_index_acs"),
    "other_condition_requiring_chronic_anticoagulation": ("protocol_facts", "other_condition_requiring_chronic_anticoagulation"),
    "drug_contraindication": ("protocol_facts", "drug_contraindication"),
    "pregnant": ("protocol_facts", "pregnant"),
    "breastfeeding": ("protocol_facts", "breastfeeding"),
    "woman_of_childbearing_potential": ("protocol_facts", "woman_of_childbearing_potential"),
    "pregnancy_test_negative": ("protocol_facts", "pregnancy_test_negative"),
}


def _get_headers() -> Dict[str, str]:
    headers = {
        "Accept": "application/fhir+json",
        "Content-Type": "application/fhir+json",
    }
    if FHIR_AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {FHIR_AUTH_TOKEN}"
    return headers


def _calculate_age(birth_date_str: str) -> Optional[int]:
    """Calculate age in years from FHIR birthdate (YYYY-MM-DD)."""
    try:
        birth_date = datetime.strptime(birth_date_str.split("T")[0], "%Y-%m-%d").date()
        today = date.today()
        return today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )
    except Exception as e:
        logger.warning("Failed to parse birthDate '%s': %s", birth_date_str, e)
        return None


def _normalize_gender(gender_val: Any) -> str:
    """Standardize sex representation to 'female' or 'male' matching PatientData."""
    s = str(gender_val or "").strip().lower()
    if s in ["female", "f"]:
        return "female"
    if s in ["male", "m"]:
        return "male"
    return str(gender_val) if gender_val else "unknown"


def _extract_primitive_observation(resource: Dict[str, Any]) -> Any:
    """Extracts scalar observation values including quantities, strings, booleans, and concepts."""
    if "valueQuantity" in resource:
        return resource["valueQuantity"].get("value")
    if "valueInteger" in resource:
        return resource["valueInteger"]
    if "valueBoolean" in resource:
        return resource["valueBoolean"]
    if "valueString" in resource:
        return resource["valueString"]
    if "valueDateTime" in resource:
        return resource["valueDateTime"]
    if "valueCodeableConcept" in resource:
        cc = resource["valueCodeableConcept"]
        return cc.get("text") or (cc.get("coding", [{}])[0].get("display")) or (cc.get("coding", [{}])[0].get("code"))
    return None


def fetch_patient_demographics(patient_id: str) -> Dict[str, Any]:
    """Queries GET /Patient/{id} and returns normalized demographic fields."""
    if not FHIR_BASE_URL or not patient_id:
        return {}

    url = f"{FHIR_BASE_URL}/Patient/{patient_id}"
    try:
        resp = requests.get(url, headers=_get_headers(), timeout=FHIR_TIMEOUT_SECONDS)
        if resp.status_code != 200:
            logger.warning("FHIR Patient lookup failed (%s): HTTP %d", url, resp.status_code)
            return {}

        resource = resp.json()
        demographics: Dict[str, Any] = {
            "patient_id": patient_id,
        }

        if "gender" in resource:
            demographics["sex"] = _normalize_gender(resource["gender"])

        if "birthDate" in resource:
            bdate = resource["birthDate"]
            demographics["dob"] = bdate
            demographics["birth_date"] = bdate
            age = _calculate_age(bdate)
            if age is not None:
                demographics["age"] = age

        names = resource.get("name", [])
        if names:
            demographics["name"] = (
                names[0].get("text")
                or f"{' '.join(names[0].get('given', []))} {names[0].get('family', '')}".strip()
            )

        for ext in resource.get("extension", []):
            url_str = ext.get("url", "")
            if "trial_id" in url_str:
                demographics["trial_id"] = ext.get("valueString")
            elif "cohort" in url_str:
                demographics["cohort"] = ext.get("valueString")

        for ident in resource.get("identifier", []):
            if ident.get("system") == TAG_SYSTEM:
                demographics["internal_id"] = ident.get("value")

        return demographics
    except Exception as e:
        logger.warning("FHIR connection error on %s: %s", url, e)
        return {}


def fetch_patient_observations(patient_id: str) -> Dict[str, Any]:
    """Queries GET /Observation?patient={id}&_sort=-date
    Extracts latest values mapped into lab_results, vital_signs, cardiac_function,
    protocol_facts, and root attributes.
    """
    if not FHIR_BASE_URL or not patient_id:
        return {}

    url = f"{FHIR_BASE_URL}/Observation"
    params = {
        "patient": patient_id,
        "_sort": "-date",
        "_count": "80",
    }

    try:
        resp = requests.get(url, headers=_get_headers(), params=params, timeout=FHIR_TIMEOUT_SECONDS)
        if resp.status_code != 200:
            logger.warning("FHIR Observation lookup failed: HTTP %d", resp.status_code)
            return {}

        bundle = resp.json()
        categorized_results: Dict[str, Dict[str, Any]] = {
            "lab_results": {},
            "vital_signs": {},
            "cardiac_function": {},
            "protocol_facts": {},
        }
        root_results: Dict[str, Any] = {}

        for entry in bundle.get("entry", []):
            resource = entry.get("resource", {})
            val = _extract_primitive_observation(resource)
            if val is None:
                continue

            codings = resource.get("code", {}).get("coding", [])
            code_text = resource.get("code", {}).get("text")

            target_mapping = None

            # 1. Check custom TrialGuard coding system
            for coding in codings:
                system = coding.get("system")
                code = coding.get("code")
                if system == CODE_SYSTEM and code in CUSTOM_CODE_MAP:
                    target_mapping = CUSTOM_CODE_MAP[code]
                    break

            # 2. Check standard LOINC codes
            if not target_mapping:
                for coding in codings:
                    code = coding.get("code")
                    if code in LOINC_MAP:
                        target_mapping = LOINC_MAP[code]
                        break

            # 3. Fallback on code text if direct parameter name
            if not target_mapping and code_text in CUSTOM_CODE_MAP:
                target_mapping = CUSTOM_CODE_MAP[code_text]

            if not target_mapping:
                continue

            category, metric_name = target_mapping

            # Parse string lists for drug contraindications
            if metric_name == "drug_contraindication" and isinstance(val, str):
                try:
                    val = json.loads(val)
                except Exception:
                    val = [x.strip() for x in val.split(",") if x.strip()] if val else []

            parsed_val = float(val) if isinstance(val, (int, float)) and not isinstance(val, bool) else val

            if category is None:
                if metric_name not in root_results:
                    root_results[metric_name] = parsed_val
            else:
                if metric_name not in categorized_results[category]:
                    categorized_results[category][metric_name] = parsed_val

        final_output: Dict[str, Any] = {
            cat: data for cat, data in categorized_results.items() if data
        }
        final_output.update(root_results)
        return final_output

    except Exception as exc:
        logger.warning("FHIR Observation query failed: %s", exc)
        return {}


def _fallback_from_expanded_json(patient_id: str) -> Dict[str, Any]:
    """Reads local patients_expanded.json fixture if the HAPI server is offline or record is missing."""
    repo_root = Path(__file__).resolve().parents[4] if len(Path(__file__).resolve().parents) >= 5 else Path(__file__).resolve().parents[2]
    candidates = [
        Path(__file__).resolve().parent / "patients_expanded.json",
        Path(__file__).resolve().parents[1] / "patients_expanded.json",
        repo_root / "packages" / "mcp-ehr" / "src" / "mcp_ehr" / "patients_expanded.json",
        repo_root / "packages" / "mcp-ehr" / "src" / "patients_expanded.json",
        repo_root / "data" / "patients_expanded.json",
    ]
    for path in candidates:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                for entry in data.get("patients", []):
                    p = entry.get("patient", entry)
                    pid = str(entry.get("patient_id") or p.get("patient_id"))
                    iid = str(p.get("internal_id") or pid)
                    fid = str(p.get("fhir_id") or entry.get("fhir_id", ""))
                    if patient_id in (pid, iid, fid):
                        result = dict(p)
                        result["patient_id"] = pid
                        result["internal_id"] = iid
                        result["trial_id"] = (
                            entry.get("assigned_demo_trial_id")
                            or entry.get("trial_id")
                            or p.get("trial_id")
                        )
                        result["cohort"] = entry.get("cohort") or p.get("cohort")
                        result["sex"] = _normalize_gender(result.get("sex"))

                        # Flatten nested {'value': ...} structures
                        for bucket in ("lab_results", "vital_signs", "cardiac_function"):
                            if bucket in result and isinstance(result[bucket], dict):
                                result[bucket] = {
                                    k: (v.get("value") if isinstance(v, dict) else v)
                                    for k, v in result[bucket].items()
                                }

                        return result
            except Exception:
                pass
    return {}


def try_autoresupply_from_fhir(patient_id: str, missing_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """Primary interface for data_resupply_node.
    Inspects missing fields, executes targeted FHIR queries, and falls back to local fixtures.
    """
    if not patient_id:
        return {}

    resolved: Dict[str, Any] = {}
    fields = missing_fields or []

    # If missing_fields not specified, fetch all available demographics and observations
    needs_demographics = not fields or any(
        f in [
            "patient.age", "patient.sex", "age", "sex",
            "patient.name", "trial_id", "patient.dob", "dob"
        ]
        for f in fields
    )
    if needs_demographics and FHIR_BASE_URL:
        demo = fetch_patient_demographics(patient_id)
        resolved.update(demo)

    needs_observations = not fields or any(
        f.startswith("patient.lab_results")
        or f.startswith("lab_results")
        or f.startswith("patient.vital_signs")
        or f.startswith("vital_signs")
        or f.startswith("patient.cardiac_function")
        or f.startswith("cardiac_function")
        or f.startswith("patient.protocol_facts")
        or f.startswith("protocol_facts")
        or f in [
            "patient.weight", "patient.ecog_status", "patient.consent_capacity",
            "patient.pregnancy_test_result", "patient.last_systemic_therapy_date"
        ]
        for f in fields
    )
    if needs_observations and FHIR_BASE_URL:
        observations = fetch_patient_observations(patient_id)
        if observations:
            resolved.update(observations)

    # If FHIR server returned incomplete data, hydrate missing elements from local fixture
    still_lacks = (not fields) or any(f.replace("patient.", "") not in resolved for f in fields)
    if still_lacks:
        fixture_data = _fallback_from_expanded_json(patient_id)
        if fixture_data:
            for k, v in fixture_data.items():
                if k not in resolved or not resolved[k]:
                    resolved[k] = v

    # Final sanity standardization on sex
    if "sex" in resolved:
        resolved["sex"] = _normalize_gender(resolved["sex"])

    logger.info("FHIR auto-resupply resolved keys: %s", list(resolved.keys()))
    return resolved


# Provide public alias for orchestrator ingestion endpoints
get_patient = try_autoresupply_from_fhir