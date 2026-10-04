from typing import Any


def normalize(value: Any):

    if isinstance(value, str):
        return value.strip().lower()

    return value


def compare_scalar(
    observed,
    operator,
    threshold
):

    observed = normalize(
        observed
    )

    threshold = normalize(
        threshold
    )

    if operator in {
        "=",
        "=="
    }:
        return observed == threshold

    if operator == "!=":
        return observed != threshold

    if operator == ">":
        return observed > threshold

    if operator == ">=":
        return observed >= threshold

    if operator == "<":
        return observed < threshold

    if operator == "<=":
        return observed <= threshold

    raise ValueError(
        f"Unsupported scalar operator: "
        f"{operator}"
    )


def compare_collection(
    observed,
    operator,
    threshold
):

    if not isinstance(
        observed,
        list
    ):
        observed = [observed]

    observed_values = {
        str(value)
        .strip()
        .lower()

        for value
        in observed
    }

    if isinstance(
        threshold,
        list
    ):

        threshold_values = {
            str(value)
            .strip()
            .lower()

            for value
            in threshold
        }

    else:

        threshold_values = {
            str(threshold)
            .strip()
            .lower()
        }

    if operator in {
        "CONTAINS",
        "ANY_OF",
        "IN"
    }:

        return bool(
            observed_values
            & threshold_values
        )

    if operator == "NOT_IN":

        return not bool(
            observed_values
            & threshold_values
        )

    raise ValueError(
        f"Unsupported collection "
        f"operator: {operator}"
    )

