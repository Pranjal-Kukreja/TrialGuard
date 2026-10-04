import json
from pathlib import Path

from fastapi.testclient import TestClient

from src.api.main import app


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = PROJECT_ROOT / "data" / "mock_fhir" / "demo"


client = TestClient(app)


def load_patient(filename):
    with (DEMO_DIR / filename).open(encoding="utf-8") as file:
        return json.load(file)


def test_health_contract():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["rule_engine"] == "v3"
    assert response.json()["rag"] == "ready"
    assert isinstance(
        response.json()["llm_configured"],
        bool
    )


def test_evaluate_contract_for_demo_decisions():
    cases = [
        ("augustus_pass.json", "ELIGIBLE"),
        ("augustus_fail.json", "INELIGIBLE"),
        ("augustus_review.json", "INSUFFICIENT_EVIDENCE"),
    ]

    required_fields = {
        "trial_id",
        "decision",
        "eligibility",
        "violations",
        "matched_criteria",
        "unknown_criteria",
        "evidence",
        "safety_evidence",
        "explanation",
        "confidence",
        "needs_human_review",
    }

    for filename, expected_status in cases:
        response = client.post(
            "/evaluate",
            json={
                "trial_id": "NCT02415400",
                "patient": load_patient(filename),
                "query": "Check eligibility",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert required_fields <= payload.keys()
        assert payload["trial_id"] == "NCT02415400"
        assert payload["eligibility"] in {
            "ELIGIBLE",
            "INELIGIBLE",
            "UNCERTAIN",
        }

        expected_decision = {
            "ELIGIBLE": "PASS",
            "INELIGIBLE": "FAIL",
            "INSUFFICIENT_EVIDENCE": "REVIEW",
        }[expected_status]
        assert payload["decision"] == expected_decision