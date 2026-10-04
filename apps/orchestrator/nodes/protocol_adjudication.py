"""Protocol Adjudication Node for Clinical Trial Evaluation.

Evaluates:
  - Patient EHR profiles and medical history against protocol criteria.
  - Synthesizes findings from upstream RAG analysis (RagAnalysisOutput).
  - Normalizes semantic criteria records (violations, matched, unknown).
  - Emits candidate evaluation records for multi-agent convergence.
  - Deterministic protocol fallback when Kado proxy gateway times out.
"""

import asyncio
import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional

from apps.orchestrator.schemas.eligibility_output import LLMProtocolEvaluation
from dotenv import find_dotenv, load_dotenv
import httpx
from langchain_openai import ChatOpenAI
from shared_schemas.state import TrialState

load_dotenv(find_dotenv(usecwd=True))

logger = logging.getLogger(__name__)


def get_kado_client() -> ChatOpenAI:
    """Instantiates the Kado OpenAI chat client with resilient HTTP transport."""
    api_key = os.getenv("KADO_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            f"OPENAI_API_KEY / KADO_API_KEY is missing from environment. (CWD: {os.getcwd()})"
        )

    base_url = os.getenv("KADO_BASE_URL", "https://awesome.kado.so/openai/v1")
    model_name = os.getenv("KADO_MODEL", "kado")

    # Resilient socket connection and read limits to handle proxy latency
    # Kado's gateway requires the credential in this dedicated header, not
    # the SDK's default Authorization bearer token -- omitting it causes
    # every request to fail with "401 virtual_key_required". This mirrors
    # the identical fix already applied in safety_server.py / financial_server.py.
    custom_sync_client = httpx.Client(
        timeout=httpx.Timeout(connect=15.0, read=90.0, write=30.0, pool=10.0),
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        headers={"x-bf-vk": api_key},
    )
    custom_async_client = httpx.AsyncClient(
        timeout=httpx.Timeout(connect=15.0, read=90.0, write=30.0, pool=10.0),
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        headers={"x-bf-vk": api_key},
    )

    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0.0,
        http_client=custom_sync_client,
        http_async_client=custom_async_client,
        default_headers={"x-bf-vk": api_key},
    )


def extract_json_payload(text: str) -> str:
    """Robustly strips markdown fences from LLM responses."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1].strip()
    return text


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
    return str(action or "")


def _extract_numeric_dose(action_str: str) -> Optional[float]:
    match = re.search(r"(\d+(?:\.\d+)?)\s*mg", action_str.lower())
    if match:
        try:
            return float(match.group(1))
        except (ValueError, TypeError):
            pass
    return None


def _deterministic_adjudication_fallback(
    proposed_action: str, patient: Dict[str, Any], modification: Optional[str] = None
) -> Dict[str, Any]:
    """Deterministic protocol fallback triggered when Kado proxy gateway times out."""
    action_str = proposed_action.lower()
    violations: List[Dict[str, Any]] = []
    matched: List[Dict[str, Any]] = []

    dose_val = _extract_numeric_dose(action_str)

    # Rule 1: Protocol Max Single Dose Ceiling (5.0 mg)
    if dose_val is not None and dose_val > 5.0:
        violations.append({
            "rule_id": "NCT02415400_DOSE_LIMIT",
            "parameter": "dosage",
            "observed": f"{dose_val} mg",
            "expected": "<= 5.0 mg single dose",
            "severity": "HARD",
            "reason": f"Prescribed dose ({dose_val} mg) exceeds protocol maximum allowed single dose of 5 mg.",
        })
    elif dose_val is not None:
        matched.append({
            "rule_id": "NCT02415400_DOSE_LIMIT",
            "criterion": f"Prescribed single dose {dose_val} mg within allowed threshold (<= 5.0 mg)",
            "result": "PASSED",
        })

    # Rule 2: Protocol Mandatory Frequency (BID / Twice Daily)
    is_once_daily = any(q in action_str for q in ["once daily", "qd", "daily", "once a day"]) and not any(
        q in action_str for q in ["twice", "bid", "2x", "two times"]
    )
    if is_once_daily:
        violations.append({
            "rule_id": "NCT02415400_FREQ_LIMIT",
            "parameter": "frequency",
            "observed": "once daily",
            "expected": "twice daily",
            "severity": "HARD",
            "reason": "Protocol mandates twice-daily scheduling for therapeutic stroke prevention.",
        })
    else:
        matched.append({
            "rule_id": "NCT02415400_FREQ_LIMIT",
            "criterion": "Twice daily scheduling compliant with stroke prevention protocol",
            "result": "PASSED",
        })

    is_compliant = len(violations) == 0
    verdict = "APPROVED" if is_compliant else "REJECTED"
    eligibility = "ELIGIBLE" if is_compliant else "INELIGIBLE"
    summary = (
        f"Deterministic fallback evaluation: Prescribed action '{proposed_action}' satisfies protocol dosing parameters."
        if is_compliant
        else violations[0]["reason"]
    )

    evaluation_dict = {
        "verdict": verdict,
        "confidence": 0.90,
        "summary": summary,
        "violations": violations,
        "matched_criteria": matched,
        "unknown_criteria": [],
        "adjudication_violations": violations,
    }

    return {
        "evaluation": evaluation_dict,
        "decision": verdict,
        "eligibility": eligibility,
        "confidence": 0.90,
        "explanation": summary,
        "matched_criteria": matched,
        "unknown_criteria": [],
        "audit_logs": [
            {
                "step": "protocol_adjudication",
                "model": "offline_deterministic_fallback",
                "status": "completed",
                "verdict": verdict,
                "confidence": 0.90,
                "violations_count": len(violations),
            }
        ],
    }


def build_clinical_prompt(
    patient: Dict[str, Any],
    evidence: Any,
    proposed_action: str,
    rag_analysis: Optional[Dict[str, Any]] = None,
    modification: Optional[str] = None,
) -> str:
    narrative = patient.get("medical_history_narrative", "None documented.")
    facts = patient.get("protocol_facts", {})

    rag_section = (
        f"""
