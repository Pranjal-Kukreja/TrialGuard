"""
Seeds synthetic patients from patients_expanded.json directly onto
the public HAPI FHIR R4 server as standard FHIR transaction Bundles.

Updates include:
  - Preserves exact demographics (trial_id, cohort, official name, dob)
  - Formats sex according to FHIR R4 requirements ('male', 'female', 'other', 'unknown')
  - Maps human names cleanly to HumanName resources
  - Supports last_systemic_therapy_date, ecog_status, and full protocol_facts
  - Saves full metadata mapping (fhir_id, name, trial_id, cohort) to seeded_patient_ids.json

Run:
    python seed_data.py
    # or
    python seed_data.py --all
"""

import json
import os
import re
import sys
import time
import uuid
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx

_pkg_dir = str(Path(__file__).parent)
if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)

from fhir_codes import CODE_SYSTEM, FIELD_ROUTES, HACKATHON_TAG_CODE, HACKATHON_TAG_SYSTEM

FHIR_BASE_URL = (
    os.getenv("FHIR_BASE_URL")
    or os.getenv("FHIR_SERVER_URL", "https://hapi.fhir.org/baseR4")
).rstrip("/")

_OUTPUT_PATH = Path(__file__).parent / "seeded_patient_ids.json"
_EXPANDED_JSON_PATH = Path(__file__).resolve().parent / "patients_expanded.json"


def _generate_medical_history_narrative(p: Dict[str, Any]) -> str:
    """Produces a clean 3-4 line clinical summary from patient fixture fields."""
    age = p.get("age", "Unknown")
    sex = p.get("sex", "individual")
    diagnoses = ", ".join(p.get("diagnoses", [])) or "No active chronic diagnoses"
    meds = ", ".join(p.get("medications", [])) or "None reported"

    raw_history = p.get("medical_history")
    if isinstance(raw_history, list):
        history = ", ".join(raw_history) or "No prior documented procedures"
    elif isinstance(raw_history, dict):
        history = ", ".join(f"{k}: {v}" for k, v in raw_history.items())
    else:
        history = "No prior documented procedures"

    allergies = ", ".join(p.get("allergies", [])) or "No known drug allergies (NKDA)"

    line1 = f"Patient is a {age}-year-old {sex} presenting with a primary history of {diagnoses}."
    line2 = f"Active pharmacological regimen includes {meds}, with recorded allergies to {allergies}."
    line3 = f"Relevant past interventions and procedures include {history}."
    line4 = "Baseline organ function and hematologic profiles have been verified for clinical trial evaluation."

    return f"{line1}\n{line2}\n{line3}\n{line4}"


def _normalize_gender(raw_sex: Any) -> str:
    """Standardizes sex to valid FHIR R4 administrative gender values."""
    s = str(raw_sex or "").strip().lower()
    if s in ["m", "male"]:
        return "male"
    if s in ["f", "female"]:
        return "female"
    if s in ["other", "transgender"]:
        return "other"
    return "unknown"


