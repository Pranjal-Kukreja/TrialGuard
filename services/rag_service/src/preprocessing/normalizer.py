from typing import Any


def normalize_trial(raw: dict[str, Any]) -> dict:

    protocol = raw.get(
        "protocolSection",
        raw
    )

    identification = protocol.get(
        "identificationModule",
        {}
    )

    design = protocol.get(
        "designModule",
        {}
    )

    conditions = protocol.get(
        "conditionsModule",
        {}
    )

    eligibility = protocol.get(
        "eligibilityModule",
        {}
    )

    arms = protocol.get(
        "armsInterventionsModule",
        {}
    )

    return {
        "trial_id":
            identification.get("nctId")
            or raw.get("nctId")
            or raw.get("trial_id"),

        "title":
            identification.get("briefTitle")
            or raw.get("title"),

        "conditions":
            conditions.get("conditions")
            or raw.get("conditions", []),

        "phases":
            design.get("phases")
            or raw.get("phases", []),

        "eligibility_text":
            eligibility.get("eligibilityCriteria")
            or raw.get("eligibility_text", ""),

        "minimum_age":
            eligibility.get("minimumAge")
            or raw.get("minimum_age"),

        "maximum_age":
            eligibility.get("maximumAge")
            or raw.get("maximum_age"),

        "sex":
            eligibility.get("sex")
            or raw.get("sex"),

        "healthy_volunteers":
            eligibility.get("healthyVolunteers"),

        "interventions":
            arms.get("interventions")
            or raw.get("interventions", []),

        "source":
            "ClinicalTrials.gov"
    }