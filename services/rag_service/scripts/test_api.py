import json
from pathlib import Path

import requests


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

PATIENT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "test_patient_normalized.json"
)

URL = (
    "http://127.0.0.1:8000/evaluate"
)


def main():

    with PATIENT_FILE.open(
        "r",
        encoding="utf-8"
    ) as f:

        patient = json.load(f)

    payload = {
        "trial_id":
            "NCT02415400",

        "patient":
            patient,

        "query":
            (
                "Check whether this "
                "patient is eligible "
                "for the trial."
            )
    }

    print("=" * 70)
    print("TESTING TRIALGUARD API")
    print("=" * 70)

    response = requests.post(
        URL,
        json=payload,
        timeout=120
    )

    print(
        "HTTP status:",
        response.status_code
    )

    print()

    try:

        data = response.json()

        print(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False
            )
        )

    except Exception:

        print(
            response.text
        )


if __name__ == "__main__":
    main()