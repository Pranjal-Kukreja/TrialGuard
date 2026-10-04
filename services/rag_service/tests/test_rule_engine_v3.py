from src.safety.rule_engine_v3 import (
    ELIGIBLE,
    INELIGIBLE,
    INSUFFICIENT_EVIDENCE,
    evaluate_rule,
    evaluate_trial,
)



def test_numeric_range_pass():
    patient = {
        "demographics": {
            "age": 65
        }
    }

    rule = {
        "rule_id": "TEST_AGE",
        "criterion_type": "inclusion",
        "rule_type": "numeric_range",
        "field_path": "demographics.age",
        "min": 18,
        "evidence_required": True,
    }

    result = evaluate_rule(
        rule,
        patient,
    )

    assert result["state"] == "PASS"


def test_numeric_range_fail():
    patient = {
        "demographics": {
            "age": 15
        }
    }

    rule = {
        "rule_id": "TEST_AGE",
        "criterion_type": "inclusion",
        "rule_type": "numeric_range",
        "field_path": "demographics.age",
        "min": 18,
        "evidence_required": True,
    }

    result = evaluate_rule(
        rule,
        patient,
    )

    assert result["state"] == "FAIL"


def test_missing_required_evidence():
    patient = {
        "demographics": {}
    }

    rule = {
        "rule_id": "TEST_AGE",
        "criterion_type": "inclusion",
        "rule_type": "numeric_range",
        "field_path": "demographics.age",
        "min": 18,
        "evidence_required": True,
    }

    result = evaluate_rule(
        rule,
        patient,
    )

    assert result["state"] == "UNKNOWN"


def test_triggered_exclusion_is_fail():
    patient = {
        "medical_history": {
            "history_intracranial_hemorrhage": True
        }
    }

    rule = {
        "rule_id": "TEST_ICH",
        "criterion_type": "exclusion",
        "rule_type": "exact_exclusion",
        "field_path": (
            "medical_history."
            "history_intracranial_hemorrhage"
        ),
        "disallowed_value": True,
        "evidence_required": True,
    }

    result = evaluate_rule(
        rule,
        patient,
    )

    assert result["state"] == "FAIL"


def test_non_triggered_exclusion_is_pass():
    patient = {
        "medical_history": {
            "history_intracranial_hemorrhage": False
        }
    }

    rule = {
        "rule_id": "TEST_ICH",
        "criterion_type": "exclusion",
        "rule_type": "exact_exclusion",
        "field_path": (
            "medical_history."
            "history_intracranial_hemorrhage"
        ),
        "disallowed_value": True,
        "evidence_required": True,
    }

    result = evaluate_rule(
        rule,
        patient,
    )

    assert result["state"] == "PASS"


def test_trial_eligible():
    patient = {
        "demographics": {
            "age": 50
        },
        "medical_history": {
            "bleeding": False
        },
    }

    trial = {
        "name": "TEST",
        "rules": [
            {
                "rule_id": "INC_AGE",
                "criterion_type": "inclusion",
                "rule_type": "numeric_range",
                "field_path": "demographics.age",
                "min": 18,
                "evidence_required": True,
            },
            {
                "rule_id": "EXC_BLEED",
                "criterion_type": "exclusion",
                "rule_type": "exact_exclusion",
                "field_path": "medical_history.bleeding",
                "disallowed_value": True,
                "evidence_required": True,
            },
        ],
    }

    result = evaluate_trial(
        "TEST001",
        trial,
        patient,
    )

    assert result["status"] == ELIGIBLE


def test_trial_failed_inclusion_is_ineligible():
    patient = {
        "demographics": {
            "age": 15
        }
    }

    trial = {
        "name": "TEST",
        "rules": [
            {
                "rule_id": "INC_AGE",
                "criterion_type": "inclusion",
                "rule_type": "numeric_range",
                "field_path": "demographics.age",
                "min": 18,
                "evidence_required": True,
            }
        ],
    }

    result = evaluate_trial(
        "TEST001",
        trial,
        patient,
    )

    assert result["status"] == INELIGIBLE


