"""
Ingress validation and resupply guardrails (Guardrail 1).

Updated to synchronize with the complete TrialGuard pipeline:
  - Validates that the synthesized RAG output (state['rag_analysis']) conforms
    to the RagAnalysisOutput JSON contract (trial_id, decision, eligibility,
    rule_analysis_package, violations, etc.).
  - Enforces core patient demographic integrity (patient_id, age, sex).
  - Standardizes sex representation ('female' / 'male') during validation and resupply.
  - Attempts silent FHIR auto-resupply or pauses execution via LangGraph interrupt()
    if critical schema elements remain unresolved.
  - Correctly resets short-circuit flags upon successful resupply to resume pipeline flow.
"""

import copy
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from langgraph.types import interrupt
from shared_schemas.state import TrialState

MANDATORY_PATIENT_FIELDS = ["patient_id", "age", "sex"]
DEFAULT_MAX_MISSING_DATA_RETRIES = 3


def _resolve_fhir_patient(patient_id: str) -> dict:
    """Attempts to fetch patient data from mcp_ehr with dynamic path fallback."""
    try:
        from mcp_ehr.fhir_client import get_patient
        return get_patient(patient_id)
    except ImportError:
        repo_root = Path(__file__).resolve().parents[3]
        pkg_src = repo_root / "packages" / "mcp-ehr" / "src"
        pkg_inner = pkg_src / "mcp_ehr"
        for p in (str(pkg_src), str(pkg_inner)):
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            from mcp_ehr.fhir_client import get_patient
            return get_patient(patient_id)
        except Exception:
            try:
                from fhir_client import get_patient
                return get_patient(patient_id)
            except Exception:
                return {}
    except Exception:
        return {}


def _normalize_sex(raw_sex: Any) -> Optional[str]:
    """Standardizes sex to 'female' or 'male' conforming to rules and state schema."""
    if raw_sex is None:
        return None
    s = str(raw_sex).strip().lower()
    if s in ["female", "f"]:
        return "female"
    if s in ["male", "m"]:
        return "male"
    return str(raw_sex)


def guardrail_schema_check(state: TrialState) -> Dict[str, Any]:
    """
    Guardrail 1 (G1): Validates schema integrity of both PatientData and
    the upstream synthesized `rag_analysis` contract.
    """
    raw_patient = state.get("patient") or state.get("raw_fhir_patient") or {}
    patient = copy.deepcopy(raw_patient)
    rag_data = state.get("rag_analysis")
    missing_fields: List[str] = []

    # 1. Root & Trial Context Check
    trial_id = state.get("trial_id") or (rag_data.get("trial_id") if rag_data else None)
    if not trial_id:
        missing_fields.append("trial_id")

    # 2. Patient Demographics Integrity Check
    for field in MANDATORY_PATIENT_FIELDS:
        val = patient.get(field)
        if val is None or str(val).strip() == "":
            missing_fields.append(f"patient.{field}")

    # Standardize sex
    if patient.get("sex"):
        patient["sex"] = _normalize_sex(patient["sex"])

    # 3. Upstream RAG Analysis Schema Contract Check
    if not rag_data:
        missing_fields.append("rag_analysis")
    else:
        pkg = rag_data.get("rule_analysis_package")
        if not pkg or not isinstance(pkg, dict):
            missing_fields.append("rag_analysis.rule_analysis_package")
        if not rag_data.get("decision"):
            missing_fields.append("rag_analysis.decision")
        if not rag_data.get("eligibility"):
            missing_fields.append("rag_analysis.eligibility")

    is_failed = len(missing_fields) > 0
    audit_entry = {
        "step": "guardrail_schema_check",
        "status": "failed" if is_failed else "passed",
        "missing_fields": missing_fields,
        "has_rag_payload": bool(rag_data),
    }

    return {
        "guardrail_1_passed": not is_failed,
        "is_short_circuited": is_failed,
        "patient": patient,
        "active_evaluation_stage": "ingestion_sanity_check",
        "audit_logs": [audit_entry],
    }


def try_autoresupply_from_fhir(patient_id: str) -> dict:
    """Attempts to retrieve the complete patient bundle from the FHIR server or fixtures."""
    if not patient_id:
        return {}
    return _resolve_fhir_patient(patient_id)


def route_after_g1(state: TrialState) -> str:
    """
    Routes cleanly to Guardrail 2 (G2) if schema verification passes.
    Otherwise routes to resupply or terminates if retry budget is exhausted.
    """
    if state.get("guardrail_1_passed") and not state.get("is_short_circuited"):
        return "guardrail_2"

    max_retries = state.get("max_missing_data_retries", DEFAULT_MAX_MISSING_DATA_RETRIES)
    current_count = state.get("missing_data_query_count", 0)

    if current_count >= max_retries:
        return "max_iterations_exceeded"

    return "missing_data_request"


def max_iterations_exceeded_node(state: TrialState) -> Dict[str, Any]:
    """Terminal failure node when data resupply retries are exhausted."""
    audit_logs = state.get("audit_logs", [])
    g1_logs = [log for log in audit_logs if log.get("step") == "guardrail_schema_check"]
    latest_g1_log = g1_logs[-1] if g1_logs else {}
    missing = latest_g1_log.get("missing_fields", [])

    retries_used = state.get("missing_data_query_count", 0)
    message = (
        f"Mandatory schema resupply failed after {retries_used} attempt(s). "
        f"Still missing: {missing}. Aborting evaluation."
    )

    return {
        "trial_status": "ABORTED",
        "eligibility": "INDETERMINATE",
        "decision": "FAIL",
        "final_decision": "ERROR_MAX_RETRIES_EXCEEDED",
        "terminal_reason": "missing_data_retry_budget_exhausted",
        "error_message": message,
        "is_short_circuited": True,
        "needs_human_review": True,
        "requires_hitl": True,
        "hitl_reason": message,
        "hitl_approval_status": "FAILED_INGESTION",
        "audit_logs": [{
            "step": "max_iterations_exceeded",
            "status": "error",
            "missing_fields": missing,
            "retries_used": retries_used,
        }],
    }


