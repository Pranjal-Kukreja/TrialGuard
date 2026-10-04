"""
Standardized terminal audit reporting node (complete_audit_node).

Updated to synchronize with the complete TrialGuard pipeline:
  - Summarizes multi-agent specialist verdicts (Compliance, Safety, Financial).
  - Reflects refinement loop iterations and chronological history tracking.
  - Normalizes eligibility, final_decision, and confidence parameters.
  - Formats an immutable 21 CFR Part 11 audit entry into state['audit_logs'].
"""

import json
import time
from typing import Any, Dict, List
from shared_schemas.state import TrialState


def _normalize_action_str(action: Any) -> str:
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
    return str(action or "Standard Protocol")


def complete_audit_node(state: TrialState) -> Dict[str, Any]:
    """
    Standardized terminal audit reporting node.
    Extracts finalized values, prints a structured audit log, and seals the state.
    """
    verdict = state.get("final_decision") or state.get("decision") or "UNKNOWN"
    raw_eligibility = state.get("eligibility")
    if raw_eligibility:
        eligibility = raw_eligibility
    elif verdict in ("APPROVED", "ACCEPTED"):
        eligibility = "ELIGIBLE"
    elif verdict in ("REJECTED", "FAIL"):
        eligibility = "INELIGIBLE"
    else:
        eligibility = "INDETERMINATE"

    patient_id = state.get("patient_id")
    trial_id = state.get("trial_id")
    cohort = state.get("cohort") or "Unassigned"
    prescribed_action = _normalize_action_str(
        state.get("prescribed_action") or state.get("proposed_action")
    )
    modification = state.get("modification")
    confidence = state.get("confidence")
    violations = state.get("violations", [])
    hitl_status = state.get("hitl_approval_status") or "AUTO_PROCESSED"
    clinician_notes = state.get("hitl_comments")
    refinement_count = state.get("refinement_iteration_count", 0)

    # Sub-agent specialist verdict histories
    comp_history = state.get("compliance_verdict_history", [])
    safe_history = state.get("safety_verdict_history", [])
    fin_history = state.get("financial_verdict_history", [])

    comp_latest = comp_history[-1] if comp_history else {}
    safe_latest = safe_history[-1] if safe_history else {}
    fin_latest = fin_history[-1] if fin_history else {}

    print("\n" + "=" * 75)
    print("📊 TRIALGUARD FINAL ADJUDICATION AUDIT RECORD (21 CFR PART 11)")
    print("=" * 75)
    print(f" • Patient ID           : {patient_id}")
    print(f" • Trial Identifier     : {trial_id}")
    print(f" • Assigned Cohort      : {cohort}")
    print(f" • Evaluated Action     : {prescribed_action}")
    if modification:
        print(f" • Modification Note    : {modification}")
    print(f" • Final Adjudication   : {verdict} ({eligibility})")
    print(f" • Confidence Score     : {f'{confidence:.2f}' if confidence is not None else 'N/A'}")
    print(f" • Refinement Loops     : {refinement_count}")
    print(f" • Audit Resolution     : {'CLINICIAN_OVERRIDE' if clinician_notes else 'AUTOMATED_CONSENSUS'}")
    print(f" • HITL Review Status   : {hitl_status}")

    # Display Sub-Agent Summary
    print("\n --- Sub-Agent Specialist Summary ---")
    print(f" • Compliance Agent     : {comp_latest.get('compliance_status', 'N/A')} (Total Evaluations: {len(comp_history)})")
    print(f" • Safety Agent         : {safe_latest.get('safety_status', 'N/A')} (Risk Score: {safe_latest.get('risk_score', 0.0)})")
    print(f" • Financial Agent      : {fin_latest.get('coverage_status', 'N/A')} (Tier: {fin_latest.get('tier', 'Standard')})")

    # Display Active Deviations / Violations
    print(f"\n • Recorded Violations  : {len(violations)}")
    if violations:
        for idx, v in enumerate(violations, start=1):
            rule = v.get("rule_id", "RULE_UNKNOWN")
            severity = v.get("severity", "HARD")
            reason = v.get("reason", "Protocol deviation recorded")
            param = v.get("parameter", "general")
            diff = v.get("difference")
            diff_str = f" [Δ: {diff.get('amount')} {diff.get('direction', '')}]" if isinstance(diff, dict) else ""
            print(f"   [{idx}] [{severity}] {rule} ({param}): {reason}{diff_str}")

    if clinician_notes:
        print(f"\n • Clinician Rationale  : {clinician_notes}")
    print("=" * 75 + "\n")

    # Immutable Audit Log Entry
    audit_entry: Dict[str, Any] = {
        "timestamp": time.time(),
        "step": "final_audit_sealed",
        "status": "completed",
        "patient_id": patient_id,
        "trial_id": trial_id,
        "cohort": cohort,
        "action": prescribed_action,
        "modification": modification,
        "final_decision": verdict,
        "eligibility": eligibility,
        "confidence": confidence,
        "active_violations": len(violations),
        "hitl_status": hitl_status,
        "clinician_notes": clinician_notes,
        "refinement_iterations": refinement_count,
        "sub_agents": {
            "compliance_iterations": len(comp_history),
            "final_compliance_status": comp_latest.get("compliance_status"),
            "final_safety_status": safe_latest.get("safety_status"),
            "final_financial_status": fin_latest.get("coverage_status"),
        },
    }

    return {
        "final_decision": verdict,
        "decision": verdict,
        "eligibility": eligibility,
        "active_evaluation_stage": "adjudication_sealed",
        "terminal_reason": f"Workflow completed with verdict: {verdict}",
        "audit_logs": [audit_entry],  # Appends via operator.add
    }