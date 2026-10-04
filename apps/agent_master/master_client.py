"""
Master A2A Orchestrator Client.
Dispatches evaluation payloads concurrently across specialized microservices:
  - Compliance Agent (Port 8001)
  - Safety Agent (Port 8002)
  - Financial Agent (Port 8003)

Equipped with deterministic offline rule backstops for CI/CD and standalone testing.
"""

import json
import logging
import os
import uuid
from typing import Any, Dict, List, Optional
import httpx

from shared_schemas.state import TrialState

logger = logging.getLogger(__name__)

COMPLIANCE_URL = os.getenv("COMPLIANCE_AGENT_URL", "http://127.0.0.1:8001/rpc").replace("://0.0.0.0:", "://127.0.0.1:")
SAFETY_URL = os.getenv("SAFETY_AGENT_URL", "http://127.0.0.1:8002/rpc").replace("://0.0.0.0:", "://127.0.0.1:")
FINANCIAL_URL = os.getenv("FINANCIAL_AGENT_URL", "http://127.0.0.1:8003/rpc").replace("://0.0.0.0:", "://127.0.0.1:")

HTTP_TIMEOUT_SECONDS = float(os.getenv("A2A_TIMEOUT_SECONDS", "15.0"))


def _normalize_action(action: Any) -> Dict[str, Any]:
    if isinstance(action, dict):
        return action
    return {"raw_text": str(action or "")}


