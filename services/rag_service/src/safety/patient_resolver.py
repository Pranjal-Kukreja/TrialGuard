from typing import Any


MISSING = object()


def normalize_text(value: Any) -> str:
    return str(value).strip().lower()




MISSING = object()


def resolve_dotted_path(
    patient: dict[str, Any],
    field_path: str,
) -> Any:
    """
    Resolve a dotted path such as:
        demographics.age
        lab_results.platelets
        protocol_facts.days_since_acs

    Returns MISSING when the path does not exist.
    """
    if not field_path:
        return MISSING

    current: Any = patient

    for part in field_path.split("."):
        if not isinstance(current, dict):
            return MISSING

        if part not in current:
            return MISSING

        current = current[part]

    return current

def resolve_patient_value(
    patient: dict,
    parameter: str
):

    # ----------------------------------------
    # Direct patient fields
    # ----------------------------------------

    if parameter in patient:

        value = patient[parameter]

        if value is not None:
            return value

    # ----------------------------------------
    # Laboratory results
    # ----------------------------------------

    labs = patient.get(
        "lab_results",
        {}
    )

    if parameter in labs:

        item = labs[parameter]

        if isinstance(item, dict):

            return item.get(
                "value",
                MISSING
            )

        return item

    # ----------------------------------------
    # Vital signs
    # ----------------------------------------

    vitals = patient.get(
        "vital_signs",
        {}
    )

    if parameter in vitals:

        return vitals[
            parameter
        ]

    # ----------------------------------------
    # Protocol-specific facts
    # ----------------------------------------

    facts = patient.get(
        "protocol_facts",
        {}
    )

    if parameter in facts:

        return facts[
            parameter
        ]

    # ----------------------------------------
    # Special aliases
    # ----------------------------------------

    if parameter == "diagnoses":

        return patient.get(
            "diagnoses",
            []
        )

    if parameter == "medications":

        return patient.get(
            "medications",
            []
        )

    if parameter == "allergies":

        return patient.get(
            "allergies",
            []
        )

    if parameter == "medical_history":

        return patient.get(
            "medical_history",
            []
        )

    if parameter == "current_symptoms":

        return patient.get(
            "current_symptoms",
            []
        )

    return MISSING