def test_trial_missing_evidence():
    patient = {}

    trial = {
        "name": "TEST",
        "rules": [
            {
                "rule_id": "INC_AGE",
                "criterion_type": "inclusion",
                "rule_type": "numeric_range",
                "field_path": "demographics.age",
                "min": 18,
                "evidence_required": True,
            }
        ],
    }

    result = evaluate_trial(
        "TEST001",
        trial,
        patient,
    )

    assert (
        result["status"]
        == INSUFFICIENT_EVIDENCE
    )


def test_exclusion_overrides_unknown():
    patient = {
        "medical_history": {
            "bleeding": True
        }
    }

    trial = {
        "name": "TEST",
        "rules": [
            {
                "rule_id": "INC_AGE",
                "criterion_type": "inclusion",
                "rule_type": "numeric_range",
                "field_path": "demographics.age",
                "min": 18,
                "evidence_required": True,
            },
            {
                "rule_id": "EXC_BLEED",
                "criterion_type": "exclusion",
                "rule_type": "exact_exclusion",
                "field_path": "medical_history.bleeding",
                "disallowed_value": True,
                "evidence_required": True,
            },
        ],
    }

    result = evaluate_trial(
        "TEST001",
        trial,
        patient,
    )

    assert result["status"] == INELIGIBLE

import json
from pathlib import Path

from src.safety.rule_engine_v3 import (
    evaluate_all_trials,
)


def test_schema_aligned_patient_all_trials_resolve():
    root = Path(__file__).resolve().parents[1]

    rules_path = (
        root
        / "data"
        / "processed"
        / "rules"
        / "rules.json"
    )

    patient_path = (
        root
        / "data"
        / "processed"
        / "test_patient_schema_test.json"
    )

    with rules_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        rules = json.load(file)

    with patient_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        patient = json.load(file)

    result = evaluate_all_trials(
        rules,
        patient,
    )

    assert len(result["trials"]) == 4

    for trial_result in result["trials"].values():
        assert (
            trial_result["status"]
            == "ELIGIBLE"
        )

        assert (
            trial_result["summary"]["unknown"]
            == 0
        )

def test_numeric_exclusion_structured_measurement_not_triggered():
    patient = {
        "lab_results": {
            "creatinine_clearance": {
                "value": 42,
                "unit": "mL/min",
            }
        }
    }

    rule = {
        "rule_id": "TEST_RENAL",
        "criterion_type": "exclusion",
        "rule_type": "numeric_exclusion",
        "field_path": "lab_results.creatinine_clearance",
        "operator": "<",
        "threshold": 30,
        "unit": "mL/min",
        "evidence_required": True,
    }

    result = evaluate_rule(
        rule,
        patient,
    )

    assert result["state"] == "PASS"


def test_numeric_exclusion_structured_measurement_triggered():
    patient = {
        "lab_results": {
            "creatinine_clearance": {
                "value": 20,
                "unit": "mL/min",
            }
        }
    }

    rule = {
        "rule_id": "TEST_RENAL",
        "criterion_type": "exclusion",
        "rule_type": "numeric_exclusion",
        "field_path": "lab_results.creatinine_clearance",
        "operator": "<",
        "threshold": 30,
        "unit": "mL/min",
        "evidence_required": True,
    }

    result = evaluate_rule(
        rule,
        patient,
    )

    assert result["state"] == "FAIL"


def test_numeric_measurement_unit_mismatch_is_unknown():
    patient = {
        "lab_results": {
            "creatinine_clearance": {
                "value": 42,
                "unit": "wrong-unit",
            }
        }
    }

    rule = {
        "rule_id": "TEST_RENAL",
        "criterion_type": "exclusion",
        "rule_type": "numeric_exclusion",
        "field_path": "lab_results.creatinine_clearance",
        "operator": "<",
        "threshold": 30,
        "unit": "mL/min",
        "evidence_required": True,
    }

    result = evaluate_rule(
        rule,
        patient,
    )

    assert result["state"] == "UNKNOWN"