def _extract_numeric_val(val: Any) -> Optional[float]:
    if isinstance(val, dict):
        val = val.get("value")
    if val is None or str(val).strip().lower() in ("none", "null", ""):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _call_a2a_agent(
    url: str,
    method: str,
    payload: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Dispatches an A2A JSON-RPC 2.0 SendMessage request."""
    req_id = str(uuid.uuid4())
    rpc_body = {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": "SendMessage",
        "params": {
            "message": {
                "role": "ROLE_USER",  # protobuf enum expects ROLE_USER
                "parts": [{"text": json.dumps(payload), "media_type": "application/json"}],
            }
        },
    }

    try:
        with httpx.Client(timeout=HTTP_TIMEOUT_SECONDS) as client:
            resp = client.post(url, json=rpc_body)
            if resp.status_code != 200:
                logger.warning("Agent at %s returned status %d", url, resp.status_code)
                return None

            data = resp.json()
            if "error" in data:
                logger.warning("Agent at %s returned RPC error: %s", url, data["error"])
                return None

            artifacts = data.get("result", {}).get("task", {}).get("artifacts", [])
            if artifacts:
                text_part = artifacts[0].get("parts", [{}])[0].get("text", "{}")
                return json.loads(text_part)

            return data.get("result")
    except Exception as exc:
        logger.warning("Failed connecting to agent at %s: %s", url, exc)
        return None


# ---------------------------------------------------------------------------
# Deterministic Fallbacks
# ---------------------------------------------------------------------------
def _deterministic_safety_fallback(patient: Dict[str, Any], iteration: int) -> Dict[str, Any]:
    labs = patient.get("lab_results", {})
    pfacts = patient.get("protocol_facts", {})
    violations: List[Dict[str, Any]] = []

    # 1. Renal Boundary
    egfr = _extract_numeric_val(labs.get("eGFR"))
    if egfr is not None and egfr < 30.0:
        violations.append({
            "rule_id": "SAFETY_RENAL_EGFR_BREACH",
            "parameter": "eGFR",
            "observed": f"{egfr} mL/min/1.73m2",
            "expected": ">= 30.0 mL/min/1.73m2",
            "severity": "HARD",
            "reason": f"Severe renal impairment (eGFR {egfr} < 30). Antithrombotic clearance severely compromised.",
        })

    crcl = _extract_numeric_val(labs.get("creatinine_clearance"))
    if crcl is not None and crcl < 30.0:
        violations.append({
            "rule_id": "SAFETY_RENAL_CLEARANCE_BREACH",
            "parameter": "creatinine_clearance",
            "observed": f"{crcl} mL/min",
            "expected": ">= 30.0 mL/min",
            "severity": "HARD",
            "reason": f"Severe renal impairment (CrCl {crcl} mL/min < 30 mL/min). Antithrombotic clearance severely compromised.",
        })

    # 2. Hepatic Boundary
    alt = _extract_numeric_val(labs.get("ALT"))
    ast = _extract_numeric_val(labs.get("AST"))
    if (alt and alt > 120.0) or (ast and ast > 120.0):
        violations.append({
            "rule_id": "SAFETY_HEPATIC_TRANSAMINASE_ELEVATION",
            "parameter": "ALT/AST",
            "observed": f"ALT={alt}, AST={ast} U/L",
            "expected": "<= 120 U/L",
            "severity": "HARD",
            "reason": "Severe transaminase elevation exceeding 3x ULN.",
        })

    # 3. Bleeding Risk
    if pfacts.get("ongoing_bleeding") is True:
        violations.append({
            "rule_id": "SAFETY_HEMORRHAGE_HAZARD",
            "parameter": "ongoing_bleeding",
            "observed": "True",
            "expected": "False",
            "severity": "HARD",
            "reason": "Active hemorrhage present; systemic anticoagulation contraindicated.",
        })

    is_safe = len(violations) == 0
    return {
        "iteration": iteration,
        "safety_status": "CLEARED" if is_safe else "CRITICAL",
        "risk_score": 0.12 if is_safe else 0.88,
        "contraindications_found": len(violations),
        "violations": violations,
        "summary": "Baseline organ clearance and bleeding risk safe." if is_safe else violations[0]["reason"],
        "needs_human_review": not is_safe,
    }


def _deterministic_financial_fallback(state: TrialState, iteration: int) -> Dict[str, Any]:
    return {
        "iteration": iteration,
        "coverage_status": "COVERED",
        "tier": "Tier-1 Investigational Coverage",
        "violations": [],
        "explanation": "Deterministic fallback: standard investigational sponsor trial coverage.",
        "needs_human_review": False,
    }


# ---------------------------------------------------------------------------
# LangGraph Node Handlers
# ---------------------------------------------------------------------------
def safety_agent_node(state: TrialState) -> Dict[str, Any]:
    patient = state.get("patient") or state.get("raw_fhir_patient") or {}
    iteration = max(
        state.get("refinement_iteration_count", 0) + 1,
        len(state.get("safety_verdict_history", [])) + 1,
    )

    payload = {
        "trial_id": state.get("trial_id", "NCT02415400"),
        "patient_id": state.get("patient_id") or patient.get("patient_id") or patient.get("internal_id") or "UNKNOWN_PATIENT",
        "recent_action": _normalize_action(
            state.get("prescribed_action") or state.get("proposed_action")
        ),
        "patient_data": patient,
        "report_history": state.get("safety_verdict_history", []),
        "modification": state.get("modification", ""),
        "iteration": iteration,
    }

    result = _call_a2a_agent(SAFETY_URL, "evaluate_safety", payload)
    if not result:
        result = _deterministic_safety_fallback(patient, iteration)

    return {
        "safety_verdict_history": [result],
        "audit_logs": [{
            "step": "safety_evaluation",
            "status": result.get("safety_status"),
            "risk_score": result.get("risk_score"),
            "violations_count": len(result.get("violations", [])),
        }],
    }


def financial_agent_node(state: TrialState) -> Dict[str, Any]:
    iteration = max(
        state.get("refinement_iteration_count", 0) + 1,
        len(state.get("financial_verdict_history", [])) + 1,
    )
    payload = {
        "trial_id": state.get("trial_id", "NCT02415400"),
        "recent_action": _normalize_action(
            state.get("prescribed_action") or state.get("proposed_action")
        ),
        "financial_context": state.get("financial_context", {}),
        "relevant_policies": state.get("relevant_policies", []),
        "report_history": state.get("financial_verdict_history", []),
        "iteration": iteration,
    }

    result = _call_a2a_agent(FINANCIAL_URL, "evaluate_financial", payload)
    if not result:
        result = _deterministic_financial_fallback(state, iteration)

    return {
        "financial_verdict_history": [result],
        "audit_logs": [{
            "step": "financial_evaluation",
            "status": result.get("coverage_status"),
            "tier": result.get("tier"),
        }],
    }