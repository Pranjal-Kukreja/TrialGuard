import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
import requests

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parents[1]

try:
    from dotenv import find_dotenv, load_dotenv
    load_dotenv(find_dotenv(usecwd=True))
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

HOST = os.environ.get("A2A_HOST", "127.0.0.1")
PORT = int(os.environ.get("FINANCIAL_FASTAPI_PORT", "8003"))
A2A_URL = os.environ.get("A2A_FINANCIAL_URL", f"http://{HOST}:{PORT}/").replace("://0.0.0.0:", "://127.0.0.1:")


def run_financial_test(financial_input: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatches JSON-RPC payload to the Financial A2A server and extracts result."""
    task_id = str(uuid.uuid4())
    payload = {
        "jsonrpc": "2.0",
        "id": task_id,
        "method": "SendMessage",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "ROLE_USER",
                "parts": [{"text": json.dumps(financial_input)}],
            }
        },
    }

    try:
        response = requests.post(
            A2A_URL,
            json=payload,
            headers={"Content-Type": "application/json", "A2A-Version": "1.0"},
            timeout=60,
        )
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            f"Unable to connect to Financial A2A server at {A2A_URL}. "
            "Ensure 'python apps/agent-financial/server.py' is running."
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"A2A server returned HTTP {response.status_code}: {response.text}"
        )

    try:
        a2a_response = response.json()
    except ValueError:
        raise ValueError(f"A2A server returned non-JSON response: {response.text}")

    if "error" in a2a_response:
        raise RuntimeError(json.dumps(a2a_response["error"], indent=2))

    result = a2a_response.get("result")
    if not result:
        raise ValueError("A2A response does not contain 'result'.")

    task = result.get("task")
    if not task:
        raise ValueError("A2A response does not contain 'result.task'.")

    task_state = task.get("status", {}).get("state")
    artifacts = task.get("artifacts", [])

    financial_result: Optional[Dict[str, Any]] = None
    for artifact in artifacts:
        for part in artifact.get("parts", []):
            text = part.get("text")
            if not text:
                continue
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict) and ("coverage_status" in parsed or "error" in parsed):
                    financial_result = parsed
                    break
            except json.JSONDecodeError:
                continue
        if financial_result is not None:
            break

    if financial_result is None:
        raise ValueError(
            f"No valid financial result or error found in task artifacts (Task State: {task_state})."
        )

    print(json.dumps(financial_result, indent=2))
    return financial_result


# TEST 1: Initial evaluation (Standard Trial Investigational Coverage -> COVERED)
test_1_input = {
    "trial_id": "NCT02415400",
    "iteration": 1,
    "recent_action": {
        "drug": "apixaban",
        "dosage": "5 mg",
        "frequency": "twice daily",
        "route": "oral",
        "raw_text": "Apixaban 5 mg oral twice daily",
    },
    "financial_context": {
        "payer_id": "SPONSOR_TRIAL_EXPENSE",
        "insurance_plan": "Clinical Study Core Grant",
        "coverage_tier": "Tier-1 Investigational",
        "has_preauth": False,
    },
    "relevant_policies": [
        {
            "policy_id": "sponsor-grant-billing-01",
            "section": "Section 4.1 investigational medication supply",
            "text": (
                "The study sponsor covers 100% of study-mandated medications, "
                "including oral anticoagulants (apixaban) supplied for protocol arms."
            ),
        }
    ],
    "report_history": [],
}

# TEST 2: Off-label / Non-covered drug requiring prior auth
test_2_input = {
    "trial_id": "NCT02415400",
    "iteration": 1,
    "recent_action": {
        "drug": "edoxaban",
        "dosage": "60 mg",
        "frequency": "once daily",
        "route": "oral",
        "raw_text": "Prescribe off-study Edoxaban 60 mg oral once daily",
    },
    "financial_context": {
        "payer_id": "COMMERCIAL_PAYER_BCBS",
        "insurance_plan": "Standard Commercial HMO",
        "coverage_tier": "Non-Formulary",
        "has_preauth": False,
    },
    "relevant_policies": [
        {
            "policy_id": "payer-policy-pharm-99",
            "section": "Section 8 Prior Authorization Criteria",
            "text": (
                "Non-formulary Factor Xa inhibitors like Edoxaban require formal prior authorization "
                "and documented intolerance to protocol-preferred formulary agents before coverage approval."
            ),
        }
    ],
    "report_history": [],
}

# TEST 3: Contract Guardrail (patient_id or patient demographic rejection)
test_3_prohibited_patient_id = {
    "trial_id": "NCT02415400",
    "patient_id": "P001",
    "recent_action": {
        "drug": "apixaban",
        "dosage": "5 mg",
    },
    "financial_context": {
        "payer_id": "SPONSOR_TRIAL_EXPENSE",
    },
    "relevant_policies": [],
    "report_history": [],
}

test_3_prohibited_patient_data = {
    "trial_id": "NCT02415400",
    "patient": {
        "dob": "1964-08-12",
        "ssn": "000-12-3456",
    },
    "recent_action": "apixaban 5mg BID",
    "financial_context": {},
    "relevant_policies": [],
}


if __name__ == "__main__":
    print(f"Targeting Financial A2A Endpoint: {A2A_URL}\n")

    print("============================================================")
    print("RUNNING TEST 1: Initial Pass (Trial Covered Drug -> COVERED)")
    print("============================================================")
    res1 = run_financial_test(test_1_input)
    assert res1.get("coverage_status") == "COVERED", f"Test 1 failed! Got: {res1.get('coverage_status')}"
    assert res1.get("iteration") == 1, "Test 1 expected iteration=1"
    print("--> Test 1 Passed: Correctly approved investigational coverage.\n")

    print("============================================================")
    print("RUNNING TEST 2: Off-Label Drug -> REQUIRES_PRE_AUTH / NOT_COVERED")
    print("============================================================")
    res2 = run_financial_test(test_2_input)
    assert res2.get("coverage_status") in ("REQUIRES_PRE_AUTH", "NOT_COVERED", "REQUIRES_PREAUTH", "DENIED"), f"Test 2 failed! Got: {res2.get('coverage_status')}"
    print("--> Test 2 Passed: Correctly identified prior-auth requirement/denial.\n")

    print("============================================================")
    print("RUNNING TEST 3A: Contract Guardrail (patient_id Rejection)")
    print("============================================================")
    res3a = run_financial_test(test_3_prohibited_patient_id)
    assert "error" in res3a or res3a.get("coverage_status") == "NOT_COVERED" or "PHI" in res3a.get("explanation", ""), "Test 3A failed to trigger guardrail!"
    print("--> Test 3A Passed: Rejected prohibited 'patient_id'.\n")

    print("============================================================")
    print("RUNNING TEST 3B: Contract Guardrail (patient demographic Rejection)")
    print("============================================================")
    res3b = run_financial_test(test_3_prohibited_patient_data)
    assert "error" in res3b or res3b.get("coverage_status") == "NOT_COVERED" or "PHI" in res3b.get("explanation", ""), "Test 3B failed to trigger guardrail!"
    print("--> Test 3B Passed: Rejected prohibited 'patient' demographic object.\n")

    print("=" * 60)
    print("All Financial Agent integration tests on A2A server passed successfully!")
    print("=" * 60)