def _load_patients_from_json() -> List[Dict[str, Any]]:
    """Loads and normalizes patient records from patients_expanded.json."""
    if not _EXPANDED_JSON_PATH.exists():
        raise FileNotFoundError(f"Missing fixture file: {_EXPANDED_JSON_PATH}")

    data = json.loads(_EXPANDED_JSON_PATH.read_text(encoding="utf-8"))
    raw_list = data.get("patients", [])
    normalized: List[Dict[str, Any]] = []

    current_year = date.today().year

    for item in raw_list:
        p = item.get("patient", item)
        internal_id = item.get("patient_id") or p.get("patient_id")
        trial_id = item.get("assigned_demo_trial_id") or item.get("trial_id") or p.get("trial_id")
        cohort = item.get("cohort") or p.get("cohort") or "Cohort A - Standard Protocol"
        name = item.get("name") or p.get("name") or f"Patient {internal_id}"

        # Age and birth date derivation
        age = p.get("age", 50)
        birth_date = p.get("dob") or p.get("birth_date")
        if not birth_date:
            birth_year = current_year - age
            birth_date = f"{birth_year}-01-15"

        # Unpack scalar values from {'value': ..., 'unit': ...} dicts
        labs: Dict[str, Any] = {}
        for k, v in (p.get("lab_results") or {}).items():
            labs[k] = v.get("value") if isinstance(v, dict) else v

        vitals: Dict[str, Any] = {}
        for k, v in (p.get("vital_signs") or {}).items():
            vitals[k] = v.get("value") if isinstance(v, dict) else v

        cardiac: Dict[str, Any] = {}
        for k, v in (p.get("cardiac_function") or {}).items():
            cardiac[k] = v.get("value") if isinstance(v, dict) else v

        patient_record = {
            "internal_id": internal_id,
            "patient_id": internal_id,
            "trial_id": trial_id,
            "cohort": cohort,
            "name": name,
            "age": age,
            "sex": _normalize_gender(p.get("sex")),
            "birth_date": birth_date,
            "weight": p.get("weight"),
            "diagnoses": p.get("diagnoses") or [],
            "medications": p.get("medications") or [],
            "allergies": p.get("allergies") or [],
            "lab_results": labs,
            "vital_signs": vitals,
            "cardiac_function": cardiac,
            "medical_history": p.get("medical_history") or [],
            "medical_history_narrative": _generate_medical_history_narrative(p),
            "current_symptoms": p.get("current_symptoms") or [],
            "protocol_facts": p.get("protocol_facts") or {},
            "consent_capacity": p.get("consent_capacity", True),
            "ecog_status": p.get("ecog_status"),
            "pregnancy_test_result": p.get("pregnancy_test_result", "negative"),
            "last_systemic_therapy_date": p.get("last_systemic_therapy_date"),
        }
        normalized.append(patient_record)

    return normalized


# Pre-load normalized synthetic patients
SYNTHETIC_PATIENTS = _load_patients_from_json()


def _tag() -> Dict[str, Any]:
    return {"system": HACKATHON_TAG_SYSTEM, "code": HACKATHON_TAG_CODE}


def _urn() -> str:
    return f"urn:uuid:{uuid.uuid4()}"


def _find_existing_patient_id(client: httpx.Client, internal_id: str) -> Optional[str]:
    """Look up an already-seeded patient by our custom identifier."""
    search_url = f"{FHIR_BASE_URL}/Patient"
    try:
        resp = client.get(
            search_url,
            params={"identifier": f"{HACKATHON_TAG_SYSTEM}|{internal_id}"},
            timeout=15.0,
        )
        if resp.status_code == 200:
            bundle = resp.json()
            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                if resource.get("resourceType") == "Patient":
                    return resource.get("id")
    except Exception:
        pass
    return None


def _extract_patient_id_from_response_bundle(response_bundle: Dict[str, Any]) -> Optional[str]:
    """Extract real patient ID from either successful response or duplicate-resource payload."""
    for entry in response_bundle.get("entry", []):
        response = entry.get("response", {})
        location = response.get("location")
        if location and location.startswith("Patient/"):
            return location.split("/", 2)[1]
        resource = entry.get("resource", {})
        if resource.get("resourceType") == "Patient":
            patient_id = resource.get("id")
            if patient_id:
                return str(patient_id)

    outcome_text = json.dumps(response_bundle)
    match = re.search(r"Patient/([A-Za-z0-9\-\.]+)", outcome_text)
    if match:
        return match.group(1)
    return None


def _build_patient_entry(p: Dict[str, Any], patient_urn: str) -> Dict[str, Any]:
    full_name = p.get("name", "").strip()
    name_parts = full_name.split()

    if len(name_parts) > 1:
        family_name = name_parts[-1]
        given_names = name_parts[:-1]
    elif len(name_parts) == 1:
        family_name = name_parts[0]
        given_names = [name_parts[0]]
    else:
        family_name = "Patient"
        given_names = ["Unknown"]

    human_name: Dict[str, Any] = {
        "use": "official",
        "text": full_name or f"Patient {p.get('internal_id')}",
        "family": family_name,
        "given": given_names,
    }

    resource: Dict[str, Any] = {
        "resourceType": "Patient",
        "meta": {"tag": [_tag()]},
        "name": [human_name],
        "gender": p["sex"],
        "birthDate": p["birth_date"],
        "identifier": [
            {"system": HACKATHON_TAG_SYSTEM, "value": p["internal_id"]},
        ],
    }

    # Cohort and trial extensions using unified tag system
    extensions = []
    if p.get("trial_id"):
        extensions.append({
            "url": f"{HACKATHON_TAG_SYSTEM}/trial_id",
            "valueString": str(p["trial_id"]),
        })
    if p.get("cohort"):
        extensions.append({
            "url": f"{HACKATHON_TAG_SYSTEM}/cohort",
            "valueString": str(p["cohort"]),
        })
    if extensions:
        resource["extension"] = extensions

    return {
        "fullUrl": patient_urn,
        "resource": resource,
        "request": {"method": "POST", "url": "Patient"},
    }


