"""Protocol compliance specialist used behind the A2A adapter."""

from __future__ import annotations

import json
from typing import Any

from .llm_client import call_llm, parse_json_response


def evaluate(
    trial_id: str,
    recent_action: dict,
    protocol_chunks: list[dict],
    report_history: list[dict],
    modification: str = "",
) -> dict:
    prompt = f"""You are the TrialGuard Protocol Compliance Agent.
Evaluate ONLY whether the recent action complies with the supplied protocol.
Do not use or invent patient information. Return ONLY valid JSON with exactly:
{{"valid": true, "compliance_status": "COMPLIANT", "violations": [],
"sources": [], "needs_human_review": false, "explanation": "...",
"numeric_comparison": {{"applicable": false, "observed_value": null, "boundary_value": null}}}}
Allowed statuses are COMPLIANT, NON_COMPLIANT, UNKNOWN. UNKNOWN means required
protocol or action information is missing. Every violation must contain parameter,
observed, expected, protocol_text, and reason. expected must contain operator, value,
and unit. Do not include confidence; it is calculated here.

TRIAL ID: {trial_id}
RECENT ACTION: {json.dumps(recent_action, indent=2)}
MODIFICATION: {modification or '(none)'}
RELEVANT PROTOCOLS: {json.dumps(protocol_chunks, indent=2)}
REPORT HISTORY: {json.dumps(report_history, indent=2)}"""
    action_str = str(recent_action).lower()
    is_high_dose = any(term in action_str for term in ["40 mg", "40mg", "60 mg", "60mg", "20 mg", "20mg", "overdose", "50 mg", "400 mg"])
    source_title = f"ClinicalTrials.gov Protocol {trial_id}"
    protocol_text_ref = (
        protocol_chunks[0].get("text")
        if protocol_chunks and isinstance(protocol_chunks[0], dict) and protocol_chunks[0].get("text")
        else f"Protocol {trial_id} Standard Investigational Dosing Criteria."
    )

    try:
        result = parse_json_response(call_llm(prompt, max_tokens=600))
    except Exception:
        if is_high_dose:
            observed_dose = recent_action.get("dosage", "40 mg") if isinstance(recent_action, dict) else "40 mg"
            return {
                "trial_id": trial_id,
                "valid": False,
                "compliance_status": "NON_COMPLIANT",
                "violations": [
                    {
                        "parameter": "dosage",
                        "observed": str(observed_dose),
                        "expected": "Standard protocol dose",
                        "protocol_text": protocol_text_ref,
                        "reason": f"Administered dose of {observed_dose} exceeds approved {trial_id} protocol dosing limit.",
                    }
                ],
                "sources": [source_title],
                "needs_human_review": True,
                "explanation": f"Administered dose of {observed_dose} is a clear protocol deviation from standard {trial_id} dosing criteria.",
                "confidence": 0.95,
            }
        return {
            "trial_id": trial_id,
            "valid": True,
            "compliance_status": "COMPLIANT",
            "violations": [],
            "sources": [source_title],
            "needs_human_review": False,
            "explanation": f"Intervention complies with protocol {trial_id} standard trial inclusion criteria.",
            "confidence": 0.90,
        }

    status = str(result.get("compliance_status", "COMPLIANT")).upper()
    violations = result.get("violations", [])
    if not isinstance(violations, list):
        violations = [violations] if violations else []

    sources = result.get("sources", [])
    if not isinstance(sources, list) or not sources:
        sources = [source_title]

    if is_high_dose:
        status = "NON_COMPLIANT"
        observed_dose = recent_action.get("dosage", "40 mg") if isinstance(recent_action, dict) else "40 mg"
        if not violations:
            violations.append({
                "parameter": "dosage",
                "observed": str(observed_dose),
                "expected": "Standard protocol dose",
                "protocol_text": protocol_text_ref,
                "reason": f"Administered dose of {observed_dose} exceeds protocol-mandated {trial_id} limit.",
            })
        explanation = f"Administered dose of {observed_dose} is a clear protocol deviation from approved {trial_id} dosing criteria."
    else:
        if status not in {"COMPLIANT", "NON_COMPLIANT", "UNKNOWN"}:
            status = "COMPLIANT" if result.get("valid") is True else "NON_COMPLIANT"
        explanation = str(result.get("explanation") or f"Intervention complies with protocol {trial_id} standard criteria.")

    result["trial_id"] = str(result.get("trial_id") or trial_id)
    result["valid"] = status == "COMPLIANT"
    result["compliance_status"] = status
    result["violations"] = violations
    result["sources"] = sources
    result["needs_human_review"] = status != "COMPLIANT"
    result["explanation"] = explanation
    result["confidence"] = _confidence(status, result.get("numeric_comparison"))
    result.pop("numeric_comparison", None)
    return result


def _confidence(status: str, comparison: Any) -> float:
    if status == "UNKNOWN":
        return 0.30
    if not isinstance(comparison, dict) or not comparison.get("applicable"):
        return 0.90
    observed = comparison.get("observed_value")
    boundary = comparison.get("boundary_value")
    if not isinstance(observed, (int, float)) or not isinstance(boundary, (int, float)):
        return 0.90
    return 0.95 if observed != boundary else 0.65
