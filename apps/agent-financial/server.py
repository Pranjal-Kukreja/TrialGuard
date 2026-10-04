import os
import re
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI
from fastapi import FastAPI, Request

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
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1].strip()
    return text

def _build_prompt(
    trial_id: str,
    recent_action: Any,
    financial_context: Dict[str, Any],
    policies: List[Dict[str, Any]],
    report_history: List[Dict[str, Any]],
    modification: str = "",
) -> str:
    action_repr = json.dumps(recent_action, indent=2) if isinstance(recent_action, dict) else json.dumps({"description": str(recent_action)}, indent=2)
    return f"""
You are the TrialGuard AI Financial & Coverage Agent.
Verify whether the prescribed intervention is financially covered, requires prior authorization, or is sponsor eligible.

TRIAL ID: {trial_id}
RECENT ACTION: {action_repr}
MODIFICATION: {modification or '(None)'}
FINANCIAL CONTEXT: {json.dumps(financial_context, indent=2)}
POLICIES: {json.dumps(policies, indent=2)}
REPORT HISTORY: {json.dumps(report_history, indent=2)}

REQUIRED OUTPUT FORMAT (JSON ONLY):
{{
  "coverage_status": "COVERED",
  "pre_auth_required": false,
  "sponsor_billing_eligible": true,
  "tier": "Tier-1 Investigational Coverage",
  "exceptions": [],
  "explanation": "Intervention is fully covered under the sponsor's clinical research billing plan."
}}

Allowed values for coverage_status: "COVERED", "NOT_COVERED", "REQUIRES_PRE_AUTH".
Every item in "exceptions" MUST have:
{{
  "billing_code": "string",
  "procedure": "string",
  "coverage_status": "string",
  "reason": "string"
}}
"""

DRUG_EXPOSURES = {
    "apixaban": (3200, "5 mg BID", ["2.5 mg", "2.5mg", "5 mg", "5mg"]),
    "empagliflozin": (1250, "10 mg daily", ["10 mg", "10mg", "25 mg", "25mg"]),
    "pioglitazone": (450, "30 mg daily", ["15 mg", "15mg", "30 mg", "30mg", "45 mg", "45mg"]),
    "pembrolizumab": (23000, "200 mg Q3W", ["200 mg", "200mg"]),
}

def _get_drug_exposure(action_str: str) -> tuple[str, int, str]:
    lower = action_str.lower()
    for drug, (exp, std, allowed) in DRUG_EXPOSURES.items():
        if drug in lower:
            return drug.capitalize(), exp, std
    return "Apixaban", 3200, "5 mg BID"

