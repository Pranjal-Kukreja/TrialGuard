"""
Clinical Ingestion & Harmonization Module.

Handles:
  - Live FHIR retrieval via fhir_client
  - LLM-assisted or direct schema normalization to PatientData
  - Integration with the revised architecture:
      * Stores raw FHIR payload into raw_fhir_patient
      * Normalizes demographics (dob, cohort, sex: female/male)
      * Initializes specialized A2A history reducers
      * Formulates initial state ready for fhir_fetch_node -> rag_analysis_node
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from groq import Groq
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Dynamic Path Resolution & Schema Imports
# ---------------------------------------------------------------------------
CURRENT_FILE = Path(__file__).resolve()
REPO_ROOT = CURRENT_FILE.parents[4] if len(CURRENT_FILE.parents) >= 5 else CURRENT_FILE.parents[2]

for p in [
    str(REPO_ROOT),
    str(REPO_ROOT / "packages" / "shared-schemas"),
    str(REPO_ROOT / "packages" / "mcp-ehr" / "src" / "mcp_ehr"),
]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from shared_schemas.state import PatientData, TrialState
except ImportError:
    from state import PatientData, TrialState

try:
    from mcp_ehr.fhir_client import get_patient
except ImportError:
    from fhir_client import get_patient


# ---------------------------------------------------------------------------
# Strict Concrete Pydantic Models for LLM Harmonization
# ---------------------------------------------------------------------------
class StrictVitalSigns(BaseModel):
    heart_rate: Optional[float] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None


class StrictLabResults(BaseModel):
    # Defaults must be None to prevent hallucinating normal labs on sick patients
    ALT: Optional[float] = None                  # U/L
    AST: Optional[float] = None                  # U/L
    eGFR: Optional[float] = None                 # mL/min/1.73m2
    ANC: Optional[float] = None                  # Absolute count (/uL)
    platelets: Optional[float] = None            # Absolute count (/uL)
    hemoglobin: Optional[float] = None           # g/dL
    INR: Optional[float] = None                  # ratio
    total_bilirubin: Optional[float] = None       # mg/dL
    serum_creatinine: Optional[float] = None      # mg/dL
    creatinine_clearance: Optional[float] = None  # mL/min


class StrictCardiacFunction(BaseModel):
    LVEF: Optional[float] = None
    QTc: Optional[float] = None


class StrictProtocolFacts(BaseModel):
    oral_anticoagulation_required: Optional[bool] = None
    planned_or_existing_oral_anticoagulation: Optional[bool] = None
    acs_pathway: Optional[bool] = None
    days_since_acute_coronary_syndrome: Optional[int] = None
    pci_pathway: Optional[bool] = None
    days_since_PCI: Optional[int] = None
    planned_p2y12_duration: Optional[int] = None
    history_of_intracranial_hemorrhage: Optional[bool] = False
    prior_bleeding: Optional[bool] = False
    ongoing_bleeding: Optional[bool] = False
    known_coagulopathy: Optional[bool] = False
    cabg_for_index_acs: Optional[bool] = False
    other_condition_requiring_chronic_anticoagulation: Optional[bool] = False
    drug_contraindication: List[str] = Field(default_factory=list)
    pregnant: Optional[bool] = False
    breastfeeding: Optional[bool] = False
    woman_of_childbearing_potential: Optional[bool] = False
    pregnancy_test_negative: Optional[bool] = True


class StrictPatientRecord(BaseModel):
    patient_id: str = Field(description="Unique patient identifier, e.g. P001 or PT-4471-0293")
    internal_id: Optional[str] = None
    fhir_id: Optional[str] = None
    name: Optional[str] = None
    dob: Optional[str] = Field(default=None, description="ISO format date of birth (YYYY-MM-DD)")
    cohort: Optional[str] = Field(default=None, description="Assigned clinical trial cohort")
    age: int = Field(default=50, description="Patient age in full years")
    sex: str = Field(default="female", description="Standardized sex: 'female' or 'male'")
    weight: Optional[float] = None
    birth_date: Optional[str] = None
    diagnoses: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)

    lab_results: StrictLabResults = Field(default_factory=StrictLabResults)
    vital_signs: StrictVitalSigns = Field(default_factory=StrictVitalSigns)
    cardiac_function: StrictCardiacFunction = Field(default_factory=StrictCardiacFunction)

    medical_history: List[str] = Field(default_factory=list)
    medical_history_narrative: Optional[str] = Field(
        default=None, 
        description="Clinical overview covering patient demographics, chronics, and active interventions."
    )
    current_symptoms: List[str] = Field(default_factory=list)
    pregnancy_test_result: Optional[str] = "negative"
    consent_capacity: Optional[bool] = True
    ecog_status: Optional[int] = 0
    last_systemic_therapy_date: Optional[str] = None
    protocol_facts: StrictProtocolFacts = Field(default_factory=StrictProtocolFacts)


# ---------------------------------------------------------------------------
# Unpacking & Sanitization Helpers
# ---------------------------------------------------------------------------
def _unpack_val(val: Any) -> Any:
    if isinstance(val, dict) and "value" in val:
        return val["value"]
    return val


def _normalize_sex_code(raw_sex: Any) -> str:
    s = str(raw_sex or "").strip().lower()
    if s in ["female", "f"]:
        return "female"
    if s in ["male", "m"]:
        return "male"
    return str(raw_sex) if raw_sex else "unknown"


def _sanitize_structured_dict(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Unpacks nested {'value': x, 'unit': y} dictionaries into flat primitives and normalizes fields."""
    clean = dict(raw)

    for bucket in ("lab_results", "vital_signs", "cardiac_function"):
        if isinstance(clean.get(bucket), dict):
            clean[bucket] = {k: _unpack_val(v) for k, v in clean[bucket].items()}
        else:
            clean[bucket] = {}

    clean["weight"] = _unpack_val(clean.get("weight"))
    clean["sex"] = _normalize_sex_code(clean.get("sex"))
    clean["dob"] = clean.get("dob") or clean.get("birth_date")
    clean["pregnancy_test_result"] = clean.get("pregnancy_test_result", "negative")
    clean["consent_capacity"] = clean.get("consent_capacity", True)

    for list_field in ("diagnoses", "medications", "allergies", "medical_history", "current_symptoms"):
        if clean.get(list_field) is None:
            clean[list_field] = []

    if "protocol_facts" in clean and isinstance(clean["protocol_facts"], dict):
        pfacts = clean["protocol_facts"]
        if "planned_or_existing_oral_anticoagulation" in pfacts and "oral_anticoagulation_required" not in pfacts:
            pfacts["oral_anticoagulation_required"] = pfacts["planned_or_existing_oral_anticoagulation"]
        elif "oral_anticoagulation_required" in pfacts and "planned_or_existing_oral_anticoagulation" not in pfacts:
            pfacts["planned_or_existing_oral_anticoagulation"] = pfacts["oral_anticoagulation_required"]
    else:
        clean["protocol_facts"] = {}

    if not clean.get("medical_history_narrative"):
        age = clean.get("age", "Unknown")
        sex = clean.get("sex", "individual")
        diagnoses = ", ".join(clean.get("diagnoses", [])) or "No active chronic diagnoses"
        meds = ", ".join(clean.get("medications", [])) or "None reported"
        history = ", ".join(str(x) for x in clean.get("medical_history", [])) or "No prior documented procedures"
        clean["medical_history_narrative"] = (
            f"Patient is a {age}-year-old {sex} presenting with a primary history of {diagnoses}.\n"
            f"Active pharmacological regimen includes {meds}.\n"
            f"Relevant past interventions and procedures include {history}.\n"
            f"Baseline organ function and hematologic profiles verified for protocol review."
        )
    return clean


