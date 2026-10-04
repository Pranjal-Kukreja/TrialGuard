"""
Live FHIR client. get_patient(patient_identifier) performs a real HTTP GET against
the public HAPI FHIR R4 server using Patient/$everything. Supports both:
1. Native FHIR Resource IDs directly from the UI (e.g. '138505842')
2. Internal synthetic aliases (e.g. 'P001', 'PT-4471-0293') via seeded_patient_ids.json

Updated to synchronize with the expanded PatientData contract:
- Full extraction of trial_id, cohort, dob, last_systemic_therapy_date, and protocol_facts
- Standardizes gender/sex, flat vs nested observation metrics, and narrative generation
- Standalone signature support for find_nearest_patients tool invocations
"""

import json
import re
import sys
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx

_pkg_dir = str(Path(__file__).parent)
if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)

try:
    from fhir_codes import CODE_SYSTEM, FIELD_ROUTES
except ImportError:
    CODE_SYSTEM = "https://techquest-hackathon.local/lab-codes"
    FIELD_ROUTES = {
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
        # Root attributes
        "weight": (None, "weight"),
        "ecog_status": (None, "ecog_status"),
        "consent_capacity": (None, "consent_capacity"),
        "pregnancy_test_result": (None, "pregnancy_test_result"),
        "last_systemic_therapy_date": (None, "last_systemic_therapy_date"),
        "dob": (None, "dob"),
    }

LOINC_FIELD_MAP = {
    "2160-0": "serum_creatinine",
    "38483-4": "creatinine_clearance",
    "33914-3": "eGFR",
    "48642-3": "eGFR",
    "48643-1": "eGFR",
    "1751-7": "ALT",
    "1920-8": "AST",
    "777-3": "platelets",
    "26515-7": "platelets",
    "718-7": "hemoglobin",
    "6301-6": "INR",
    "1975-2": "total_bilirubin",
    "26499-4": "ANC",
    "751-8": "ANC",
    "8867-4": "heart_rate",
    "8480-6": "blood_pressure_systolic",
    "8462-4": "blood_pressure_diastolic",
    "10230-1": "LVEF",
    "8806-2": "LVEF",
    "18485-3": "QTc",
    "48672-0": "QTc",
}

FHIR_BASE_URL = "https://hapi.fhir.org/baseR4"
_ID_MAP_PATH = Path(__file__).parent / "seeded_patient_ids.json"
_EXPANDED_JSON_PATH = Path(__file__).parent / "patients_expanded.json"


def _load_id_maps() -> Tuple[Dict[str, str], Dict[str, str], Dict[str, Dict[str, Any]]]:
    if not _ID_MAP_PATH.exists():
        return {}, {}, {}
    try:
        raw = json.loads(_ID_MAP_PATH.read_text(encoding="utf-8"))
        int_to_fhir: Dict[str, str] = {}
        fhir_to_int: Dict[str, str] = {}
        int_to_meta: Dict[str, Dict[str, Any]] = {}

        for k, v in raw.items():
            if isinstance(v, dict):
                fid = str(v.get("fhir_id", ""))
                meta = {
                    "name": str(v.get("name", f"Patient {k}")),
                    "trial_id": v.get("trial_id"),
                    "cohort": v.get("cohort"),
                }
            else:
                fid = str(v)
                meta = {
                    "name": f"Patient {k}",
                    "trial_id": None,
                    "cohort": None,
                }

            if fid:
                int_to_fhir[k] = fid
                fhir_to_int[fid] = k
            int_to_meta[k] = meta

        return int_to_fhir, fhir_to_int, int_to_meta
    except Exception:
        return {}, {}, {}


def _compute_age(birth_date_str: str) -> int:
    try:
        birth = date.fromisoformat(birth_date_str.split("T")[0])
        today = date.today()
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    except Exception:
        return 50


def _normalize_sex(raw_gender: Any, compact: bool = False) -> str:
    s = str(raw_gender or "").strip().lower()
    if s in ["f", "female"]:
        return "F" if compact else "female"
    if s in ["m", "male"]:
        return "M" if compact else "male"
    return "unknown"


def _extract_observation_value(resource: Dict[str, Any]) -> Any:
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