================================================================================
SYNTHESIZED RAG PROTOCOL & SAFETY ANALYSIS (GROUND TRUTH EVIDENCE):
{json.dumps(rag_analysis, default=str, indent=2)}
================================================================================
"""
        if rag_analysis
        else ""
    )

    modification_section = (
        f"""
================================================================================
CLINICIAN MODIFICATION RATIONALE (HITL FEEDBACK):
{modification}
================================================================================
"""
        if modification
        else ""
    )

    schema_sample = json.dumps(LLMProtocolEvaluation.model_json_schema(), indent=2)

    return f"""You are a board-certified Clinical Protocol Safety Adjudicator for TrialGuard.
Evaluate the patient's baseline EHR profile, protocol facts, and upstream RAG analysis to adjudicate the PROPOSED CLINICAL ACTION.

================================================================================
PROPOSED CLINICAL ACTION TO ADJUDICATE:
"{proposed_action}"
================================================================================
{modification_section}
{rag_section}
CLINICAL NARRATIVE OVERVIEW:
{narrative}

GROUND PROTOCOL FACTS:
{json.dumps(facts, default=str, indent=2)}

Adjudication Directives:
1. PRIMARY ACTION SAFETY & COMPLIANCE AUDIT:
   - Evaluate the safety of the PROPOSED CLINICAL ACTION against patient organ clearance (eGFR, CrCl, AST/ALT, total bilirubin) and baseline bleeding parameters (INR, platelets, hemoglobin).
   - If the upstream RAG analysis identifies protocol violations (e.g., dose > 5 mg daily ceiling, PCI timing > 14 days), evaluate whether the proposed action resolves them.
2. Cross-reference all medical history, diagnostic codes, lab results, vitals, and active medications against protocol exclusion clauses and washout intervals.
3. Categorize criteria into:
   - violations: Explicit protocol criteria breaches, dosing ceiling deviations, or hazardous contraindications.
   - matched_criteria: Confirmed safe baseline inclusion criteria.
   - unknown_criteria: Unmonitored safety risks, missing diagnostic workups, or clinical safety ambiguities arising from the proposed action.
4. Decision Directives:
   - 'REJECTED': Hard contraindication, severe safety hazard, or unresolvable protocol breach (confidence >= 0.85).
   - 'NEEDS_REVIEW': Non-fatal deviations, clinical trade-offs requiring clinician discretion, or missing safety monitoring.
   - 'APPROVED': Proposed action and baseline profile are verified completely compliant and safe (confidence >= 0.85).
5. Output valid JSON strictly conforming to this schema:
{schema_sample}

[FULL PATIENT RECORD]
{json.dumps(patient, default=str, indent=2)}

