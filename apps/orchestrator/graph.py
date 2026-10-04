"""
LangGraph Workflow Orchestrator for Clinical Trial Adjudication.

Architecture Flow:
  START 
    -> fhir_fetch_node (fetches raw patient EHR/FHIR observations)
    -> rag_analysis_node (synthesizes the central RagAnalysisOutput payload)
    -> guardrail_1 (schema verification of the synthesized analysis)
    -> guardrail_2 (safety boundaries & protocol exclusion checks)
    -> clinical_trial_status_check
    -> master_agent 
         ├── compliance_agent ─────┐
         ├── safety_agent ─────────┼──> multi_agent_evaluation ──> hitl_escalation
         ├── financial_agent ──────┤       (synthesizes all 4           │ (modify loops to rag_analysis)
         └── protocol_adjudication ┘        agent outputs)              v (accept/reject)
  short_circuit ───────────────────────────────────────────────────> complete_audit_node -> END
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

# Resolve Repo Root
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Dynamic client imports from agent-master & agent-compliance
try:
    from apps.agent_master.master_client import financial_agent_node, safety_agent_node
except ImportError:
    from apps.orchestrator.nodes.master_client import financial_agent_node, safety_agent_node

from apps.orchestrator.nodes.compliance_client import compliance_eval_node
from apps.orchestrator.nodes.ingress import (
    data_resupply_node,
    guardrail_schema_check,
    max_iterations_exceeded_node,
    route_after_g1,
)
from apps.orchestrator.nodes.protocol import (
    clinical_trial_status_check_node,
    parallel_processing_fan_out,
    protocol_verification_node,
    route_after_g2,
    route_after_trial_status,
    short_circuit_node,
)
from apps.orchestrator.nodes.protocol_adjudication import (
    protocol_adjudication_node,
)
from apps.orchestrator.nodes.rag_node import (
    rag_protocol_retrieval_node,
)
from apps.orchestrator.nodes.hitl import hitl_review_node
from apps.orchestrator.nodes.audit import complete_audit_node
from shared_schemas.state import TrialState


def multi_agent_evaluation_node(state: TrialState) -> Dict[str, Any]:
    """
    Convergence & synthesis node:
    Consolidates safety, compliance, financial, and protocol findings into the state.
    Flushes stale historical violations and prevents duplicate error accumulation.
    """
    comp = state.get("compliance_verdict_history", [{}])[-1] if state.get("compliance_verdict_history") else {}
    safe = state.get("safety_verdict_history", [{}])[-1] if state.get("safety_verdict_history") else {}
    fin = state.get("financial_verdict_history", [{}])[-1] if state.get("financial_verdict_history") else {}

    adjudication_decision = state.get("decision") or "NEEDS_REVIEW"

    # Gather active violations exclusively from the current iteration to prevent duplicate stacking
    active_violations = []
    seen_identifiers = set()

    # 1. Evaluate Compliance Agent violations
    if comp.get("compliance_status") != "COMPLIANT" or not comp.get("valid", True):
        for v in comp.get("violations", []):
            if isinstance(v, dict):
                ident = (v.get("rule_id", "COMPLIANCE_BREACH"), v.get("reason", ""))
                if ident not in seen_identifiers:
                    active_violations.append(v)
                    seen_identifiers.add(ident)

    # 2. Evaluate Safety Agent violations
    if safe.get("safety_status") not in ("CLEARED", "SAFE") or safe.get("risk_score", 0.0) > 0.5:
        for v in safe.get("violations", []):
            if isinstance(v, dict):
                ident = (v.get("rule_id", "SAFETY_BREACH"), v.get("reason", ""))
                if ident not in seen_identifiers:
                    active_violations.append(v)
                    seen_identifiers.add(ident)

    # 3. Evaluate Protocol Adjudication Node violations
    if adjudication_decision in ("REJECTED", "FAIL"):
        eval_dict = state.get("evaluation") or {}
        for v in eval_dict.get("adjudication_violations", []):
            if isinstance(v, dict):
                ident = (v.get("rule_id", "PROTOCOL_BREACH"), v.get("reason", ""))
                if ident not in seen_identifiers:
                    active_violations.append(v)
                    seen_identifiers.add(ident)

    # Consensus Logic
    comp_ok = comp.get("compliance_status") == "COMPLIANT" and comp.get("valid", True)
    safe_ok = safe.get("safety_status") in ("CLEARED", "SAFE") and safe.get("risk_score", 0.0) <= 0.5
    fin_ok = fin.get("coverage_status") == "COVERED"
    adjudication_ok = adjudication_decision == "APPROVED"

    if len(active_violations) > 0 or not safe_ok or not fin_ok or not comp_ok:
        total_verdict = "REJECTED"
        eligibility = "INELIGIBLE"
    elif adjudication_ok and comp_ok and safe_ok and fin_ok:
        total_verdict = "APPROVED"
        eligibility = "ELIGIBLE"
    else:
        total_verdict = "NEEDS_REVIEW"
        eligibility = "PENDING_CLINICIAN_REVIEW"

    requires_hitl = (
        total_verdict in ("NEEDS_REVIEW", "PENDING_CLINICIAN_REVIEW")
        or bool(safe.get("needs_human_review"))
        or bool(comp.get("needs_human_review"))
        or bool(fin.get("needs_human_review"))
    )

    audit_entry = {
        "step": "multi_agent_evaluation",
        "status": "converged",
        "total_verdict": total_verdict,
        "adjudication_verdict": adjudication_decision,
        "compliance_status": comp.get("compliance_status"),
        "safety_status": safe.get("safety_status"),
        "coverage_status": fin.get("coverage_status"),
        "active_violations": len(active_violations),
        "requires_hitl": requires_hitl,
    }

    iteration_num = state.get("refinement_iteration_count", 0) + 1
    snapshot = {
        "iteration": iteration_num,
        "compliance": comp,
        "safety": safe,
        "financial": fin,
        "overall_action_permitted": total_verdict == "APPROVED",
    }

    return {
        "decision": total_verdict,
        "final_decision": total_verdict,
        "eligibility": eligibility,
        "violations": active_violations,  # Flushes stale errors and replaces with deduplicated active list
        "requires_hitl": requires_hitl,
        "needs_human_review": requires_hitl,
        "multi_agent_iteration_history": [snapshot],
        "active_evaluation_stage": "multi_agent_consensus_complete",
        "audit_logs": [audit_entry],
    }


def _import_get_patient():
    try:
        from mcp_ehr.fhir_client import get_patient
        return get_patient
    except ImportError:
        try:
            from fhir_client import get_patient
            return get_patient
        except ImportError:
            candidates = [
                REPO_ROOT / "packages" / "mcp-ehr" / "src" / "mcp_ehr",
                REPO_ROOT / "packages" / "mcp-ehr" / "src",
            ]
            for candidate in candidates:
                if candidate.exists() and str(candidate) not in sys.path:
                    sys.path.insert(0, str(candidate))
            from fhir_client import get_patient
            return get_patient


def fhir_fetch_node(state: TrialState) -> Dict[str, Any]:
    if state.get("raw_fhir_patient") and state.get("patient"):
        return {"active_evaluation_stage": "fhir_data_ready"}

    patient_identifier = state.get("patient_id") or (state.get("patient") or {}).get("patient_id")
    if not patient_identifier:
        return {
            "active_evaluation_stage": "fhir_fetch_failed",
            "error_message": "Missing patient_id in initial state",
        }

    try:
        get_patient = _import_get_patient()
        raw_patient = get_patient(str(patient_identifier))
        clean_patient = raw_patient.get("patient", raw_patient)

        target_trial_id = (
            state.get("trial_id")
            or raw_patient.get("assigned_demo_trial_id")
            or raw_patient.get("trial_id")
            or clean_patient.get("trial_id")
            or "NCT02415400"
        )

        return {
            "raw_fhir_patient": raw_patient,
            "patient": clean_patient,
            "trial_id": target_trial_id,
            "cohort": raw_patient.get("cohort") or clean_patient.get("cohort") or "Cohort A - Standard Protocol",
            "active_evaluation_stage": "fhir_fetch_complete",
        }
    except Exception as exc:
        return {
            "active_evaluation_stage": "fhir_fetch_failed",
            "error_message": f"Failed to fetch FHIR patient: {exc}",
        }



def build_graph(checkpointer: Optional[BaseCheckpointSaver] = None):
    if checkpointer is None:
        try:
            from apps.orchestrator.checkpointer import get_default_checkpointer
            checkpointer = get_default_checkpointer()
        except Exception as exc:
            print(f"[build_graph] Checkpointer loading notice: {exc}")

    graph = StateGraph(TrialState)

    # Core Ingress & Guardrails
    graph.add_node("fhir_fetch", fhir_fetch_node)
    graph.add_node("rag_analysis", rag_protocol_retrieval_node)
    graph.add_node("guardrail_1", guardrail_schema_check)
    graph.add_node("data_resupply", data_resupply_node)
    graph.add_node("max_iterations_exceeded", max_iterations_exceeded_node)
    graph.add_node("guardrail_2", protocol_verification_node)
    graph.add_node("short_circuit", short_circuit_node)
    graph.add_node("clinical_trial_status_check", clinical_trial_status_check_node)
    
    # Master Dispatcher & Specialist Nodes
    graph.add_node("master_agent", parallel_processing_fan_out)
    graph.add_node("compliance_agent", compliance_eval_node)
    graph.add_node("safety_agent", safety_agent_node)
    graph.add_node("financial_agent", financial_agent_node)
    graph.add_node("protocol_adjudication", protocol_adjudication_node)

    # Consensus & HITL
    graph.add_node("multi_agent_evaluation", multi_agent_evaluation_node)
    graph.add_node("hitl_escalation", hitl_review_node)
    graph.add_node("complete_audit_node", complete_audit_node)

    # Graph Flow Topology
    graph.add_edge(START, "fhir_fetch")
    graph.add_edge("fhir_fetch", "rag_analysis")
    graph.add_edge("rag_analysis", "guardrail_1")

    graph.add_conditional_edges(
        "guardrail_1",
        route_after_g1,
        {
            "guardrail_2": "guardrail_2",
            "missing_data_request": "data_resupply",
            "max_iterations_exceeded": "max_iterations_exceeded",
        },
    )
    graph.add_edge("data_resupply", "fhir_fetch")
    graph.add_edge("max_iterations_exceeded", "complete_audit_node")

    graph.add_conditional_edges(
        "guardrail_2",
        route_after_g2,
        {
            "short_circuit_node": "short_circuit",
            "clinical_trial_status_check": "clinical_trial_status_check",
        },
    )

    graph.add_conditional_edges(
        "clinical_trial_status_check",
        route_after_trial_status,
        {
            "short_circuit_node": "short_circuit",
            "parallel_processing_fan_out": "master_agent",
        },
    )
    graph.add_edge("short_circuit", "complete_audit_node")

    # Parallel Fan-Out
    graph.add_edge("master_agent", "compliance_agent")
    graph.add_edge("master_agent", "safety_agent")
    graph.add_edge("master_agent", "financial_agent")
    graph.add_edge("master_agent", "protocol_adjudication")

    # Parallel Convergence
    graph.add_edge("compliance_agent", "multi_agent_evaluation")
    graph.add_edge("safety_agent", "multi_agent_evaluation")
    graph.add_edge("financial_agent", "multi_agent_evaluation")
    graph.add_edge("protocol_adjudication", "multi_agent_evaluation")

    graph.add_edge("multi_agent_evaluation", "hitl_escalation")
    graph.add_edge("complete_audit_node", END)

    return graph.compile(checkpointer=checkpointer)


app_graph = build_graph()