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
PORT = int(os.environ.get("COMPLIANCE_FASTAPI_PORT", "8001"))
A2A_URL = os.environ.get("A2A_COMPLIANCE_URL", f"http://{HOST}:{PORT}/").replace("://0.0.0.0:", "://127.0.0.1:")


def run_compliance_test(compliance_input: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatches JSON-RPC payload to the Compliance A2A server and extracts result."""
    task_id = str(uuid.uuid4())
    payload = {
        "jsonrpc": "2.0",
        "id": task_id,
        "method": "SendMessage",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "ROLE_USER",
                "parts": [{"text": json.dumps(compliance_input)}],
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
            f"Unable to connect to Compliance A2A server at {A2A_URL}. "
            "Ensure 'python apps/agent-compliance/server.py' is running."
        )

    if response.status_code != 200:
        raise RuntimeError(f"A2A server returned HTTP {response.status_code}: {response.text}")

    try:
        a2a_response = response.json()
    except ValueError:
        raise ValueError("A2A server returned invalid JSON.")

    if "error" in a2a_response:
        raise RuntimeError(json.dumps(a2a_response["error"], indent=2))

    result = a2a_response.get("result")
    if not result:
        raise ValueError("A2A response does not contain result.")

    task = result.get("task")
    if not task:
        raise ValueError("A2A response does not contain result.task.")

    task_state = task.get("status", {}).get("state")
    artifacts = task.get("artifacts", [])

    compliance_result: Optional[Dict[str, Any]] = None
    for artifact in artifacts:
        for part in artifact.get("parts", []):
            text = part.get("text")
            if not text:
                continue
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict) and ("compliance_status" in parsed or "error" in parsed):
                    compliance_result = parsed
                    break
            except json.JSONDecodeError:
                continue
        if compliance_result is not None:
            break

    if compliance_result is None:
        raise ValueError(
            f"Compliance result was not found in A2A artifacts (Task State: {task_state})."
        )

    print(json.dumps(compliance_result, indent=2))
    return compliance_result


# TEST 1: Overdose evaluation (10 mg exceeds protocol's 5 mg / 8 mg limit -> NON_COMPLIANT)
test_1_input = {
    "trial_id": "NCT02415400",
    "recent_action": {
        "drug": "apixaban",
        "dosage": "10 mg",
        "frequency": "twice daily",
        "route": "oral",
    },
    "relevant_protocols": [
        {
            "chunk_id": "NCT02415400-treatment-003",
            "rule_id": "NCT02415400_DOSE_LIMIT",
            "text": (
                "The recommended apixaban dose is 5 mg administered "
                "twice daily. Doses exceeding 5 mg single dose are not permitted."
            ),
            "section": "treatment and dosing",
            "score": 0.96,
        }
    ],
    "report_history": [],
}

# TEST 2: Modify flow (dose adjusted down to 5 mg -> COMPLIANT)
test_2_input = {
    "trial_id": "NCT02415400",
    "recent_action": {
        "drug": "apixaban",
        "dosage": "5 mg",
        "frequency": "twice daily",
        "route": "oral",
    },
    "relevant_protocols": [
        {
            "chunk_id": "NCT02415400-treatment-003",
            "rule_id": "NCT02415400_DOSE_LIMIT",
            "text": (
                "The recommended apixaban dose is 5 mg administered "
                "twice daily. Doses exceeding 5 mg single dose are not permitted."
            ),
            "section": "treatment and dosing",
            "score": 0.96,
        }
    ],
    "report_history": [
        {
            "compliance_status": "NON_COMPLIANT",
            "violations": [
                {
                    "parameter": "dosage",
                    "observed": "10 mg",
                    "expected": {"operator": "<=", "value": "5", "unit": "mg"},
                    "protocol_text": "Recommended apixaban dose is 5 mg twice daily.",
                    "reason": "Prescribed dose (10 mg) exceeds 5 mg ceiling.",
                }
            ],
            "explanation": "Initial prescribed dose of 10 mg exceeded protocol ceiling.",
        }
    ],
    "modification": "Reduced apixaban dose from 10 mg to 5 mg twice daily to conform with protocol.",
}

# TEST 3: Contract Guardrail (rejects demographic keys like patient_id)
test_3_prohibited_input = {
    "trial_id": "NCT02415400",
    "patient_id": "P001",
    "recent_action": {"drug": "apixaban", "dosage": "5 mg"},
    "relevant_protocols": [],
    "report_history": [],
}


if __name__ == "__main__":
    print(f"Targeting Compliance A2A Endpoint: {A2A_URL}\n")

    print("============================================================")
    print("RUNNING TEST 1: Overdose Action -> NON_COMPLIANT")
    print("============================================================")
    res1 = run_compliance_test(test_1_input)
    assert res1.get("compliance_status") == "NON_COMPLIANT", f"Test 1 failed! Got: {res1.get('compliance_status')}"
    assert res1.get("valid") is False, "Test 1 expected valid=False"
    assert len(res1.get("violations", [])) > 0, "Test 1 expected violations"
    print("--> Test 1 Passed: Correctly flagged dose violation.\n")

    print("============================================================")
    print("RUNNING TEST 2: Modify Flow -> COMPLIANT")
    print("============================================================")
    res2 = run_compliance_test(test_2_input)
    assert res2.get("compliance_status") == "COMPLIANT", f"Test 2 failed! Got: {res2.get('compliance_status')}"
    assert res2.get("valid") is True, "Test 2 expected valid=True"
    assert len(res2.get("violations", [])) == 0, "Test 2 expected zero active violations"
    print("--> Test 2 Passed: Correctly validated modified dose.\n")

    print("============================================================")
    print("RUNNING TEST 3: PHI Guardrail Rejection (patient_id)")
    print("============================================================")
    res3 = run_compliance_test(test_3_prohibited_input)
    assert "PHI Guardrail" in res3.get("explanation", "") or res3.get("compliance_status") == "UNKNOWN", "Test 3 failed PHI check"
    print("--> Test 3 Passed: Correctly rejected prohibited patient demographic key.\n")

    print("=" * 60)
    print("All Compliance Agent integration tests on A2A server passed successfully!")
    print("=" * 60)