[EXTRACTED PROTOCOL CRITERIA & EVIDENCE]
{json.dumps(evidence, default=str, indent=2)}
"""


def _invoke_kado_with_retry(
    llm: ChatOpenAI, prompt: str, max_retries: int = 2
) -> LLMProtocolEvaluation:
    messages = [
        (
            "system",
            "You are an expert clinical trial adjudication engine. Adjudicate"
            " patient safety and protocol compliance with high medical precision."
            " Output strict JSON conforming to the schema.",
        ),
        ("user", prompt),
    ]

    backoff = 1.0
    for attempt in range(max_retries):
        try:
            response = llm.invoke(messages)
            content = str(response.content).strip()
            clean_json = extract_json_payload(content)
            return LLMProtocolEvaluation.model_validate_json(clean_json)
        except Exception as exc:
            if attempt < max_retries - 1:
                logger.warning(
                    "Kado inference error (%s). Retrying in %.2fs (Attempt %d/%d)...",
                    str(exc)[:60],
                    backoff,
                    attempt + 1,
                    max_retries,
                )
                time.sleep(backoff)
                backoff = min(backoff * 2.0, 3.0)
            else:
                raise exc


def protocol_adjudication_node(state: TrialState) -> Dict[str, Any]:
    """Executes deep semantic protocol evaluation against RAG and EHR data."""
    patient = state.get("patient") or state.get("raw_fhir_patient") or {}
    evidence = state.get("evidence") or []
    rag_analysis = state.get("rag_analysis") or {}
    modification = state.get("modification")

    raw_action = (
        state.get("prescribed_action")
        or state.get("proposed_action")
        or state.get("query")
        or rag_analysis.get("prescribed_action")
        or ""
    )
    proposed_action = _normalize_action_str(raw_action)

    prompt = build_clinical_prompt(
        patient=patient,
        evidence=evidence,
        proposed_action=proposed_action,
        rag_analysis=rag_analysis,
        modification=modification,
    )

    try:
        llm = get_kado_client()
        parsed = _invoke_kado_with_retry(llm, prompt)
    except Exception as exc:
        logger.warning(
            "Kado inference gateway unavailable (%s). Engaging deterministic protocol fallback.",
            str(exc)[:80],
        )
        return _deterministic_adjudication_fallback(
            proposed_action=proposed_action,
            patient=patient,
            modification=modification,
        )

    # Isolate newly emitted LLM findings safely
    existing_rule_ids = {
        v.get("rule_id") for v in state.get("violations", []) if isinstance(v, dict)
    }
    new_violations = [
        (v if isinstance(v, dict) else v.model_dump())
        for v in parsed.violations
        if getattr(v, "rule_id", (v.get("rule_id") if isinstance(v, dict) else None)) not in existing_rule_ids
    ]

    existing_unknown_ids = {
        u.get("rule_id") for u in state.get("unknown_criteria", []) if isinstance(u, dict)
    }
    new_unknowns = [
        (u if isinstance(u, dict) else u.model_dump())
        for u in parsed.unknown_criteria
        if getattr(u, "rule_id", (u.get("rule_id") if isinstance(u, dict) else None)) not in existing_unknown_ids
    ]

    existing_matched_ids = {
        m.get("rule_id") for m in state.get("matched_criteria", []) if isinstance(m, dict)
    }
    new_matched = [
        (m if isinstance(m, dict) else m.model_dump())
        for m in parsed.matched_criteria
        if getattr(m, "rule_id", (m.get("rule_id") if isinstance(m, dict) else None)) not in existing_matched_ids
    ]

    model_verdict = getattr(parsed, "verdict", "").upper()
    confidence = getattr(parsed, "confidence", 0.95)

    # Deterministic Safety Backstop on Unmonitored Therapy
    action_lower = proposed_action.lower()
    is_unmonitored = "without" in action_lower and any(
        kw in action_lower for kw in ["monitoring", "follow-up", "surveillance", "panel"]
    )
    if is_unmonitored:
        logger.warning(
            "Deterministic safety backstop triggered on unmonitored action: %s",
            proposed_action,
        )
        new_unknowns.append({
            "rule_id": "UNMONITORED_HIGH_RISK_THERAPY",
            "criterion": "clinical_safety_monitoring_schedule",
            "result": "UNKNOWN",
            "reason": (
                "Proposed action initiates or modifies high-potency antithrombotic"
                f" therapy while omitting essential safety surveillance: '{proposed_action}'"
            ),
        })
        model_verdict = "NEEDS_REVIEW"
        confidence = min(confidence, 0.65)

    # Determine Adjudication Decision
    total_violations_exist = (len(state.get("violations", [])) + len(new_violations)) > 0
    total_unknowns_exist = (len(state.get("unknown_criteria", [])) + len(new_unknowns)) > 0

    if model_verdict in ("REJECTED", "FAIL") or total_violations_exist:
        verdict = "REJECTED"
        eligibility = "INELIGIBLE"
    elif model_verdict in ("NEEDS_REVIEW", "INDETERMINATE") or total_unknowns_exist:
        verdict = "NEEDS_REVIEW"
        eligibility = "PENDING_CLINICIAN_REVIEW"
    else:
        verdict = "APPROVED"
        eligibility = "ELIGIBLE"

    audit_entry = {
        "step": "protocol_adjudication",
        "model": "kado",
        "status": "completed",
        "verdict": verdict,
        "confidence": confidence,
        "new_violations_count": len(new_violations),
        "new_matched_count": len(new_matched),
        "new_unknowns_count": len(new_unknowns),
    }

    evaluation_dict = parsed.model_dump()
    evaluation_dict["verdict"] = verdict
    evaluation_dict["confidence"] = confidence
    evaluation_dict["adjudication_violations"] = new_violations

    return {
        "evaluation": evaluation_dict,
        "decision": verdict,
        "eligibility": eligibility,
        "confidence": confidence,
        "explanation": parsed.summary,
        "matched_criteria": new_matched,
        "unknown_criteria": new_unknowns,
        "audit_logs": [audit_entry],
    }