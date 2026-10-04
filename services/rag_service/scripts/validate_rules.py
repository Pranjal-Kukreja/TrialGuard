import json
from pathlib import Path

from pydantic import ValidationError

from src.extraction.schemas import ClinicalRule


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

RULES_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "rules"
    / "rules.json"
)


def main():

    print("=" * 70)
    print("TrialGuard - Rule Validation")
    print("=" * 70)

    if not RULES_FILE.exists():

        raise FileNotFoundError(
            f"Rules file not found:\n{RULES_FILE}"
        )

    with RULES_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        rules = json.load(file)

    print(
        f"\nRules loaded: {len(rules)}"
    )

    valid = 0
    invalid = 0

    for index, raw_rule in enumerate(
        rules,
        start=1
    ):

        try:

            rule = (
                ClinicalRule
                .model_validate(
                    raw_rule
                )
            )

            valid += 1

            print(
                f"[PASS] "
                f"{rule.rule_id}"
            )

        except ValidationError as error:

            invalid += 1

            print(
                f"\n[FAIL] Rule #{index}"
            )

            print(
                raw_rule.get(
                    "rule_id",
                    "NO RULE ID"
                )
            )

            print(error)

    print("\n" + "=" * 70)

    print(
        f"Valid   : {valid}"
    )

    print(
        f"Invalid : {invalid}"
    )

    print("=" * 70)

    if invalid == 0:

        print(
            "\nAll rules passed schema validation."
        )


if __name__ == "__main__":
    main()