def _build_observation_entry(field_name: str, value: Any, patient_urn: str) -> Dict[str, Any]:
    route_meta = FIELD_ROUTES.get(field_name)
    value_type = route_meta[1] if route_meta else "string"

    resource: Dict[str, Any] = {
        "resourceType": "Observation",
        "meta": {"tag": [_tag()]},
        "status": "final",
        "code": {"coding": [{"system": CODE_SYSTEM, "code": field_name}], "text": field_name},
        "subject": {"reference": patient_urn},
    }

    if value_type == "quantity" and isinstance(value, (int, float)):
        unit = route_meta[2] if (route_meta and len(route_meta) > 2) else ""
        resource["valueQuantity"] = {"value": float(value), "unit": unit}
    elif value_type == "integer" and isinstance(value, (int, float)):
        resource["valueInteger"] = int(value)
    elif value_type == "boolean" and isinstance(value, bool):
        resource["valueBoolean"] = value
    elif value_type == "dateTime":
        resource["valueDateTime"] = str(value)
    elif isinstance(value, (list, tuple)):
        resource["valueString"] = ", ".join(str(x) for x in value)
    elif isinstance(value, dict):
        resource["valueString"] = json.dumps(value)
    else:
        resource["valueString"] = str(value)

    return {"resource": resource, "request": {"method": "POST", "url": "Observation"}}


