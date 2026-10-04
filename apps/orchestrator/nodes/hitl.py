"""
Human-in-the-Loop (HITL) Review Node for Clinical Trial Adjudication.

Handles:
  - Halting pipeline execution via LangGraph interrupt() with full sub-agent context:
      * Compliance, Safety, and Financial specialist verdict histories
      * Protocol violations, deviations, and source evidence chunks
  - Action 1 ('accept'): Clinician manual approval/override to qualify patient.
  - Action 2 ('reject'): Clinician confirmation of protocol or safety exclusion.
  - Action 3 ('modify'): Regimen titration, fact patching, and loop-back to
    rag_analysis while passing the modification rationale to all sub-agents.
"""

import copy
from typing import Any, Dict, Literal
from langgraph.types import Command, interrupt
from shared_schemas.state import TrialState


def hitl_review_node(state: TrialState) -> Command[Literal["complete_audit_node", "rag_analysis"]]:
    """
    Suspends execution when criteria require clinician review or override.
    Resumes when a clinician submits an action payload:
        action: 'accept' | 'reject' | 'modify'
    """
    comp_history = state.get("compliance_verdict_history", [])
    safe_history = state.get("safety_verdict_history", [])
    fin_history = state.get("financial_verdict_history", [])

    # 1. Capture snapshot strictly aligned with TrialState schema and UI needs
    review_payload = {
        "patient_id": state.get("patient_id"),
        "trial_id": state.get("trial_id"),
        "cohort": state.get("cohort"),
        "prescribed_action": state.get("prescribed_action"),
        "preliminary_decision": state.get("decision") or "NEEDS_REVIEW",
        "eligibility": state.get("eligibility") or "PENDING_CLINICIAN_REVIEW",
        "confidence": state.get("confidence"),
        "violations": state.get("violations", []),
        "unknown_criteria": state.get("unknown_criteria", []),
        "matched_criteria": state.get("matched_criteria", []),
        "sub_agents": {
            "compliance": comp_history[-1] if comp_history else None,
            "safety": safe_history[-1] if safe_history else None,
            "financial": fin_history[-1] if fin_history else None,
        },
        "compliance_iterations": len(comp_history),
        "refinement_iteration_count": state.get("refinement_iteration_count", 0),
        "reason": state.get("hitl_reason") or state.get("explanation"),
        "available_actions": ["accept", "reject", "modify"],
    }

    # Check whether Human-in-the-Loop review is genuinely required
    requires_review = (
        state.get("requires_hitl") is True
        or state.get("needs_human_review") is True
        or state.get("decision") in ("NEEDS_REVIEW", "PENDING_CLINICIAN_REVIEW")
    )

    if not requires_review:
        audit_entry = {
            "step": "hitl_automated_bypass",
            "action": "auto_approve",
            "reviewer_id": "SYSTEM_AUTOMATED",
            "status": state.get("decision") or "APPROVED",
            "rationale": "Automated consensus reached without requiring clinician escalation.",
            "iteration": state.get("refinement_iteration_count", 0),
        }
        return Command(
            goto="complete_audit_node",
            update={
                "final_decision": state.get("final_decision") or state.get("decision") or "APPROVED",
                "eligibility": state.get("eligibility") or "ELIGIBLE",
                "hitl_approval_status": "AUTO_BYPASS_NO_REVIEW_NEEDED",
                "requires_hitl": False,
                "needs_human_review": False,
                "active_evaluation_stage": "hitl_bypassed",
                "audit_logs": [audit_entry],
            },
        )

    # 2. Halt execution until resumed with clinician input
    human_response: Dict[str, Any] = interrupt(review_payload)
    if not isinstance(human_response, dict):
        human_response = {}
    action = str(human_response.get("action", "")).lower().strip()
    clinician_notes = (
        human_response.get("notes") 
        or human_response.get("rationale") 
        or "No clinician notes provided."
    )
    reviewer_id = human_response.get("reviewer_id", "CLINICIAN_ON_DUTY")

    # -------------------------------------------------------------------
    # Action 1: ACCEPT (Human override to qualify patient)
    # -------------------------------------------------------------------
    if action == "accept":
        audit_entry = {
            "step": "hitl_manual_override",
            "action": "accept",
            "reviewer_id": reviewer_id,
            "status": "APPROVED",
            "rationale": clinician_notes,
            "previous_decision": state.get("decision"),
            "iteration": state.get("refinement_iteration_count", 0),
        }
        return Command(
            goto="complete_audit_node",
            update={
                "final_decision": "ACCEPTED",
                "eligibility": "ELIGIBLE",
                "decision": "ACCEPTED",
                "hitl_approval_status": "APPROVED_OVERRIDE",
                "hitl_comments": clinician_notes,
                "requires_hitl": False,
                "needs_human_review": False,
                "active_evaluation_stage": "hitl_accepted_override",
                "audit_logs": [audit_entry],  # Appends via operator.add
            },
        )

    # -------------------------------------------------------------------
    # Action 2: REJECT (Human confirms safety/protocol exclusion)
    # -------------------------------------------------------------------
    elif action == "reject":
        audit_entry = {
            "step": "hitl_manual_override",
            "action": "reject",
            "reviewer_id": reviewer_id,
            "status": "REJECTED",
            "rationale": clinician_notes,
            "previous_decision": state.get("decision"),
            "iteration": state.get("refinement_iteration_count", 0),
        }
        return Command(
            goto="complete_audit_node",
            update={
                "final_decision": "REJECTED",
                "eligibility": "INELIGIBLE",
                "decision": "REJECTED",
                "hitl_approval_status": "REJECTED_BY_CLINICIAN",
                "hitl_comments": clinician_notes,
                "requires_hitl": False,
                "needs_human_review": False,
                "active_evaluation_stage": "hitl_rejected",
                "audit_logs": [audit_entry],  # Appends via operator.add
            },
        )

    # -------------------------------------------------------------------
    # Action 3: MODIFY (Regimen change, data patch & loop-back to rag_analysis)
    # -------------------------------------------------------------------
    elif action == "modify":
        corrected_patient = copy.deepcopy(state.get("patient", {}))
        corrections = human_response.get("corrections", {})
        
        # Support either explicit updated_action or prescribed_action patch
        updated_action = (
            human_response.get("updated_action")
            or corrections.get("prescribed_action")
            or human_response.get("proposed_action")
            or state.get("prescribed_action")
        )

        mod_rationale = (
            clinician_notes 
            if clinician_notes != "No clinician notes provided." 
            else f"Action modified to: {updated_action}"
        )

        # Deep patch labs, vital_signs, cardiac_function, medications, or protocol_facts
        for field, payload in corrections.items():
            if field in ("prescribed_action", "proposed_action"):
                continue
            if isinstance(payload, dict) and isinstance(corrected_patient.get(field), dict):
                merged_bucket = dict(corrected_patient[field])
                merged_bucket.update(payload)
                corrected_patient[field] = merged_bucket
            else:
                corrected_patient[field] = payload

        # Keep top-level medications list synchronized if modified in corrections
        if "medications" in corrections:
            corrected_patient["medications"] = corrections["medications"]

        audit_entry = {
            "step": "hitl_data_modification",
            "action": "modify",
            "reviewer_id": reviewer_id,
            "modified_fields": list(corrections.keys()),
            "updated_action": updated_action,
            "modification": mod_rationale,
            "rationale": mod_rationale,
            "iteration": state.get("refinement_iteration_count", 0) + 1,
        }

        return Command(
            goto="rag_analysis",
            update={
                "patient": corrected_patient,
                "prescribed_action": updated_action,
                "proposed_action": updated_action,
                "query": updated_action,
                "modification": mod_rationale,  # Critical: Propagates to Compliance, Safety, and Financial sub-agents
                "refinement_iteration_count": state.get("refinement_iteration_count", 0) + 1,
                "hitl_approval_status": "MODIFIED_FOR_REANALYSIS",
                "hitl_comments": mod_rationale,
                "active_evaluation_stage": "hitl_modification_loop",
                # Reset intermediate single-turn parameters
                "evaluation": None,
                "rag_evaluation": None,
                "decision": None,
                "eligibility": None,
                "requires_hitl": False,
                "needs_human_review": False,
                "audit_logs": [audit_entry],  # Appends via operator.add
            },
        )

    else:
        raise ValueError(f"Invalid HITL action '{action}'. Permitted actions: ['accept', 'reject', 'modify'].")