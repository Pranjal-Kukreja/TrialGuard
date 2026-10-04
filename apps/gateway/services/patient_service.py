"""Patient EHR retrieval and normalization service for the TrialGuard gateway."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_PATIENTS_CACHE: Optional[Dict[str, Dict[str, Any]]] = None

# Known candidate paths for patients_expanded.json in the repository
CANDIDATE_PATHS = [
    Path(__file__).resolve().parents[3] / "packages" / "mcp-ehr" / "src" / "mcp_ehr" / "patients_expanded.json",
    Path(__file__).resolve().parents[3] / "services" / "rag_service" / "data" / "mock_fhir" / "patients_expanded.json",
    Path(__file__).resolve().parents[2] / "packages" / "mcp-ehr" / "src" / "mcp_ehr" / "patients_expanded.json",
    Path("/Users/aahannayak/RESOURCE/techquest/packages/mcp-ehr/src/mcp_ehr/patients_expanded.json"),
]

# Synthetic severe renal impairment patient profile for clinical trial exclusion testing
SEVERE_RENAL_PATIENT = {
    "patient_id": "P033",
    "assigned_demo_trial_id": "NCT02415400",
    "cohort": "Cohort B - Renal Stratification (Severe Impairment)",
    "demo_category": "SYNTHETIC_EHR",
    "name": "Arthur Pendelton",
    "patient": {
        "patient_id": "P033",
        "name": "Arthur Pendelton",
        "cohort": "Cohort B - Renal Stratification (Severe Impairment)",
        "trial_id": "NCT02415400",
        "age": 73,
        "sex": "male",
        "weight": 64.0,
        "diagnoses": [
            "End-stage renal disease / Severe CKD Stage 4",
            "Non-valvular atrial fibrillation",
            "Hypertension",
        ],
        "medications": [
            "Apixaban 2.5mg BID",
            "Furosemide 40mg daily",
            "Amlodipine 5mg daily",
        ],
        "allergies": [],
        "lab_results": {
            "creatinine_clearance": {"value": 22.0, "unit": "mL/min"},
            "serum_creatinine": {"value": 2.9, "unit": "mg/dL"},
            "eGFR": {"value": 21.0, "unit": "mL/min/1.73m2"},
            "ALT": {"value": 24.0, "unit": "U/L"},
            "AST": {"value": 22.0, "unit": "U/L"},
            "platelets": {"value": 185000.0, "unit": "/uL"},
            "hemoglobin": {"value": 10.8, "unit": "g/dL"},
            "INR": {"value": 1.1, "unit": "ratio"},
            "total_bilirubin": {"value": 0.6, "unit": "mg/dL"},
        },
        "vital_signs": {
            "heart_rate": 70.0,
            "blood_pressure_systolic": 138,
            "blood_pressure_diastolic": 84,
        },
        "cardiac_function": {
            "LVEF": 50.0,
            "QTc": 430.0,
        },
        "medical_history": [
            "Chronic kidney disease Stage 4 diagnosed 2021",
            "Arteriovenous fistula evaluation",
        ],
        "medical_history_narrative": "73-year-old male with severe chronic kidney disease Stage 4 and non-valvular atrial fibrillation. Baseline CrCl is 22 mL/min (severe impairment, strictly below trial threshold >= 30 mL/min).",
        "protocol_facts": {
            "prior_bleeding": False,
            "severe_renal_impairment": True,
            "oral_anticoagulation_required": True,
        },
    },
}


def _load_cache() -> Dict[str, Dict[str, Any]]:
    global _PATIENTS_CACHE
    if _PATIENTS_CACHE is not None:
        return _PATIENTS_CACHE

    cache: Dict[str, Dict[str, Any]] = {}

    for path in CANDIDATE_PATHS:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                patients_list = data.get("patients", [])
                for item in patients_list:
                    pid = item.get("patient_id")
                    if pid:
                        cache[pid.strip().upper()] = item
                logger.info("Loaded %d patients from %s", len(cache), path)
                break
            except Exception as exc:
                logger.warning("Failed loading patient JSON from %s: %s", path, exc)

    # Inject severe renal patient for exclusion validation
    cache["P033"] = SEVERE_RENAL_PATIENT

    _PATIENTS_CACHE = cache
    return _PATIENTS_CACHE


def get_all_patients() -> List[Dict[str, Any]]:
    """Returns a list of all normalized patient profiles."""
    cache = _load_cache()
    return list(cache.values())


def get_patient_profile(patient_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a normalized patient record by patient ID (case-insensitive)."""
    if not patient_id:
        return None

    cache = _load_cache()
    clean_id = patient_id.strip().upper()

    # Direct match
    if clean_id in cache:
        return cache[clean_id]

    # Partial match (e.g. "P001" matching "PT-P001" or numeric)
    for k, v in cache.items():
        if clean_id in k or k in clean_id:
            return v

    return None