def build_transaction_bundle(p: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """Builds a complete FHIR transaction Bundle for a single patient."""
    patient_urn = _urn()
    entries = [_build_patient_entry(p, patient_urn)]

    for dx in p.get("diagnoses", []):
        entries.append({
            "resource": {
                "resourceType": "Condition",
                "meta": {"tag": [_tag()]},
                "subject": {"reference": patient_urn},
                "code": {"text": dx},
            },
            "request": {"method": "POST", "url": "Condition"},
        })

    for med in p.get("medications", []):
        entries.append({
            "resource": {
                "resourceType": "MedicationStatement",
                "meta": {"tag": [_tag()]},
                "status": "active",
                "subject": {"reference": patient_urn},
                "medicationCodeableConcept": {"text": med},
            },
            "request": {"method": "POST", "url": "MedicationStatement"},
        })

    for allergy in p.get("allergies", []):
        entries.append({
            "resource": {
                "resourceType": "AllergyIntolerance",
                "meta": {"tag": [_tag()]},
                "patient": {"reference": patient_urn},
                "code": {"text": allergy},
            },
            "request": {"method": "POST", "url": "AllergyIntolerance"},
        })

    # Lab and Vital Observations
    for bucket in ("lab_results", "vital_signs", "cardiac_function"):
        for field_name, value in p.get(bucket, {}).items():
            if value is not None and field_name in FIELD_ROUTES:
                entries.append(_build_observation_entry(field_name, value, patient_urn))

    # Weight Observation
    if p.get("weight") is not None and "weight" in FIELD_ROUTES:
        entries.append(_build_observation_entry("weight", p["weight"], patient_urn))

    # Medical narrative text Observation
    if p.get("medical_history_narrative"):
        entries.append({
            "resource": {
                "resourceType": "Observation",
                "meta": {"tag": [_tag()]},
                "status": "final",
                "code": {"coding": [{"system": CODE_SYSTEM, "code": "medical_history_narrative"}], "text": "medical_history_narrative"},
                "subject": {"reference": patient_urn},
                "valueString": p["medical_history_narrative"],
            },
            "request": {"method": "POST", "url": "Observation"},
        })

    # Structured medical history records as individual clinical observations
    for hist_item in p.get("medical_history", []):
        entries.append({
            "resource": {
                "resourceType": "Observation",
                "meta": {"tag": [_tag()]},
                "status": "final",
                "code": {"coding": [{"system": CODE_SYSTEM, "code": "medical_history"}], "text": "medical_history"},
                "subject": {"reference": patient_urn},
                "valueString": str(hist_item),
            },
            "request": {"method": "POST", "url": "Observation"},
        })

    # Optional root fields
    for field_name in ("ecog_status", "consent_capacity", "pregnancy_test_result", "last_systemic_therapy_date"):
        val = p.get(field_name)
        if val is not None and field_name in FIELD_ROUTES:
            entries.append(_build_observation_entry(field_name, val, patient_urn))

    # Protocol Facts as observations
    for fact_key, fact_val in p.get("protocol_facts", {}).items():
        if fact_val is not None and fact_key in FIELD_ROUTES:
            entries.append(_build_observation_entry(fact_key, fact_val, patient_urn))

    bundle = {"resourceType": "Bundle", "type": "transaction", "entry": entries}
    return bundle, patient_urn


def seed_all(limit: Optional[int] = None, dry_run: bool = False) -> Dict[str, Any]:
    """
    Seeds patients onto the FHIR server.
    Writes the enriched metadata mapping (fhir_id, name, trial_id, cohort)
    to seeded_patient_ids.json so downstream orchestrators & Supabase syncers have full context.
    """
    id_map: Dict[str, Any] = {}
    target_patients = SYNTHETIC_PATIENTS[:limit] if limit else SYNTHETIC_PATIENTS

    print(f"Preparing to seed {len(target_patients)} patients from {_EXPANDED_JSON_PATH.name}...")

    with httpx.Client(timeout=45.0) as client:
        for idx, p in enumerate(target_patients, start=1):
            internal_id = p["internal_id"]

            if dry_run:
                bundle, _ = build_transaction_bundle(p)
                print(f"[{idx}/{len(target_patients)}] Dry run for {internal_id}: {len(bundle['entry'])} entries")
                continue

            existing_id = _find_existing_patient_id(client, internal_id)
            if existing_id:
                id_map[internal_id] = {
                    "fhir_id": str(existing_id),
                    "patient_id": internal_id,
                    "name": p["name"],
                    "trial_id": p.get("trial_id"),
                    "cohort": p.get("cohort"),
                }
                print(f"[{idx}/{len(target_patients)}] {internal_id} already exists -> FHIR Patient/{existing_id}")
                continue

            bundle, _ = build_transaction_bundle(p)
            retries = 3
            real_id = None

            while retries > 0:
                try:
                    resp = client.post(
                        FHIR_BASE_URL,
                        json=bundle,
                        headers={"Content-Type": "application/fhir+json"},
                    )
                    if resp.status_code in (200, 201):
                        response_bundle = resp.json()
                        real_id = _extract_patient_id_from_response_bundle(response_bundle)
                        if real_id:
                            break
                    else:
                        print(f"[{idx}/{len(target_patients)}] HTTP {resp.status_code} from FHIR server: {resp.text[:140]}")
                        retries -= 1
                        time.sleep(1.5)
                except Exception as exc:
                    retries -= 1
                    if retries > 0:
                        time.sleep(2.0)
                    else:
                        print(f"[{idx}/{len(target_patients)}] Connection failure posting {internal_id}: {exc}")

            if real_id:
                id_map[internal_id] = {
                    "fhir_id": str(real_id),
                    "patient_id": internal_id,
                    "name": p["name"],
                    "trial_id": p.get("trial_id"),
                    "cohort": p.get("cohort"),
                }
                print(f"[{idx}/{len(target_patients)}] Seeded {internal_id} -> FHIR Patient/{real_id}")
            else:
                print(f"[{idx}/{len(target_patients)}] Could not resolve ID for {internal_id}")

    if not dry_run:
        _OUTPUT_PATH.write_text(json.dumps(id_map, indent=2), encoding="utf-8")
        print(f"\nSuccessfully seeded {len(id_map)} patients. Saved metadata mappings to {_OUTPUT_PATH}")

    return id_map


if __name__ == "__main__":
    is_dry_run = "--dry-run" in sys.argv
    limit_count = None if "--all" in sys.argv else 30
    seed_all(limit=limit_count, dry_run=is_dry_run)