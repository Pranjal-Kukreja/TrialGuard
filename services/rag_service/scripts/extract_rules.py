import json
from pathlib import Path

from pydantic import ValidationError

from src.extraction.rule_extractor import (
    extract_rules_from_chunk
)

from src.extraction.schemas import (
    ClinicalRule
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


CHUNKS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "trial_chunks.jsonl"
)


RULES_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "rules"
    / "rules.json"
)


TARGET_TRIAL = (
    "NCT02415400"
)


def load_trial_chunks():

    if not CHUNKS_FILE.exists():

        raise FileNotFoundError(
            "\nTrial chunks do not exist:\n"
            f"{CHUNKS_FILE}\n\n"
            "Run:\n"
            "python -m scripts.build_kb"
        )

    chunks = []

    with CHUNKS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            chunk = json.loads(
                line
            )

            if (
                chunk.get("trial_id")
                == TARGET_TRIAL
            ):

                chunks.append(
                    chunk
                )

    return chunks


def main():

    print("=" * 70)

    print(
        "TrialGuard AI - Rule Extraction"
    )

    print("=" * 70)

    print(
        f"Target trial: "
        f"{TARGET_TRIAL}"
    )

    chunks = load_trial_chunks()

    print(
        f"Eligibility chunks found: "
        f"{len(chunks)}"
    )

    if not chunks:

        print(
            "\nNo chunks found for "
            f"{TARGET_TRIAL}."
        )

        return

    extracted_rules = []

    rejected_rules = []

    counter = 1

    for chunk in chunks:

        candidates = (
            extract_rules_from_chunk(
                chunk,
                start_index=counter
            )
        )

        for candidate in candidates:

            try:

                # Important:
                # validate every automatically
                # produced rule with Pydantic.

                validated = (
                    ClinicalRule
                    .model_validate(
                        candidate
                    )
                )

                extracted_rules.append(
                    validated.model_dump()
                )

                counter += 1

                print(
                    "\nRULE EXTRACTED"
                )

                print(
                    "Rule ID:",
                    validated.rule_id
                )

                print(
                    "Parameter:",
                    validated.parameter
                )

                print(
                    "Operator:",
                    validated.operator
                )

                print(
                    "Threshold:",
                    validated.threshold
                )

                print(
                    "Unit:",
                    validated.unit
                )

                print(
                    "Source:",
                    validated.source_chunk_id
                )

            except ValidationError as error:

                rejected_rules.append({
                    "candidate":
                        candidate,

                    "error":
                        str(error)
                })

    # ----------------------------------------
    # Remove exact duplicate rules
    # ----------------------------------------

    unique = {}

    for rule in extracted_rules:

        key = (
            rule["trial_id"],
            rule["rule_type"],
            rule["parameter"],
            rule["operator"],
            str(rule["threshold"]),
            rule.get("unit"),
            rule[
                "source_chunk_id"
            ]
        )

        unique[key] = rule

    extracted_rules = list(
        unique.values()
    )

    # ----------------------------------------
    # Save
    # ----------------------------------------

    RULES_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with RULES_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            extracted_rules,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\n" + "=" * 70)

    print(
        "RULE EXTRACTION COMPLETE"
    )

    print("=" * 70)

    print(
        f"Rules extracted : "
        f"{len(extracted_rules)}"
    )

    print(
        f"Rules rejected  : "
        f"{len(rejected_rules)}"
    )

    print(
        f"\nSaved to:\n"
        f"{RULES_FILE}"
    )

    print(
        "\nIMPORTANT:"
    )

    print(
        "Review rules.json against the "
        "original ClinicalTrials.gov text "
        "before treating the rules as valid."
    )


if __name__ == "__main__":
    main()