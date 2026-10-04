import json
from pathlib import Path


# Find project root automatically.
# check_trials.py is inside:
# project/scripts/check_trials.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]

TRIALS_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "cleaned"
    / "trials.jsonl"
)

TARGET_TRIAL_ID = "NCT02415400"


def main():

    print("=" * 60)
    print("TrialGuard - Trial Verification")
    print("=" * 60)

    print(f"Project root : {PROJECT_ROOT}")
    print(f"Dataset      : {TRIALS_FILE}")
    print(f"Looking for  : {TARGET_TRIAL_ID}")

    # Check whether normalized file exists
    if not TRIALS_FILE.exists():

        print("\nERROR:")
        print("trials.jsonl does not exist.")

        print("\nExpected location:")
        print(TRIALS_FILE)

        print("\nRun ingestion first:")
        print("python -m scripts.ingest_data")

        return

    found = False

    with TRIALS_FILE.open(
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            record = json.loads(line)

            if (
                record.get("trial_id")
                == TARGET_TRIAL_ID
            ):

                found = True

                print("\n" + "=" * 60)
                print("TRIAL FOUND")
                print("=" * 60)

                print(
                    "\nTrial ID:",
                    record.get("trial_id")
                )

                print(
                    "\nTitle:",
                    record.get("title")
                )

                print(
                    "\nConditions:",
                    record.get("conditions")
                )

                print(
                    "\nMinimum Age:",
                    record.get("minimum_age")
                )

                print(
                    "\nMaximum Age:",
                    record.get("maximum_age")
                )

                print(
                    "\nSex:",
                    record.get("sex")
                )

                print(
                    "\nPhases:",
                    record.get("phases")
                )

                print("\n" + "=" * 60)
                print("ELIGIBILITY CRITERIA")
                print("=" * 60)

                print(
                    record.get(
                        "eligibility_text",
                        ""
                    )
                )

                print("\n" + "=" * 60)
                print("INTERVENTIONS")
                print("=" * 60)

                print(
                    json.dumps(
                        record.get(
                            "interventions",
                            []
                        ),
                        indent=2,
                        ensure_ascii=False
                    )
                )

                break

    print("\n" + "=" * 60)

    if found:

        print(
            f"SUCCESS: {TARGET_TRIAL_ID} "
            "exists in your dataset."
        )

    else:

        print(
            f"NOT FOUND: {TARGET_TRIAL_ID}"
        )

        print(
            "The trial is not present in "
            "your normalized dataset."
        )

    print("=" * 60)


if __name__ == "__main__":
    main()