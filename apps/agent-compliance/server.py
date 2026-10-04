import os
import re
import json
import math
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI
from fastapi import FastAPI, Request

# ============================================================
# ENVIRONMENT RESOLUTION
# ============================================================
load_dotenv(find_dotenv(usecwd=True))
REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

KADO_API_KEY = os.environ.get("KADO_API_KEY") or os.environ.get("OPENAI_API_KEY")
KADO_BASE_URL = os.environ.get("KADO_BASE_URL", "https://awesome.kado.so/openai/v1")
KADO_MODEL = os.environ.get("KADO_MODEL", "kado")
KADO_TIMEOUT_SECONDS = int(os.environ.get("KADO_TIMEOUT_SECONDS", "30"))

if KADO_API_KEY:
    client = OpenAI(
        api_key=KADO_API_KEY,
        base_url=KADO_BASE_URL,
        default_headers={"x-bf-vk": KADO_API_KEY},
        max_retries=0,
    )
else:
    client = None


def _clean_json_text(text: str) -> str:
    """Robustly strips markdown fences and extracts raw JSON."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1].strip()
    return text


# ============================================================
# PROMPT BUILDER
# ============================================================

def _build_prompt(
    trial_id: str,
    recent_action: Any,
    protocol_chunks: List[Dict[str, Any]],
    report_history: List[Dict[str, Any]],
    modification: str = "",
) -> str:
    action_repr = (
        json.dumps(recent_action, indent=2)
        if isinstance(recent_action, dict)
        else json.dumps({"description": str(recent_action)}, indent=2)
    )

    modification_text = (
        modification.strip()
        if modification
        else "(No explicit modification instruction provided)"
    )

    return f"""You are the TrialGuard AI Protocol Compliance Agent.

Your ONLY responsibility is to determine whether the doctor's RECENT ACTION
complies with the supplied clinical trial PROTOCOL.

IMPORTANT:
- You do NOT receive patient medical data.
- Do NOT make patient-specific decisions.
- Do NOT evaluate age, sex, diagnoses, medications, allergies,
  laboratory values, medical history, toxicity, contraindications,
  or patient eligibility.
- Only compare the recent action against the supplied protocol text.
- If the prescribed dose, frequency, or route exceeds or violates the protocol text,
  set compliance_status to "NON_COMPLIANT", valid to false, and populate "violations".
- If the protocol requires patient-specific information, mark the result as
  UNKNOWN and request human review.

TRIAL ID:
{trial_id}

RECENT ACTION:
{action_repr}

MODIFICATION INSTRUCTION FROM DOCTOR:
{modification_text}

RELEVANT PROTOCOLS:
{json.dumps(protocol_chunks, indent=2)}

REPORT HISTORY:
{json.dumps(report_history, indent=2)}

How to use MODIFICATION INSTRUCTION and REPORT HISTORY:
- The MODIFICATION INSTRUCTION describes what the doctor intended to adjust.
- If REPORT HISTORY is empty, evaluate the RECENT ACTION fresh.
- If REPORT HISTORY is NOT empty, verify whether the current action and modification
  resolve the violations listed in previous iterations (e.g., dose reduction to <= 5 mg).
- Your "violations" output MUST reflect ONLY violations present in the CURRENT
  action being evaluated right now. Never copy forward past violations that have been resolved.

==================================================
REQUIRED OUTPUT FORMAT (STRICT JSON ONLY, NO CODE FENCES)
==================================================
{{
  "valid": boolean,
  "compliance_status": "COMPLIANT" | "NON_COMPLIANT" | "UNKNOWN",
  "violations": [
    {{
      "parameter": "string",
      "observed": "string",
      "expected": {{
        "operator": "string",
        "value": "string | number",
        "unit": "string"
      }},
      "protocol_text": "Exact relevant protocol text.",
      "reason": "Why the action violates the protocol."
    }}
  ],
  "sources": [
    {{
      "chunk_id": "string",
      "text": "Exact relevant protocol text.",
      "section": "string",
      "score": number
    }}
  ],
  "needs_human_review": boolean,
  "explanation": "Clinical justification...",
  "numeric_comparison": {{
    "applicable": boolean,
    "observed_value": float | null,
    "boundary_value": float | null
  }}
}}