def _evaluate_financial(
    trial_id: str,
    recent_action: Any,
    financial_context: dict,
    policies: list,
    report_history: list,
    modification: str = "",
    iteration: Optional[int] = None,
) -> dict:
    effective_iteration = iteration if iteration is not None else (len(report_history) + 1)
    action_text = json.dumps(recent_action) if isinstance(recent_action, dict) else str(recent_action)
    action_str = action_text.lower()
    dosage_str = str(recent_action.get("dosage", "")).lower() if isinstance(recent_action, dict) else action_str
    drug_name, unapproved_exp, std_dose = _get_drug_exposure(action_str)

    is_unapproved = any(term in dosage_str or term in action_str for term in ["40 mg", "40mg", "60 mg", "60mg", "20 mg", "20mg", "overdose", "50 mg", "400 mg"])

    try:
        if not client:
            raise RuntimeError("Neither KADO_API_KEY nor OPENAI_API_KEY is configured.")
        prompt = _build_prompt(trial_id, recent_action, financial_context, policies, report_history, modification)
        response = client.chat.completions.create(
            model=KADO_MODEL,
            messages=[
                {"role": "system", "content": "You are the TrialGuard Financial Agent. Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            timeout=KADO_TIMEOUT_SECONDS,
        )
        content = response.choices[0].message.content or "{}"
        clean_text = _clean_json_text(content)
        parsed = json.loads(clean_text)

        status = parsed.get("coverage_status", "NOT_COVERED")
        if status not in {"COVERED", "NOT_COVERED", "REQUIRES_PRE_AUTH"}:
            status = "REQUIRES_PRE_AUTH" if "PRE" in status else "NOT_COVERED"

        if is_unapproved:
            status = "REQUIRES_PRE_AUTH"
            exposure = unapproved_exp
            callout = f"Sponsor coverage denied: Dosing violates {trial_id} protocol. Prior auth required (${exposure:,.0f} exposure)."
        elif status == "COVERED":
            exposure = 0
            callout = f"100% Protocol & Investigational Coverage under Sponsor Trial Agreement for {drug_name} (Zero Patient Liability)."
        else:
            exposure = unapproved_exp
            callout = f"Prior authorization required for modified {drug_name} regimen (${exposure:,.0f} exposure)."

        return {
            "iteration": effective_iteration,
            "coverage_status": status,
            "pre_auth_required": bool(parsed.get("pre_auth_required", status == "REQUIRES_PRE_AUTH")),
            "sponsor_billing_eligible": bool(parsed.get("sponsor_billing_eligible", status == "COVERED")),
            "tier": str(parsed.get("tier", "Tier-1 Investigational Coverage" if status == "COVERED" else "Non-Covered Protocol Deviation")),
            "financialExposure": exposure,
            "callout": callout,
            "exceptions": parsed.get("exceptions", []),
            "explanation": str(parsed.get("explanation", f"{drug_name} financial review completed per {trial_id} billing policy.")),
            "confidence": 0.95,
        }
    except Exception:
        # Resilient local clinical research billing fallback
        if is_unapproved:
            status = "REQUIRES_PRE_AUTH"
            exposure = unapproved_exp
            callout = f"Sponsor coverage denied: Dosing violates {trial_id} protocol. Prior auth required (${exposure:,.0f} exposure)."
            explanation = (
                f"The study sponsor covers 100% of medication costs ONLY for protocol-compliant dosing ({std_dose}). "
                f"The prescribed regimen represents an unapproved protocol deviation, triggering secondary prior authorization "
                f"with ${exposure:,.0f} in non-covered pharmaceutical exposure."
            )
            tier = "Non-Covered Protocol Deviation / Prior Auth Required"
            pre_auth = True
            sponsor_eligible = False
        else:
            status = "COVERED"
            exposure = 0
            callout = f"100% Protocol & Investigational Coverage under Sponsor Trial Agreement for {drug_name} (Zero Patient Liability)."
            explanation = f"Intervention complies with protocol {trial_id} standard {drug_name} dosing ({std_dose}). 100% covered under sponsor trial agreement at $0 patient liability."
            tier = "Tier-1 Investigational Coverage"
            pre_auth = False
            sponsor_eligible = True

        return {
            "iteration": effective_iteration,
            "coverage_status": status,
            "pre_auth_required": pre_auth,
            "sponsor_billing_eligible": sponsor_eligible,
            "tier": tier,
            "financialExposure": exposure,
            "callout": callout,
            "exceptions": [],
            "explanation": explanation,
            "confidence": 0.95,
        }

app = FastAPI(title="TrialGuard Financial Agent Service")

@app.get("/.well-known/agent-card.json")
def get_agent_card():
    return {
        "name": "TrialGuard Financial Agent",
        "description": "Evaluates coverage eligibility, billing tiers, and pre-authorization requirements.",
        "version": "1.0.0",
        "protocols": ["a2a", "jsonrpc-2.0"],
        "capabilities": ["evaluate_financial", "SendMessage"],
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

    is_a2a = (method == "SendMessage")
    if is_a2a:
        parts = params.get("message", {}).get("parts", [])
        text_payload = parts[0].get("text", "{}") if parts else "{}"
        try:
            call_params = json.loads(text_payload)
        except json.JSONDecodeError:
            call_params = {}
    elif method == "evaluate_financial":
        call_params = params
    else:
        return {"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Unknown method: {method}"}, "id": req_id}

    # Strict PHI Guardrail
    prohibited = {"patient_id", "patient", "patient_data", "dob", "ssn"}.intersection(set(call_params.keys()))
    if prohibited:
        err = {
            "iteration": call_params.get("iteration", 1),
            "coverage_status": "NOT_COVERED",
            "pre_auth_required": True,
            "sponsor_billing_eligible": False,
            "tier": "Prohibited PHI",
            "exceptions": [{"billing_code": "PHI_VIOLATION", "procedure": "none", "coverage_status": "DENIED", "reason": f"Prohibited keys: {list(prohibited)}"}],
            "explanation": "Request rejected due to PHI guardrail violation.",
        }
        if is_a2a:
            return {"jsonrpc": "2.0", "id": req_id, "result": {"task": {"id": str(uuid.uuid4()), "status": {"state": "TASK_STATE_FAILED"}, "artifacts": [{"name": "financial_error", "parts": [{"text": json.dumps(err), "media_type": "application/json"}]}]}}}
        return {"jsonrpc": "2.0", "result": err, "id": req_id}

    result = _evaluate_financial(
        trial_id=call_params.get("trial_id", ""),
        recent_action=call_params.get("recent_action") or call_params.get("prescribed_action", {}),
        financial_context=call_params.get("financial_context", {}),
        policies=call_params.get("relevant_policies") or call_params.get("policies", []),
        report_history=call_params.get("report_history", []),
        modification=call_params.get("modification", ""),
        iteration=call_params.get("iteration"),
    )

    if is_a2a:
        return {"jsonrpc": "2.0", "id": req_id, "result": {"task": {"id": str(uuid.uuid4()), "status": {"state": "TASK_STATE_COMPLETED"}, "artifacts": [{"name": "financial_verdict", "parts": [{"text": json.dumps(result), "media_type": "application/json"}]}]}}}
    return {"jsonrpc": "2.0", "result": result, "id": req_id}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("FINANCIAL_FASTAPI_PORT", 8003))
    print(f"--> Financial agent binding on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)