def _observation_field_name(resource: Dict[str, Any]) -> Optional[str]:
    # 1. Custom coding system priority
    for coding in resource.get("code", {}).get("coding", []):
        if coding.get("system") == CODE_SYSTEM:
            code = coding.get("code")
            if code in FIELD_ROUTES:
                return code

    # 2. Standard LOINC codes
    for coding in resource.get("code", {}).get("coding", []):
        loinc = coding.get("code")
        if loinc in LOINC_FIELD_MAP:
            return LOINC_FIELD_MAP[loinc]

    # 3. Direct field route on code text
    code_text = resource.get("code", {}).get("text")
    if code_text:
        if code_text in FIELD_ROUTES:
            return code_text
        if code_text in LOINC_FIELD_MAP:
            return LOINC_FIELD_MAP[code_text]

    return None


def _is_resolved_or_history(resource: Dict[str, Any], text: str) -> bool:
    status = ""
    for coding in resource.get("clinicalStatus", {}).get("coding", []):
        status = coding.get("code", "").lower()

    category = ""
    for cat in resource.get("category", []):
        for coding in cat.get("coding", []):
            category = coding.get("code", "").lower()

    if status in ("resolved", "inactive", "remission") or category in ("history", "past"):
        return True

    lower_text = text.lower()
    if any(kw in lower_text for kw in ("prior", "remote", "history of", "resolved", "previous", "status post")):
        return True
    if bool(re.search(r"\(19\d\d|\(20\d\d", text)):
        return True

    return False


def _parse_everything_bundle(bundle: Dict[str, Any], canonical_id: str) -> Dict[str, Any]:
    patient: Dict[str, Any] = {
        "patient_id": canonical_id,
        "internal_id": canonical_id,
        "fhir_id": canonical_id,
        "trial_id": None,
        "cohort": None,
        "name": None,
        "dob": None,
        "age": 50,
        "sex": "unknown",
        "weight": None,
        "diagnoses": [],
        "medications": [],
        "allergies": [],
        "lab_results": {},
        "vital_signs": {},
        "cardiac_function": {},
        "protocol_facts": {},
        "medical_history": [],
        "medical_history_narrative": None,
        "current_symptoms": [],
        "consent_capacity": True,
        "ecog_status": None,
        "pregnancy_test_result": "negative",
        "last_systemic_therapy_date": None,
    }

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        rtype = resource.get("resourceType")

        if rtype == "Patient":
            bdate = resource.get("birthDate")
            if bdate:
                patient["dob"] = bdate
                patient["birth_date"] = bdate
                patient["age"] = _compute_age(bdate)
            patient["sex"] = _normalize_sex(resource.get("gender"))

            names = resource.get("name", [])
            if names:
                name_entry = names[0]
                patient["name"] = name_entry.get("text") or f"{' '.join(name_entry.get('given', []))} {name_entry.get('family', '')}".strip()

            raw_div = resource.get("text", {}).get("div", "")
            if raw_div:
                clean_narrative = re.sub(r"<[^>]+>", "", raw_div).strip()
                if clean_narrative:
                    patient["medical_history_narrative"] = clean_narrative

            for ext in resource.get("extension", []):
                url = ext.get("url", "")
                if "trial_id" in url:
                    patient["trial_id"] = ext.get("valueString")
                elif "cohort" in url:
                    patient["cohort"] = ext.get("valueString")

            for ident in resource.get("identifier", []):
                if ident.get("system") == "https://techquest-hackathon.local/tags":
                    patient["internal_id"] = ident.get("value")

        elif rtype == "Condition":
            text = resource.get("code", {}).get("text")
            if text:
                if _is_resolved_or_history(resource, text):
                    if text not in patient["medical_history"]:
                        patient["medical_history"].append(text)
                else:
                    if text not in patient["diagnoses"]:
                        patient["diagnoses"].append(text)

        elif rtype == "MedicationStatement":
            text = resource.get("medicationCodeableConcept", {}).get("text")
            if text and text not in patient["medications"]:
                patient["medications"].append(text)

        elif rtype == "AllergyIntolerance":
            text = resource.get("code", {}).get("text")
            if text and text not in patient["allergies"]:
                patient["allergies"].append(text)

        elif rtype == "Observation":
            field_name = _observation_field_name(resource)
            if field_name is None or field_name not in FIELD_ROUTES:
                code_text = resource.get("code", {}).get("text")
                if code_text and "valueQuantity" in resource:
                    vq = resource["valueQuantity"]
                    val = vq.get("value")
                    if val is not None:
                        try:
                            patient["lab_results"][code_text] = float(val)
                        except (ValueError, TypeError):
                            patient["lab_results"][code_text] = val
                continue

            route = FIELD_ROUTES[field_name]
            bucket = route[0]
            value = _extract_observation_value(resource)

            if field_name == "drug_contraindication" and isinstance(value, str):
                try:
                    value = json.loads(value)
                except Exception:
                    value = [x.strip() for x in value.split(",") if x.strip()] if value else []

            if field_name == "medical_history" and value:
                if str(value) not in patient["medical_history"]:
                    patient["medical_history"].append(str(value))
                continue

            # Cast labs / vitals / cardiac to float where appropriate
            if bucket in ("lab_results", "vital_signs", "cardiac_function") and value is not None:
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    pass

            if bucket is None:
                patient[field_name] = value
                if field_name == "dob" and value:
                    patient["birth_date"] = value
                    patient["age"] = _compute_age(str(value))
            else:
                if bucket not in patient:
                    patient[bucket] = {}
                patient[bucket][field_name] = value

    return patient


