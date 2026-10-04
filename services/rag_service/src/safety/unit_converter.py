def normalize_unit(
    unit: str | None
):

    if unit is None:
        return None

    value = (
        str(unit)
        .strip()
        .lower()
    )

    aliases = {
        "years": "years",
        "year": "years",

        "days": "days",
        "day": "days",

        "months": "months",
        "month": "months",

        "kg": "kg",

        "mg/dl": "mg/dL",

        "ml/min": "mL/min",

        "ml/min/1.73m2":
            "mL/min/1.73m2",

        "ml/min/1.73m²":
            "mL/min/1.73m2",

        "uln": "ULN",
        "xuln": "ULN"
    }

    return aliases.get(
        value,
        str(unit).strip()
    )


def units_match(
    observed,
    expected
):

    if expected is None:
        return True

    if observed is None:
        return None

    return (
        normalize_unit(observed)
        ==
        normalize_unit(expected)
    )