NUMERIC COMPARISON REPORTING:
- Set "applicable" to true ONLY when the decision is based on comparing an observed numeric value against a protocol threshold.
- Otherwise, set "applicable" to false and values to null.
"""


# ============================================================
# CONFIDENCE CALCULATION (Deterministic, Not LLM-Reported)
# ============================================================

_CONFIDENCE_TAU = 0.05
_CONFIDENCE_AT_BOUNDARY = 0.65
_CONFIDENCE_CLEAR_CUT = 0.95
_CONFIDENCE_NON_NUMERIC = 0.90
_CONFIDENCE_UNKNOWN = 0.30


def _compute_confidence(compliance_status: str, numeric_comparison: Any) -> float:
    if compliance_status == "UNKNOWN":
        return _CONFIDENCE_UNKNOWN

    if not isinstance(numeric_comparison, dict):
        return _CONFIDENCE_NON_NUMERIC

    applicable = numeric_comparison.get("applicable")
    if not applicable:
        return _CONFIDENCE_NON_NUMERIC

    raw_obs = numeric_comparison.get("observed_value")
    raw_bnd = numeric_comparison.get("boundary_value")

    try:
        if raw_obs is None or raw_bnd is None:
            return _CONFIDENCE_NON_NUMERIC
        observed_value = float(raw_obs)
        boundary_value = float(raw_bnd)
    except (ValueError, TypeError):
        return _CONFIDENCE_NON_NUMERIC

    if boundary_value == 0:
        margin_ratio = abs(observed_value - boundary_value)
    else:
        margin_ratio = abs(observed_value - boundary_value) / abs(boundary_value)

    saturation = 1 - math.exp(-margin_ratio / _CONFIDENCE_TAU)
    confidence = _CONFIDENCE_AT_BOUNDARY + saturation * (_CONFIDENCE_CLEAR_CUT - _CONFIDENCE_AT_BOUNDARY)
    return round(confidence, 2)


def _build_final_result(result: dict, recent_action: Any, iteration: int = 1) -> dict:
    """Constructs the output adhering strictly to ComplianceVerdictRecord."""
    if "numeric_comparison" not in result or not isinstance(result["numeric_comparison"], dict):
        result["numeric_comparison"] = {"applicable": False, "observed_value": None, "boundary_value": None}

    result.pop("confidence", None)

    allowed_statuses = {"COMPLIANT", "NON_COMPLIANT", "UNKNOWN"}
    status = result.get("compliance_status")
    if status not in allowed_statuses:
        status = "UNKNOWN"

    computed_confidence = _compute_confidence(
        compliance_status=status,
        numeric_comparison=result.get("numeric_comparison"),
    )

    action_payload = (
        recent_action
        if isinstance(recent_action, dict)
        else {"drug": "investigational_agent", "description": str(recent_action), "raw_text": str(recent_action)}
    )

    return {
        "iteration": iteration,
        "compliance_status": status,
        "valid": bool(result.get("valid", status == "COMPLIANT")),
        "confidence": computed_confidence,
        "violations": result.get("violations", []),
        "explanation": str(result.get("explanation", "")),
        "sources": result.get("sources", []),
        "prescribed_action": action_payload,
        "needs_human_review": bool(result.get("needs_human_review", status != "COMPLIANT")),
    }


# ============================================================
# COMPLIANCE EVALUATION ENTRYPOINT
# ============================================================

def _evaluate(
    trial_id: str,
    recent_action: Any,
    protocol_chunks: list,
    report_history: list,
    modification: str = "",
    iteration: Optional[int] = None,
) -> dict:
    effective_iteration = iteration if iteration is not None else (len(report_history) + 1)

    try:
        if not client:
            raise RuntimeError("Neither KADO_API_KEY nor OPENAI_API_KEY is configured.")
        prompt = _build_prompt(
            trial_id=trial_id,
            recent_action=recent_action,
            protocol_chunks=protocol_chunks,
            report_history=report_history,
            modification=modification,
        )

        response = client.chat.completions.create(
            model=KADO_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are the TrialGuard Protocol Compliance Agent. "
                        "Return only valid JSON conforming strictly to the requested schema. "
                        "Do not return markdown. Do not return code fences."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            timeout=KADO_TIMEOUT_SECONDS,
        )

        if not response.choices:
            raise ValueError("Model returned no choices.")

        content = response.choices[0].message.content
        if not content:
            raise ValueError(f"Model returned empty response. Finish reason: {response.choices[0].finish_reason}")

        clean_text = _clean_json_text(content)
        result = json.loads(clean_text)

        return _build_final_result(
            result=result,
            recent_action=recent_action,
            iteration=effective_iteration,
        )

    except Exception as e:
        status_code = getattr(e, "status_code", None)
        if status_code in (401, 403):
            print(f"[compliance_server] Kado gateway auth failure ({status_code}): {e}")

        action_payload = (
            recent_action
            if isinstance(recent_action, dict)
            else {"drug": "investigational_agent", "description": str(recent_action), "raw_text": str(recent_action)}
        )
        return {
            "iteration": effective_iteration,
            "compliance_status": "UNKNOWN",
            "valid": False,
            "confidence": 0.0,
            "violations": [],
            "explanation": f"Compliance assessment could not be completed: {str(e)}",
            "sources": [],
            "prescribed_action": action_payload,
            "needs_human_review": True,
        }


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(title="TrialGuard Compliance Agent Service")


@app.get("/.well-known/agent-card.json")
def get_agent_card():
    return {
        "name": "TrialGuard Compliance Agent",
        "description": "Evaluates clinical trial protocol compliance and dosing guidelines.",
        "version": "1.0.0",
        "protocols": ["a2a", "jsonrpc-2.0"],
        "capabilities": ["evaluate_compliance", "SendMessage"],
    }


@app.post("/")
@app.post("/rpc")
async def handle_rpc(request: Request):
    try:
        body = await request.json()
    except Exception:
        return {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}

    req_id = body.get("id")
    method = body.get("method", "")
    params = body.get("params", {})

    is_a2a_send_message = (method == "SendMessage")
    if is_a2a_send_message:
        message = params.get("message", {}) if isinstance(params, dict) else {}
        parts = message.get("parts", [])
        text_payload = parts[0].get("text", "{}") if parts else "{}"
        try:
            call_params = json.loads(text_payload)
        except json.JSONDecodeError:
            call_params = {}
    elif method == "evaluate_compliance":
        call_params = params if isinstance(params, dict) else {}
    else:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": f"Unknown method: {method}"},
            "id": req_id,
        }

    # Strict PHI Guardrail Verification
    prohibited_keys = {"patient_id", "patient", "patient_data", "dob", "ssn"}
    found_prohibited = prohibited_keys.intersection(set(call_params.keys()))
    if found_prohibited:
        err_msg = f"PHI Guardrail Violation: Prohibited demographic keys detected: {list(found_prohibited)}"
        error_result = {
            "iteration": call_params.get("iteration", 1),
            "compliance_status": "UNKNOWN",
            "valid": False,
            "confidence": 0.0,
            "violations": [],
            "explanation": err_msg,
            "sources": [],
            "prescribed_action": None,
            "needs_human_review": True,
        }
        if is_a2a_send_message:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "task": {
                        "id": str(uuid.uuid4()),
                        "status": {"state": "TASK_STATE_FAILED"},
                        "artifacts": [
                            {
                                "name": "compliance_error",
                                "parts": [{"text": json.dumps(error_result), "media_type": "application/json"}],
                            }
                        ],
                    }
                },
            }
        return {"jsonrpc": "2.0", "result": error_result, "id": req_id}

    trial_id = call_params.get("trial_id", "")
    recent_action = call_params.get("recent_action") or call_params.get("prescribed_action", {})
    protocol_chunks = call_params.get("relevant_protocols") or call_params.get("protocol_chunks", [])
    report_history = call_params.get("report_history", [])
    modification = call_params.get("modification", "")
    iteration = call_params.get("iteration")

    result = _evaluate(
        trial_id=trial_id,
        recent_action=recent_action,
        protocol_chunks=protocol_chunks,
        report_history=report_history,
        modification=modification,
        iteration=iteration,
    )

    if is_a2a_send_message:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "task": {
                    "id": str(uuid.uuid4()),
                    "status": {"state": "TASK_STATE_COMPLETED"},
                    "artifacts": [
                        {
                            "name": "compliance_result",
                            "parts": [{"text": json.dumps(result), "media_type": "application/json"}],
                        }
                    ],
                }
            },
        }

    return {"jsonrpc": "2.0", "result": result, "id": req_id}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("COMPLIANCE_FASTAPI_PORT", 8001))
    print(f"--> Compliance agent binding on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)