def _enrich_from_expanded_json(patient_data: Dict[str, Any], lookup_keys: List[str]) -> Dict[str, Any]:
    if not _EXPANDED_JSON_PATH.exists():
        return patient_data

    try:
        expanded = json.loads(_EXPANDED_JSON_PATH.read_text(encoding="utf-8"))
        match = None
        match_entry = None

        for item in expanded.get("patients", []):
            p = item.get("patient", item)
            pid = str(item.get("patient_id") or p.get("patient_id", ""))
            iid = str(p.get("internal_id") or pid)
            fid = str(item.get("fhir_id") or p.get("fhir_id", ""))
            if any(str(k) in (pid, iid, fid) for k in lookup_keys if k):
                match = p
                match_entry = item
                break

        if match:
            if not patient_data.get("trial_id"):
                patient_data["trial_id"] = (
                    match_entry.get("assigned_demo_trial_id") 
                    or match_entry.get("trial_id") 
                    or match.get("trial_id")
                )
            if not patient_data.get("cohort"):
                patient_data["cohort"] = match_entry.get("cohort") or match.get("cohort")
            if not patient_data.get("dob"):
                patient_data["dob"] = match.get("dob") or match.get("birth_date")

            if not patient_data.get("medical_history") and match.get("medical_history"):
                patient_data["medical_history"] = match.get("medical_history", [])

            if not patient_data.get("medical_history_narrative") and match.get("medical_history_narrative"):
                patient_data["medical_history_narrative"] = match.get("medical_history_narrative")

            if not patient_data.get("protocol_facts") and match.get("protocol_facts"):
                patient_data["protocol_facts"] = match.get("protocol_facts", {})

            for section in ("lab_results", "vital_signs", "cardiac_function"):
                sec_dict = match.get(section, {})
                if sec_dict:
                    if section not in patient_data or not patient_data[section]:
                        patient_data[section] = {}
                    for k, v in sec_dict.items():
                        if k not in patient_data[section]:
                            patient_data[section][k] = v.get("value") if isinstance(v, dict) else v

            for opt_key in ("weight", "ecog_status", "consent_capacity", "pregnancy_test_result", "last_systemic_therapy_date"):
                if patient_data.get(opt_key) is None and match.get(opt_key) is not None:
                    patient_data[opt_key] = match.get(opt_key)
    except Exception:
        pass

    return patient_data


