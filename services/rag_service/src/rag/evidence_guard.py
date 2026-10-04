def filter_trial_evidence(
    evidence,
    trial_id
):
    """Keep only evidence explicitly belonging to the requested trial."""

    safe = []

    for item in evidence or []:
        if item.get("trial_id") != trial_id:
            continue

        safe.append(item)

    return safe
