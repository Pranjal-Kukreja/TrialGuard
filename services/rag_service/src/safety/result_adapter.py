from src.safety.status_mapper import (
    map_engine_status
)


def adapt_engine_result(
    engine_result
):

    engine_status = (
        engine_result.get(
            "status",
            "INSUFFICIENT_EVIDENCE"
        )
    )

    (
        decision,
        eligibility,
        needs_review
    ) = map_engine_status(
        engine_status
    )

    raw_results = (
        engine_result.get(
            "rule_results"
        )
        or engine_result.get(
            "rules"
        )
        or []
    )

    violations = []
    matched = []
    unknown = []
    not_applicable = []
    dosage_checks = []

    for item in raw_results:

        status = (
            str(
                item.get(
                    "status",
                    item.get(
                        "state",
                        "UNKNOWN"
                    )
                )
            )
            .upper()
        )

        rule_id = item.get(
            "rule_id",
            "UNKNOWN_RULE"
        )

        criterion = (
            item.get(
                "parameter"
            )
            or item.get(
                "criterion"
            )
            or "unknown"
        )

        if status in {
            "FAIL",
            "VIOLATION"
        }:

            violations.append({
                "rule_id":
                    rule_id,

                "parameter":
                    criterion,

                "value":
                    item.get(
                        "value"
                    ),

                "threshold":
                    item.get(
                        "threshold"
                    ),

                "unit":
                    item.get(
                        "unit"
                    ),

                "action":
                    item.get(
                        "action",
                        "EXCLUDE"
                    ),

                "reason":
                    item.get(
                        "reason",
                        "Criterion failed."
                    )
            })

        elif status == "PASS":

            if (
                item.get(
                    "action"
                )
                == "DOSE_CHECK"
            ):

                dosage_checks.append(
                    item
                )

            else:

                matched.append({
                    "rule_id":
                        rule_id,

                    "criterion":
                        criterion,

                    "result":
                        "PASS",

                    "value":
                        item.get(
                            "value"
                        ),

                    "threshold":
                        item.get(
                            "threshold"
                        ),

                    "unit":
                        item.get(
                            "unit"
                        )
                })

        elif status == "UNKNOWN":

            unknown.append({
                "rule_id":
                    rule_id,

                "criterion":
                    criterion,

                "reason":
                    item.get(
                        "reason",
                        "Required evidence is missing."
                    )
            })

        elif (
            status
            == "NOT_APPLICABLE"
        ):

            not_applicable.append({
                "rule_id":
                    rule_id,

                "criterion":
                    criterion,

                "reason":
                    item.get(
                        "reason",
                        "Criterion does not apply."
                    )
            })

    return {
        "decision":
            decision,

        "eligibility":
            eligibility,

        "violations":
            violations,

        "matched_criteria":
            matched,

        "unknown_criteria":
            unknown,

        "not_applicable_criteria":
            not_applicable,

        "dosage_checks":
            dosage_checks,

        "needs_human_review":
            needs_review
    }