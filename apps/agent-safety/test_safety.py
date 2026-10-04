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
PORT = int(os.environ.get("SAFETY_FASTAPI_PORT", "8002"))
A2A_URL = os.environ.get("SAFETY_AGENT_URL", f"http://{HOST}:{PORT}/").replace("://0.0.0.0:", "://127.0.0.1:")


def run_safety_test(safety_input: Dict[str, Any], method: str = "SendMessage") -> Dict[str, Any]:
    """Dispatches JSON-RPC payload to the Safety server and extracts result."""
    task_id = str(uuid.uuid4())
    if method == "SendMessage":
        payload = {
            "jsonrpc": "2.0",
            "id": task_id,
            "method": "SendMessage",
            "params": {
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "ROLE_USER",
                    "parts": [{"text": json.dumps(safety_input)}],
                }
            },
        }
    else:
        payload = {
            "jsonrpc": "2.0",
            "id": task_id,
            "method": "evaluate_safety",
            "params": safety_input,
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
            f"Unable to connect to Safety A2A server at {A2A_URL}. "
            "Ensure 'python apps/agent-safety/server.py' is running."
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"Safety server returned HTTP {response.status_code}: {response.text}"
        )

    try:
        a2a_response = response.json()
    except ValueError:
        raise RuntimeError(f"Server returned non-JSON response: {response.text}")

    if "error" in a2a_response:
        raise RuntimeError(f"JSON-RPC error: {a2a_response['error']}")

    result = a2a_response.get("result", {})
    if method == "SendMessage":
        task = result.get("task", {})
        artifacts = task.get("artifacts", [])
        if not artifacts:
            raise RuntimeError(f"A2A task returned no artifacts: {task}")
        text_payload = artifacts[0]["parts"][0]["text"]
        return json.loads(text_payload)
    return result


def test_agent_card():
    card_url = f"{A2A_URL.rstrip('/')}/.well-known/agent-card.json"
    print(f"\n[TEST 0] Checking Agent Discovery -> {card_url}")
    resp = requests.get(card_url, timeout=10)
    assert resp.status_code == 200, f"Failed agent-card status: {resp.status_code}"
    card = resp.json()
    print(f"  Agent Name: {card.get('name')}")
    print(f"  Protocols: {card.get('protocols')}")
    print("  ✓ Agent discovery card verified.")


def test_safety_cleared():
    print("\n[TEST 1] Testing Cleared Baseline Patient...")
    payload = {
        "trial_id": "TRIAL-2026-ONC",
        "patient_id": "PT-SAFE-001",
        "recent_action": {
            "drug": "Apixaban",
            "dosage": "5mg",
            "frequency": "BID",
            "route": "Oral"
        },
        "patient_data": {
            "lab_results": {
                "creatinine_clearance": 75.0,
                "eGFR": 82.0,
                "ALT": 24.0,
                "AST": 28.0
            },
            "protocol_facts": {
                "ongoing_bleeding": False
            }
        }
    }
    result = run_safety_test(payload)
    print("  Safety Status:", result.get("safety_status"))
    print("  Risk Score:", result.get("risk_score"))
    print("  Contraindications:", result.get("contraindications_found"))
    assert result.get("safety_status") in ("CLEARED", "FLAGGED"), f"Unexpected status: {result}"
    print("  ✓ Baseline patient safety cleared.")


def test_safety_renal_contraindication():
    print("\n[TEST 2] Testing Severe Renal Impairment (< 30 mL/min CrCl)...")
    payload = {
        "trial_id": "TRIAL-2026-ONC",
        "patient_id": "PT-RENAL-002",
        "recent_action": {
            "drug": "Apixaban",
            "dosage": "5mg",
            "frequency": "BID",
            "route": "Oral"
        },
        "patient_data": {
            "lab_results": {
                "creatinine_clearance": 22.0,
                "eGFR": 25.0,
                "ALT": 30.0,
                "AST": 32.0
            },
            "protocol_facts": {
                "ongoing_bleeding": False
            }
        }
    }
    result = run_safety_test(payload)
    print("  Safety Status:", result.get("safety_status"))
    print("  Risk Score:", result.get("risk_score"))
    print("  Violations:", len(result.get("violations", [])))
    assert result.get("safety_status") == "CRITICAL", f"Expected CRITICAL for CrCl=22, got {result.get('safety_status')}"
    assert result.get("contraindications_found", 0) >= 1
    rule_ids = [v.get("rule_id") for v in result.get("violations", [])]
    assert "SAFETY_RENAL_CLEARANCE_BREACH" in rule_ids, f"Expected SAFETY_RENAL_CLEARANCE_BREACH, found {rule_ids}"
    print("  ✓ Hard renal contraindication detected properly.")


def test_safety_hepatic_toxicity():
    print("\n[TEST 3] Testing Hepatic Toxicity (> 120 U/L ALT/AST)...")
    payload = {
        "trial_id": "TRIAL-2026-ONC",
        "patient_id": "PT-HEPATIC-003",
        "recent_action": {
            "drug": "Experimental-X",
            "dosage": "100mg",
            "frequency": "Daily",
            "route": "Oral"
        },
        "patient_data": {
            "lab_results": {
                "creatinine_clearance": 80.0,
                "ALT": 195.0,
                "AST": 150.0
            },
            "protocol_facts": {
                "ongoing_bleeding": False
            }
        }
    }
    result = run_safety_test(payload)
    print("  Safety Status:", result.get("safety_status"))
    assert result.get("safety_status") == "CRITICAL"
    rule_ids = [v.get("rule_id") for v in result.get("violations", [])]
    assert "SAFETY_HEPATIC_TRANSAMINASE_ELEVATION" in rule_ids
    print("  ✓ Hepatic transaminase toxicity detected properly.")


def test_safety_missing_patient_id():
    print("\n[TEST 4] Testing Missing Patient ID (PHI Safeguard)...")
    payload = {
        "trial_id": "TRIAL-2026-ONC",
        "recent_action": {"drug": "Aspirin"}
    }
    result = run_safety_test(payload)
    print("  Safety Status:", result.get("safety_status"))
    assert result.get("safety_status") == "UNKNOWN"
    rule_ids = [v.get("rule_id") for v in result.get("violations", [])]
    assert "PHI_REQUIRED" in rule_ids
    print("  ✓ Missing patient_id guarded correctly.")


if __name__ == "__main__":
    print(f"Executing Safety Agent Test Suite against {A2A_URL}")
    try:
        test_agent_card()
        test_safety_cleared()
        test_safety_renal_contraindication()
        test_safety_hepatic_toxicity()
        test_safety_missing_patient_id()
        print("\nAll Safety Agent tests completed successfully!")
    except Exception as e:
        print(f"\n[ERROR] Test run failed: {e}", file=sys.stderr)
        sys.exit(1)
