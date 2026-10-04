"""
Local Fallback Compliance Evaluator for TrialGuard Orchestrator.

Provides seamless standalone execution when the remote A2A compliance 
service (apps/agent-compliance/a2a_server.py) is not running. Emits 
canonical ComplianceVerdictRecord dictionaries into compliance_verdict_history.
"""

import json
import re
from typing import Any, Dict, List
from shared_schemas.state import ComplianceVerdictRecord, TrialState


def _normalize_action_text(action: Any) -> str:
    """Safely extracts text representation whether action is a string or dictionary."""
    if isinstance(action, dict):
        parts = [
            str(action.get("drug", "")),
            str(action.get("dosage", "")),
            str(action.get("frequency", "")),
            str(action.get("route", "")),
            str(action.get("description", "")),
            str(action.get("raw_text", "")),
        ]
        text = " ".join(p for p in parts if p).strip()
        return text if text else json.dumps(action)
    return str(action or "")


def _extract_dose_mg(action_text: str) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:mg|milligram)", action_text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return 0.0
    return 0.0


def compliance_eval_node(state: TrialState) -> Dict[str, Any]:
    """
    Evaluates protocol compliance locally (dosing limits, intervals)
    and appends a new ComplianceVerdictRecord to state history.
    """
    trial_id = state.get("trial_id", "NCT02415400")
    raw_action = (
        state.get("prescribed_action")
        or state.get("proposed_action")
        or state.get("query")
        or ""
    )
    prescribed_action = _normalize_action_text(raw_action)
    modification = state.get("modification") or ""

    # Synchronize iteration sequence with HITL loop count
    history = state.get("compliance_verdict_history", [])
    refinement_count = state.get("refinement_iteration_count", 0)
    current_iteration = max(refinement_count + 1, len(history) + 1)

    dose = _extract_dose_mg(prescribed_action)
    action_lower = prescribed_action.lower()

    violations: List[Dict[str, Any]] = []

    # 1. Deterministic Protocol Dose Limit (AUGUSTUS NCT02415400 standard: max 5 mg BID)
    if dose > 5.0:
        violations.append({
            "parameter": "dosage",
            "observed": f"{dose} mg",
            "expected": {
                "operator": "<=",
                "value": "5",
                "unit": "mg",
            },
            "protocol_text": "The recommended apixaban dose is 5 mg administered orally twice daily.",
            "reason": f"Prescribed dose of {dose} mg exceeds protocol maximum single dose limit of 5 mg.",
        })

    # 2. Check for missing/prohibited schedules
    if "apixaban" in action_lower and "once daily" in action_lower and dose > 2.5:
        violations.append({
            "parameter": "frequency",
            "observed": "once daily",
            "expected": {
                "operator": "=",
                "value": "twice daily",
                "unit": "schedule",
            },
            "protocol_text": "Apixaban should be administered twice daily (BID).",
            "reason": "Protocol mandates twice-daily scheduling for therapeutic stroke prevention.",
        })

    is_compliant = len(violations) == 0
    compliance_status = "COMPLIANT" if is_compliant else "NON_COMPLIANT"

    mod_suffix = f" [Clinician Modification: '{modification}']" if modification else ""
    if is_compliant:
        explanation = f"Iteration {current_iteration}: Prescribed action '{prescribed_action}' complies with protocol dosing rules.{mod_suffix}"
    else:
        explanation = f"Iteration {current_iteration}: Prescribed action '{prescribed_action}' violates protocol boundaries.{mod_suffix}"

    verdict_record: ComplianceVerdictRecord = {
        "iteration": current_iteration,
        "compliance_status": compliance_status,
        "valid": is_compliant,
        "confidence": 0.95,
        "violations": violations,
        "explanation": explanation,
        "sources": [
            {
                "chunk_id": f"{trial_id}-treatment-003",
                "section": "treatment and dosing",
                "score": 0.96,
                "text": "The recommended apixaban dose is 5 mg administered orally twice daily.",
            }
        ],
        "prescribed_action": {
            "drug": "apixaban" if "apixaban" in action_lower else "investigational_agent",
            "raw_text": prescribed_action,
        },
        "needs_human_review": not is_compliant,
    }

    audit_entry = {
        "step": "compliance_evaluation",
        "mode": "LOCAL_STANDALONE",
        "iteration": current_iteration,
        "status": compliance_status,
        "violations_count": len(violations),
        "modification_applied": bool(modification),
    }

    return {
        "compliance_verdict_history": [verdict_record],
        "compliance_needed": not is_compliant,
        "active_evaluation_stage": "compliance_evaluation_complete",
        "audit_logs": [audit_entry],
    }