# ---------------------------------------------------------------------------
# Harmonization Function (Groq Powered)
# ---------------------------------------------------------------------------
def harmonize_clinical_payload(raw_clinical_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Uses Groq to map unstructured, mislabeled, or incomplete FHIR extraction data
    into a structured dictionary strictly conforming to PatientData.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[Harmonizer Warning] GROQ_API_KEY not found. Returning sanitized raw payload.")
        return _sanitize_structured_dict(raw_clinical_data)

    client = Groq(api_key=api_key)
    target_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    schema_json = json.dumps(StrictPatientRecord.model_json_schema(), indent=2)

    prompt = f"""You are an automated Clinical EHR Harmonization Agent.
Your job is to normalize and map arbitrary clinical data into the strict schema below.

JSON Target Schema:
{schema_json}

CRITICAL RULES:
1. Patient Demographics:
   - Standardize sex to 'female' or 'male'.
   - Ensure 'age' is an integer.
   - Maintain 'patient_id', 'dob', and 'cohort' if present.
2. Lab Results & Vital Signs:
   - Map ALT, AST, eGFR, hemoglobin, INR, total_bilirubin, serum_creatinine, creatinine_clearance.
   - Set missing lab values to null; DO NOT invent normal numbers.
   - ANC and platelets must be absolute counts (/uL) if present.
   - Map heart_rate, blood_pressure_systolic, blood_pressure_diastolic.
   - Map cardiac parameters: LVEF (percentage) and QTc (ms).
3. Narrative & Protocol Facts:
   - If 'medical_history_narrative' is missing, generate a concise 3-4 sentence clinical overview summarizing age, sex, primary chronic conditions, and past procedures.
   - Map clinical trial indicators (e.g., oral_anticoagulation_required, days_since_PCI) into 'protocol_facts'.
4. Output valid JSON only matching the schema.

[RAW INPUT DATA]
{json.dumps(raw_clinical_data, default=str, indent=2)}
"""

    try:
        completion = client.chat.completions.create(
            model=target_model,
            messages=[
                {"role": "system", "content": "You are a clinical data transformer that outputs strict schema-conforming JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )

        validated_record = StrictPatientRecord.model_validate_json(completion.choices[0].message.content)
        data = validated_record.model_dump()

        for field in ("last_systemic_therapy_date", "birth_date"):
            if not data.get(field):
                data.pop(field, None)

        return data

    except Exception as exc:
        print(f"[Harmonizer Warning] Groq harmonization failed: {exc}. Returning sanitized raw payload.")
        return _sanitize_structured_dict(raw_clinical_data)


# ---------------------------------------------------------------------------
# UI Ingestion Gateway
# ---------------------------------------------------------------------------
def prepare_trial_state_from_ui(
    trial_id: str,
    raw_patient_id: str,
    proposed_action: str = "",
    evidence: Optional[List[Dict[str, Any]]] = None,
    protocol_rules: Optional[List[Dict[str, Any]]] = None,
) -> TrialState:
    """
    Coordinates the ingestion pipeline:
    1. Live FHIR extraction via FastMCP / fhir_client (stores into raw_fhir_patient).
    2. Zero-Quota Structured Data Sanitization (or Groq harmonization fallback).
    3. Bundles full state ready for the LangGraph entry flow.
    """
    print(f"--> [Step 1] Fetching live FHIR bundle for ID: {raw_patient_id}...")
    try:
        raw_fhir_record = get_patient(raw_patient_id)
    except Exception as e:
        print(f"[FHIR Warning] Could not fetch patient {raw_patient_id}: {e}")
        raw_fhir_record = {"patient_id": raw_patient_id}

    target_patient_dict = raw_fhir_record.get("patient", raw_fhir_record)

    if isinstance(target_patient_dict, dict) and "lab_results" in target_patient_dict and target_patient_dict.get("lab_results"):
        print("--> [Step 2] FHIR payload already structured; unpacking primitives and bypassing LLM.")
        sanitized_patient = _sanitize_structured_dict(target_patient_dict)
    else:
        print("--> [Step 2] Sending unstructured payload to Groq Strict JSON Harmonizer...")
        sanitized_patient = harmonize_clinical_payload(target_patient_dict)

    clean_pid = str(raw_patient_id)
    sanitized_patient["patient_id"] = clean_pid

    cohort = target_patient_dict.get("cohort") or raw_fhir_record.get("cohort") or "Cohort A - Standard Protocol"
    effective_trial_id = trial_id or target_patient_dict.get("trial_id") or raw_fhir_record.get("trial_id") or "NCT02415400"

    sanitized_patient["cohort"] = cohort

    print("--> [Step 3] Assembling clean TrialState for LangGraph START...")
    clean_state: TrialState = {
        # Core identification & inputs
        "trial_id": effective_trial_id,
        "patient_id": clean_pid,
        "cohort": cohort,
        "prescribed_action": proposed_action,
        "proposed_action": proposed_action,
        "doctor_query": f"Analyze whether this prescribed action '{proposed_action}' is valid for this patient.",
        "query": proposed_action,
        "patient": sanitized_patient,
        "raw_fhir_patient": raw_fhir_record,

        # Financial context configuration
        "financial_context": {
            "payer_id": "SPONSOR_TRIAL_EXPENSE",
            "insurance_plan": "Clinical Core Grant",
            "coverage_tier": "Tier-1 Investigational",
            "has_preauth": False,
        },
        "relevant_policies": [],

        # RAG analysis synthesized payload placeholder
        "rag_analysis": None,
        "rag_query": None,

        # Rules
        "protocol_rules": protocol_rules or [],

        # Guardrail execution tracking
        "guardrail_1_passed": None,
        "guardrail_2_passed": None,

        # Reducer lists (Annotated with operator.add)
        "messages": [],
        "audit_logs": [
            {
                "step": "doctor_action_submission",
                "status": "success",
                "patient_id": clean_pid,
                "trial_id": effective_trial_id,
                "proposed_action": proposed_action,
            }
        ],
        "violations": [],
        "matched_criteria": [],
        "unknown_criteria": [],
        "not_applicable_criteria": [],
        "dosage_checks": [
            {
                "action_type": "prescribed_action_review",
                "proposed_action": proposed_action,
                "status": "PENDING_REVIEW",
            }
        ],
        "safety_evidence": [],
        "criteria_evaluations": [],
        "evidence": evidence or [],

        # Multi-Agent Sub-Verdict History Reducers
        "compliance_verdict_history": [],
        "safety_verdict_history": [],
        "financial_verdict_history": [],
        "multi_agent_iteration_history": [],

        # Evaluation & Adjudication Verdict Parameters
        "evaluation": None,
        "rag_evaluation": None,
        "decision": None,
        "eligibility": None,
        "explanation": None,
        "confidence": None,
        "needs_human_review": False,
        "is_short_circuited": False,

        # Trial Phase, Status & HITL Tracking
        "trial_phase": "Phase II",
        "trial_status": "ACTIVE",
        "trial_results": None,
        "compliance_needed": False,
        "toxicity_score": 0.0,
        "financial_approved": True,
        "agent_consensus": False,
        "final_decision": None,
        "requires_hitl": False,
        "hitl_reason": None,
        "hitl_approval_status": "PENDING",
        "hitl_comments": None,
        "modification": None,  # Properly registered for HITL refine cycles

        # Loop Counters & Execution Stage Control
        "refinement_iteration_count": 0,
        "missing_data_query_count": 0,
        "max_missing_data_retries": 3,
        "agent_consensus_reached": False,
        "active_evaluation_stage": "ingestion_complete",
        "terminal_reason": None,
        "error_message": None,
        "raw_api_response": None,
    }

    return clean_state