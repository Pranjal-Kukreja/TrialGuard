def _list_text(
    value
):

    if not value:
        return ""

    if isinstance(
        value,
        list
    ):

        return ", ".join(
            str(item)
            for item
            in value
        )

    return str(value)


def build_trial_query(
    *,
    trial_id,
    patient,
    rule_results,
    user_query
):

    important = []

    for result in (
        rule_results
        or []
    ):

        status = result.get(
            "status"
        )

        if status in {
            "FAIL",
            "VIOLATION",
            "UNKNOWN"
        }:

            parameter = (
                result.get(
                    "parameter"
                )
                or result.get(
                    "criterion"
                )
            )

            if parameter:

                important.append(
                    str(parameter)
                )

    diagnoses = _list_text(
        patient.get(
            "diagnoses"
        )
    )

    medications = _list_text(
        patient.get(
            "medications"
        )
    )

    return (
        f"Clinical trial {trial_id}. "
        f"Eligibility assessment. "
        f"Patient diagnoses: "
        f"{diagnoses}. "
        f"Medications: "
        f"{medications}. "
        f"Important criteria: "
        f"{', '.join(important)}. "
        f"Find relevant inclusion "
        f"criteria, exclusion criteria "
        f"and protocol evidence. "
        f"Question: {user_query}"
    )

def build_fda_query(
    patient,
    trial_id=None
):

    medications = (
        patient.get(
            "medications"
        )
        or []
    )

    diagnoses = (
        patient.get(
            "diagnoses"
        )
        or []
    )

    trial_drugs = {
        "NCT02415400": [
            "apixaban",
            "VKA",
            "aspirin",
            "clopidogrel",
        ],
    }

    drugs = list(
        dict.fromkeys(
            [
                *trial_drugs.get(
                    trial_id,
                    []
                ),
                *medications,
            ]
        )
    )

    return (
        "FDA drug safety evidence. "
        f"Medications: "
        f"{', '.join(drugs)}. "
        f"Diagnoses: "
        f"{', '.join(diagnoses)}. "
        "Find relevant contraindications, "
        "warnings, drug interactions, "
        "bleeding risks and dosage "
        "information."
    )