def list_patients_for_ui(query: Optional[str] = None) -> List[Dict[str, Any]]:
    int_to_fhir, _, int_to_meta = _load_id_maps()
    patients_pool = []

    if _EXPANDED_JSON_PATH.exists():
        try:
            data = json.loads(_EXPANDED_JSON_PATH.read_text(encoding="utf-8"))
            for entry in data.get("patients", []):
                p = entry.get("patient", entry)
                p_copy = dict(p)
                p_copy["trial_id"] = entry.get("assigned_demo_trial_id") or entry.get("trial_id") or p.get("trial_id")
                p_copy["cohort"] = entry.get("cohort") or p.get("cohort")
                patients_pool.append(p_copy)
        except Exception:
            patients_pool = []

    if not patients_pool:
        try:
            from mcp_ehr.seed_data import SYNTHETIC_PATIENTS
            patients_pool = SYNTHETIC_PATIENTS
        except ImportError:
            try:
                from seed_data import SYNTHETIC_PATIENTS
                patients_pool = SYNTHETIC_PATIENTS
            except ImportError:
                pass

    results = []
    for p in patients_pool:
        internal_id = str(p.get("internal_id") or p.get("patient_id"))
        fhir_id = int_to_fhir.get(internal_id, internal_id)
        
        meta = int_to_meta.get(internal_id, {})
        name = meta.get("name") or p.get("name") or f"Patient {internal_id}"
        trial_id = p.get("trial_id") or meta.get("trial_id")
        cohort = p.get("cohort") or meta.get("cohort") or "Standard Cohort"

        diagnoses = p.get("diagnoses", [])
        primary_diag = diagnoses[0] if diagnoses else "Stable"
        sex_display = _normalize_sex(p.get("sex"), compact=True)
        label = f"{name} ({internal_id} / #{fhir_id}) — {p.get('age')}y {sex_display} [{primary_diag}] — {cohort}"

        results.append({
            "patient_id": str(internal_id),
            "internal_id": str(internal_id),
            "fhir_id": str(fhir_id),
            "name": name,
            "dob": p.get("dob") or p.get("birth_date"),
            "trial_id": trial_id,
            "cohort": cohort,
            "age": p.get("age"),
            "sex": _normalize_sex(p.get("sex"), compact=False),
            "diagnoses": diagnoses,
            "display_label": label,
        })

    if query:
        return find_nearest_patients(query, results)

    return results


def find_nearest_patients(
    query: str,
    patients: Optional[List[Dict[str, Any]]] = None,
    limit: int = 10,
    top_k: Optional[int] = None,
    threshold: float = 0.50,
) -> List[Dict[str, Any]]:
    max_results = top_k or limit
    pool = patients if patients is not None else list_patients_for_ui()

    if not query or not str(query).strip():
        return pool[:max_results]

    q = str(query).strip().lower()

    exact_id_matches = [
        p for p in pool
        if q == str(p.get("internal_id", "")).lower()
        or q == str(p.get("patient_id", "")).lower()
        or q == str(p.get("fhir_id", "")).lower()
    ]
    if exact_id_matches:
        return exact_id_matches

    substring_matches = [
        p for p in pool
        if q in str(p.get("name", "")).lower()
        or q in str(p.get("trial_id", "")).lower()
        or q in str(p.get("cohort", "")).lower()
        or any(q in str(d).lower() for d in p.get("diagnoses", []))
    ]
    if substring_matches:
        return substring_matches[:max_results]

    scored = []
    q_tokens = q.split()

    for p in pool:
        name = str(p.get("name", "")).lower()
        score_name = SequenceMatcher(None, q, name).ratio()

        name_tokens = name.split()
        token_scores = [
            max((SequenceMatcher(None, qt, nt).ratio() for nt in name_tokens), default=0.0)
            for qt in q_tokens
        ] if name_tokens else [0.0]
        token_score = sum(token_scores) / len(token_scores) if token_scores else 0.0

        score = max(score_name, token_score)
        if score >= threshold:
            scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:max_results]]


