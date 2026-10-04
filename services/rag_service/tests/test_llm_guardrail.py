from src.safety.status_mapper import (
    map_engine_status
)


def test_deterministic_fail_maps_to_fail():
    decision, eligibility, review = map_engine_status(
        "INELIGIBLE"
    )

    assert decision == "FAIL"
    assert eligibility == "INELIGIBLE"
    assert review is False


def test_unknown_maps_to_review():
    decision, eligibility, review = map_engine_status(
        "INSUFFICIENT_EVIDENCE"
    )

    assert decision == "REVIEW"
    assert eligibility == "UNCERTAIN"
    assert review is True
