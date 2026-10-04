def map_engine_status(
    engine_status: str
) -> tuple[str, str, bool]:

    status = (
        str(engine_status)
        .strip()
        .upper()
    )

    if status == "ELIGIBLE":

        return (
            "PASS",
            "ELIGIBLE",
            False
        )

    if status == "INELIGIBLE":

        return (
            "FAIL",
            "INELIGIBLE",
            False
        )

    # Includes:
    #
    # INSUFFICIENT_EVIDENCE
    # UNKNOWN
    # anything unexpected

    return (
        "REVIEW",
        "UNCERTAIN",
        True
    )