import json
from pathlib import Path

import pytest

from src.safety.rule_engine_v3 import evaluate_trial


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = PROJECT_ROOT / "data" / "mock_fhir" / "demo"


@pytest.mark.parametrize(
    "trial_id,filename,expected",
    [
        ("NCT02415400", "augustus_pass.json", "ELIGIBLE"),
        ("NCT02415400", "augustus_fail.json", "INELIGIBLE"),
        (
            "NCT02415400",
            "augustus_review.json",
            "INSUFFICIENT_EVIDENCE",
        ),
        ("NCT00699998", "trilogy_pass.json", "ELIGIBLE"),
        ("NCT00699998", "trilogy_fail.json", "INELIGIBLE"),
        (
            "NCT00699998",
            "trilogy_review.json",
            "INSUFFICIENT_EVIDENCE",
        ),
        ("NCT00781573", "score_pass.json", "ELIGIBLE"),
        ("NCT00781573", "score_fail.json", "INELIGIBLE"),
        (
            "NCT00781573",
            "score_review.json",
            "INSUFFICIENT_EVIDENCE",
        ),
        ("NCT00809965", "atlas_pass.json", "ELIGIBLE"),
        ("NCT00809965", "atlas_fail.json", "INELIGIBLE"),
        (
            "NCT00809965",
            "atlas_review.json",
            "INSUFFICIENT_EVIDENCE",
        ),
    ],
)
def test_demo_decision(trial_id, filename, expected):
    with (DEMO_DIR / filename).open(encoding="utf-8") as file:
        patient = json.load(file)

    result = evaluate_trial(trial_id, patient)

    assert result["status"] == expected
