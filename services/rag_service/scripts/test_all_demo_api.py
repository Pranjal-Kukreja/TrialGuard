import json
from pathlib import Path

import requests


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

DEMO_DIR = (
    PROJECT_ROOT
    / "data"
    / "mock_fhir"
    / "demo"
)

API_URL = (
    "http://127.0.0.1:8000/evaluate"
)


CASES = [
    (
        "augustus_pass.json",
        "NCT02415400",
        "PASS"
    ),
    (
        "augustus_fail.json",
        "NCT02415400",
        "FAIL"
    ),
    (
        "augustus_review.json",
        "NCT02415400",
        "REVIEW"
    ),

    (
        "trilogy_pass.json",
        "NCT00699998",
        "PASS"
    ),
    (
        "trilogy_fail.json",
        "NCT00699998",
        "FAIL"
    ),
    (
        "trilogy_review.json",
        "NCT00699998",
        "REVIEW"
    ),

    (
        "score_pass.json",
        "NCT00781573",
        "PASS"
    ),
    (
        "score_fail.json",
        "NCT00781573",
        "FAIL"
    ),
    (
        "score_review.json",
        "NCT00781573",
        "REVIEW"
    ),

    (
        "atlas_pass.json",
        "NCT00809965",
        "PASS"
    ),
    (
        "atlas_fail.json",
        "NCT00809965",
        "FAIL"
    ),
    (
        "atlas_review.json",
        "NCT00809965",
        "REVIEW"
    )
]


def main():

    print("=" * 75)
    print("TRIALGUARD HTTP DEMO TEST")
    print("=" * 75)

    passed = 0

    for (
        filename,
        trial_id,
        expected
    ) in CASES:

        path = (
            DEMO_DIR
            / filename
        )

        with path.open(
            "r",
            encoding="utf-8"
        ) as f:

            patient = json.load(f)

        payload = {
            "trial_id":
                trial_id,

            "patient":
                patient,

            "query":
                (
                    "Check whether this "
                    "patient is eligible "
                    "for this trial."
                )
        }

        try:

            response = requests.post(
                API_URL,
                json=payload,
                timeout=120
            )

            if (
                response.status_code
                != 200
            ):

                print(
                    f"[HTTP ERROR] "
                    f"{filename}: "
                    f"{response.status_code}"
                )

                print(
                    response.text
                )

                continue

            result = (
                response.json()
            )

            actual = result.get(
                "decision"
            )

            ok = (
                actual == expected
            )

            if ok:
                passed += 1

            print(
                f"[{'PASS' if ok else 'FAIL'}] "
                f"{filename:25} "
                f"expected={expected:6} "
                f"actual={actual}"
            )

            if not ok:

                print(
                    json.dumps(
                        result,
                        indent=2
                    )
                )

        except Exception as error:

            print(
                f"[ERROR] {filename}: "
                f"{error}"
            )

    print("\n" + "=" * 75)

    print(
        f"Successful: "
        f"{passed}/{len(CASES)}"
    )


if __name__ == "__main__":
    main()