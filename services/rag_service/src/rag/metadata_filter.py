def build_trial_query(
    request,
    rule_results=None
):

    patient = request.patient

    relevant_parameters = []

    if rule_results:

        relevant_parameters = [
            result["parameter"]
            for result
            in rule_results
            if result["status"]
            in {
                "VIOLATION",
                "UNKNOWN"
            }
        ]

    labs = ", ".join(
        f"{key}={value}"
        for key, value
        in patient.lab_results.items()
    )

    return (
        f"Trial {request.trial_id} "
        f"eligibility assessment. "
        f"Age: {patient.age}. "
        f"Sex: {patient.sex}. "
        f"Diagnoses: "
        f"{', '.join(patient.diagnoses)}. "
        f"Medications: "
        f"{', '.join(patient.medications)}. "
        f"Laboratory results: {labs}. "
        f"Important rule parameters: "
        f"{', '.join(relevant_parameters)}. "
        f"Retrieve inclusion criteria, "
        f"exclusion criteria and protocol "
        f"evidence relevant to these facts. "
        f"Question: {request.query}"
    )