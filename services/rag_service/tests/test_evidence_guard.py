from src.rag.evidence_guard import filter_trial_evidence


def test_filter_trial_evidence_rejects_other_trials():
    evidence = [
        {
            "trial_id": "NCT02415400",
            "chunk_id": "good",
        },
        {
            "trial_id": "NCT00781573",
            "chunk_id": "wrong",
        },
    ]

    result = filter_trial_evidence(
        evidence,
        "NCT02415400"
    )

    assert result == [evidence[0]]
