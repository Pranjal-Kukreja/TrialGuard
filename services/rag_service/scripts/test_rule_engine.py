import json
from pathlib import Path

from src.safety.rule_engine import (
    RuleEngine,
    derive_decision
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


PATIENT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "test_patient_complete.json"
)


def main():

    with PATIENT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        patient = json.load(
            file
        )

    engine = RuleEngine()

    results = engine.evaluate(
        patient,
        "NCT02415400"
    )

    for result in results:

        print(
            f'{result["status"]:15} '
            f'{result["rule_id"]}'
        )

        print(
            f'    {result["reason"]}'
        )

    (
        decision,
        eligibility,
        review
    ) = derive_decision(
        results
    )

    print("\n" + "=" * 70)

    print(
        "Decision:",
        decision
    )

    print(
        "Eligibility:",
        eligibility
    )

    print(
        "Human review:",
        review
    )


if __name__ == "__main__":
    main()