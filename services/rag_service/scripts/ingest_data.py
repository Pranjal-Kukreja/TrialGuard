import json
from pathlib import Path

from src.ingestion.clinicaltrials_loader import load_trials
from src.preprocessing.normalizer import normalize_trial
from src.ingestion.fda_label_loader import (
    load_fda_labels
)

TRIAL_INPUT = "data/raw/clinicaltrials/clinical_trials.json"

TRIAL_OUTPUT = "data/interim/cleaned/trials.jsonl"

FDA_LABEL_DIR = (
    "data/raw/fda_labels"
)

FDA_LABEL_OUTPUT = (
    "data/interim/cleaned/"
    "fda_labels.jsonl"
)


def ingest_fda_labels():

    Path(FDA_LABEL_OUTPUT).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    count = 0

    with open(
        FDA_LABEL_OUTPUT,
        "w",
        encoding="utf-8"
    ) as output:

        for path in Path(
            FDA_LABEL_DIR
        ).glob("*.json"):

            print(
                "Processing:",
                path.name
            )

            for label in load_fda_labels(
                str(path)
            ):

                output.write(
                    json.dumps(
                        label,
                        ensure_ascii=False
                    )
                    + "\n"
                )

                count += 1

    print(
        f"Processed {count} FDA labels"
    )

def ingest_trials():

    print("Starting ClinicalTrials.gov ingestion...")
    print(f"Input:  {TRIAL_INPUT}")
    print(f"Output: {TRIAL_OUTPUT}")

    input_path = Path(TRIAL_INPUT)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Clinical trial dataset not found: "
            f"{input_path.resolve()}"
        )

    Path(TRIAL_OUTPUT).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    trials = load_trials(TRIAL_INPUT)

    print(f"Raw trials loaded: {len(trials)}")

    written = 0

    with open(
        TRIAL_OUTPUT,
        "w",
        encoding="utf-8"
    ) as output:

        for raw in trials:

            trial = normalize_trial(raw)

            if not trial.get("trial_id"):
                continue

            output.write(
                json.dumps(
                    trial,
                    ensure_ascii=False
                )
                + "\n"
            )

            written += 1

    print(f"Successfully normalized {written} trials.")
    print(
        f"Saved to: "
        f"{Path(TRIAL_OUTPUT).resolve()}"
    )


if __name__ == "__main__":
    ingest_trials()