def extract_patient_clinical_package(patient_id: str, fallback_patient: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Builds a standardized rule_analysis_package.patient structure for LangGraph agents."""
    raw = get_patient_profile(patient_id)
    if not raw and fallback_patient:
        raw = fallback_patient

    if not raw:
        return {
            "patient_id": patient_id,
            "name": f"Patient {patient_id}",
            "trial_id": "NCT02415400",
            "cohort": "Cohort A - Standard Protocol",
            "age": 65,
            "sex": "male",
            "diagnoses": ["Non-valvular atrial fibrillation"],
            "medications": ["Apixaban 5mg BID", "Clopidogrel 75mg daily"],
            "medical_history": {"prior_bleeding": False},
            "lab_results": {
                "creatinine_clearance": {"value": 65.0, "unit": "mL/min", "reference_range": {"min": 30}},
                "serum_creatinine": {"value": 1.0, "unit": "mg/dL"},
            },
            "protocol_facts": {},
        }

    p = raw.get("patient", raw)
    lab_results = p.get("lab_results", {})

    # Ensure creatinine clearance has standardized dictionary structure
    crcl = lab_results.get("creatinine_clearance")
    if isinstance(crcl, (int, float)):
        lab_results["creatinine_clearance"] = {"value": float(crcl), "unit": "mL/min", "reference_range": {"min": 30}}
    elif isinstance(crcl, dict):
        val = crcl.get("value", 65.0)
        lab_results["creatinine_clearance"] = {
            "value": float(val) if val is not None else 65.0,
            "unit": crcl.get("unit", "mL/min"),
            "reference_range": crcl.get("reference_range", {"min": 30}),
        }
    elif "creatinine_clearance" not in lab_results:
        lab_results["creatinine_clearance"] = {"value": 65.0, "unit": "mL/min", "reference_range": {"min": 30}}

    # Standardize serum creatinine
    scr = lab_results.get("serum_creatinine")
    if isinstance(scr, (int, float)):
        lab_results["serum_creatinine"] = {"value": float(scr), "unit": "mg/dL"}
    elif isinstance(scr, dict):
        val = scr.get("value", 1.0)
        lab_results["serum_creatinine"] = {"value": float(val) if val is not None else 1.0, "unit": scr.get("unit", "mg/dL")}

    trial_id = raw.get("assigned_demo_trial_id") or raw.get("trial_id") or p.get("trial_id") or "NCT02415400"
    cohort = raw.get("cohort") or p.get("cohort") or "Cohort A - Standard Protocol"

    return {
        "patient_id": patient_id,
        "name": raw.get("name") or p.get("name") or f"Patient {patient_id}",
        "trial_id": trial_id,
        "cohort": cohort,
        "age": p.get("age") if "age" in p else 65,
        "sex": p.get("sex") if "sex" in p else "male",
        "weight": p.get("weight", 70.0),
        "diagnoses": p.get("diagnoses", []),
        "medications": p.get("medications", []),
        "allergies": p.get("allergies", []),
        "medical_history": p.get("medical_history", []),
        "medical_history_narrative": p.get("medical_history_narrative", ""),
        "lab_results": lab_results,
        "vital_signs": p.get("vital_signs", {}),
        "cardiac_function": p.get("cardiac_function", {}),
        "protocol_facts": p.get("protocol_facts", {}),
    }
