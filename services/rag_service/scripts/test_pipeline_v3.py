import json
from pathlib import Path

from src.api.models import (
    TrialGuardRequest
)

from src.pipeline_v3 import (
    TrialGuardPipelineV3
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
    / "test_patient_normalized.json"
)


def main():

    with PATIENT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        patient = json.load(
            file
        )

    request = (
        TrialGuardRequest(
            trial_id="NCT02415400",

            patient=patient,

            query=(
                "Check whether this "
                "patient is eligible "
                "for the trial."
            )
        )
    )

    pipeline = (
        TrialGuardPipelineV3()
    )

    result = (
        pipeline.evaluate_without_llm(
            request
        )
    )

    print(
        json.dumps(
            result,
            indent=2,
            default=str
        )
    )


if __name__ == "__main__":
    main()