def _merge_patient_payload(current_patient: Dict[str, Any], resupplied_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merges updated clinical values, narratives, and protocol facts."""
    explicit_patient = resupplied_payload.get("patient", {})
    fallback_patient = {
        k: v for k, v in resupplied_payload.items()
        if k in MANDATORY_PATIENT_FIELDS or k in [
            "internal_id", "fhir_id", "name", "dob", "cohort", "weight",
            "diagnoses", "medications", "allergies", "lab_results",
            "vital_signs", "cardiac_function", "medical_history",
            "medical_history_narrative", "current_symptoms", "protocol_facts",
            "pregnancy_test_result", "consent_capacity", "ecog_status",
            "last_systemic_therapy_date"
        ]
    }
    merged_resupply = {**fallback_patient, **explicit_patient}

    merged_patient = dict(current_patient)
    for key, val in merged_resupply.items():
        if isinstance(val, dict) and isinstance(merged_patient.get(key), dict):
            merged_patient[key] = {**merged_patient[key], **val}
        else:
            merged_patient[key] = val

    if merged_patient.get("sex"):
        merged_patient["sex"] = _normalize_sex(merged_patient["sex"])

    return merged_patient


def data_resupply_node(state: TrialState) -> Dict[str, Any]:
    """
    Attempts resolution of missing attributes:
    1. Silent programmatic lookup via FHIR.
    2. Interactive pause via LangGraph interrupt() for clinician entry.
    """
    # Always increment retry budget to prevent infinite loops
    current_count = state.get("missing_data_query_count", 0) + 1

    audit_logs = state.get("audit_logs", [])
    g1_logs = [log for log in audit_logs if log.get("step") == "guardrail_schema_check"]
    latest_g1_log = g1_logs[-1] if g1_logs else {}
    missing = list(latest_g1_log.get("missing_fields", []))

    current_patient = dict(state.get("patient") or {})
    current_trial_id = state.get("trial_id")
    new_audit_logs: List[Dict[str, Any]] = []

    # 1. Silent FHIR auto-resupply attempt
    patient_id = (
        current_patient.get("patient_id") 
        or current_patient.get("internal_id")
        or state.get("patient_id", "")
    )
    raw_bundle = try_autoresupply_from_fhir(patient_id)

    if raw_bundle:
        patient_data = raw_bundle.get("patient", raw_bundle)
        current_patient = _merge_patient_payload(current_patient, patient_data)
        
        # Check both root and nested bundle for trial identifier
        if not current_trial_id:
            current_trial_id = (
                raw_bundle.get("trial_id")
                or raw_bundle.get("assigned_demo_trial_id")
                or patient_data.get("trial_id")
            )

        new_audit_logs.append({
            "step": "data_resupply",
            "source": "FHIR_AUTO",
            "status": "RESUPPLIED",
            "resupplied_keys": list(patient_data.keys()),
        })

    # Recalculate what remains missing across patient, trial, and upstream RAG
    still_missing: List[str] = []
    if not current_trial_id:
        still_missing.append("trial_id")

    for field in MANDATORY_PATIENT_FIELDS:
        if current_patient.get(field) is None or str(current_patient.get(field)).strip() == "":
            still_missing.append(f"patient.{field}")

    # Retain upstream RAG missing items if present
    for m in missing:
        if m.startswith("rag_analysis") and m not in still_missing:
            still_missing.append(m)

    # If all demographic requirements are satisfied, return to pipeline
    if not any(k.startswith("patient.") or k == "trial_id" for k in still_missing):
        return {
            "patient": current_patient,
            "raw_fhir_patient": raw_bundle or state.get("raw_fhir_patient"),
            "trial_id": current_trial_id,
            "missing_data_query_count": current_count,
            "is_short_circuited": False,
            "guardrail_1_passed": True,
            "audit_logs": new_audit_logs,
        }

    # 2. Human-in-the-loop (HITL) interrupt fallback
    raw_resupply = interrupt({
        "type": "mandatory_data_missing",
        "missing_fields": still_missing,
        "trial_id_missing": "trial_id" in still_missing,
        "message": f"Missing required data fields: {still_missing}. Please provide values.",
        "query_count": current_count,
        "auto_resolved_by_fhir": list(raw_bundle.keys()) if raw_bundle else [],
    })

    resupplied_payload = raw_resupply if isinstance(raw_resupply, dict) else {}
    current_patient = _merge_patient_payload(current_patient, resupplied_payload)
    updated_trial_id = resupplied_payload.get("trial_id") or current_trial_id

    new_audit_logs.append({
        "step": "data_resupply",
        "source": "DOCTOR_MANUAL",
        "status": "RESUPPLIED",
        "resupplied_keys": list(resupplied_payload.keys()),
    })

    return {
        "patient": current_patient,
        "raw_fhir_patient": current_patient,
        "trial_id": updated_trial_id,
        "missing_data_query_count": current_count,
        "is_short_circuited": False,
        "guardrail_1_passed": True,
        "audit_logs": new_audit_logs,
    }