import json
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

DEMO_DIR = (
    PROJECT_ROOT
    / "data"
    / "mock_fhir"
    / "demo"
)


class PatientNotFoundError(LookupError):
    pass


def get_patient(patient_id: str) -> dict:
    """Return one complete mock-FHIR patient by patient ID."""

    normalized_id = patient_id.strip().upper()
    patient_path = DEMO_DIR / (
        normalized_id.lower()
        + ".json"
    )

    # Demo files use semantic names, so search their patient_id values.
    for candidate in DEMO_DIR.glob("*.json"):
        with candidate.open(
            "r",
            encoding="utf-8"
        ) as file:
            patient = json.load(file)

        if str(patient.get("patient_id", "")).upper() == normalized_id:
            return patient

    if patient_path.is_file():
        with patient_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    raise PatientNotFoundError(
        f"Mock FHIR patient not found: {patient_id}"
    )