def get_patient(patient_identifier: str) -> Dict[str, Any]:
    clean_id = str(patient_identifier).strip()
    int_to_fhir, fhir_to_int, int_to_meta = _load_id_maps()

    if clean_id in int_to_fhir:
        internal_id = clean_id
        fhir_id = int_to_fhir[clean_id]
    elif clean_id in fhir_to_int:
        fhir_id = clean_id
        internal_id = fhir_to_int[clean_id]
    else:
        internal_id = clean_id
        fhir_id = clean_id

    meta = int_to_meta.get(internal_id, {})
    assigned_name = meta.get("name")

    # 1. Local patients_expanded.json priority
    if _EXPANDED_JSON_PATH.exists():
        try:
            expanded_data = json.loads(_EXPANDED_JSON_PATH.read_text(encoding="utf-8"))
            for entry in expanded_data.get("patients", []):
                p = entry.get("patient", entry)
                candidates = {
                    str(entry.get("patient_id", "")),
                    str(entry.get("fhir_id", "")),
                    str(p.get("internal_id", "")),
                    str(p.get("patient_id", "")),
                    str(p.get("fhir_id", "")),
                }
                candidates.discard("")
                if any(cand in (internal_id, fhir_id, clean_id) for cand in candidates):
                    result = dict(p)
                    result["patient_id"] = internal_id
                    result["internal_id"] = internal_id
                    result["fhir_id"] = fhir_id
                    result["name"] = assigned_name or p.get("name") or f"Patient {internal_id}"
                    result["trial_id"] = (
                        entry.get("assigned_demo_trial_id") 
                        or entry.get("trial_id") 
                        or p.get("trial_id") 
                        or meta.get("trial_id")
                    )
                    result["cohort"] = entry.get("cohort") or p.get("cohort") or meta.get("cohort")
                    result["dob"] = p.get("dob") or p.get("birth_date")
                    result["sex"] = _normalize_sex(result.get("sex"), compact=False)

                    # Flatten nested {'value': x} dictionaries
                    for bucket in ("lab_results", "vital_signs", "cardiac_function"):
                        if bucket in result and isinstance(result[bucket], dict):
                            result[bucket] = {
                                k: (v.get("value") if isinstance(v, dict) else v)
                                for k, v in result[bucket].items()
                            }

                    return result
        except Exception as exc:
            print(f"[FHIR Notice] Failed reading patients_expanded.json: {exc}")

    # 2. Search by internal identifier tag on FHIR server if needed
    if not fhir_id and internal_id:
        try:
            search_url = f"{FHIR_BASE_URL}/Patient"
            resp = httpx.get(
                search_url,
                params={"identifier": f"https://techquest-hackathon.local/tags|{internal_id}"},
                timeout=8.0,
            )
            if resp.status_code == 200:
                bundle = resp.json()
                for entry in bundle.get("entry", []):
                    res = entry.get("resource", {})
                    if res.get("resourceType") == "Patient" and res.get("id"):
                        fhir_id = str(res.get("id"))
                        break
        except Exception:
            pass

    target_fhir_id = fhir_id or clean_id

    # 3. Live HAPI FHIR query fallback
    patient_data = None
    try:
        url = f"{FHIR_BASE_URL}/Patient/{target_fhir_id}/$everything"
        resp = httpx.get(url, params={"_format": "json"}, timeout=15.0)
        if resp.status_code == 200:
            bundle = resp.json()
            patient_data = _parse_everything_bundle(bundle, canonical_id=str(target_fhir_id))
            patient_data["patient_id"] = internal_id
            patient_data["internal_id"] = internal_id
            patient_data["fhir_id"] = str(target_fhir_id)
            if assigned_name:
                patient_data["name"] = assigned_name
            if meta.get("trial_id"):
                patient_data["trial_id"] = meta["trial_id"]
            if meta.get("cohort"):
                patient_data["cohort"] = meta["cohort"]
    except Exception as exc:
        print(f"[FHIR Notice] Live FHIR query for {target_fhir_id} failed: {exc}")

    if patient_data:
        patient_data = _enrich_from_expanded_json(patient_data, [internal_id, str(target_fhir_id), clean_id])
        if patient_data.get("medical_history"):
            hist_set = set(patient_data["medical_history"])
            patient_data["diagnoses"] = [d for d in patient_data.get("diagnoses", []) if d not in hist_set]
        if not patient_data.get("name"):
            patient_data["name"] = assigned_name or f"Patient {internal_id}"
        patient_data["sex"] = _normalize_sex(patient_data.get("sex"), compact=False)
        return patient_data

    raise ValueError(f"Patient with identifier '{patient_identifier}' could not be found.")