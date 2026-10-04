import json
from pathlib import Path

from src.safety.comparators import (
    compare_scalar,
    compare_collection
)

from src.safety.patient_resolver import (
    MISSING,
    resolve_patient_value
)

from enum import Enum


class EvaluationState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)


DEFAULT_RULE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "rules"
    / "rules.json"
)


COLLECTION_OPERATORS = {
    "CONTAINS",
    "ANY_OF",
    "IN",
    "NOT_IN"
}


CONDITIONAL_ACTIONS = {
    "REQUIRE_IF_ACS_PATHWAY",
    "REQUIRE_IF_PCI_PATHWAY",
    "REQUIRE_IF_WOCBP"
}


class RuleEngine:

    def __init__(
        self,
        rule_file=None
    ):

        self.rule_file = (
            Path(rule_file)
            if rule_file
            else DEFAULT_RULE_FILE
        )

        self.rules = []

        self.reload()

    def reload(self):

        if not self.rule_file.exists():

            self.rules = []
            return

        with self.rule_file.open(
            "r",
            encoding="utf-8"
        ) as file:

            self.rules = json.load(
                file
            )

    def get_rules(
        self,
        trial_id: str
    ):

        return [
            rule
            for rule
            in self.rules
            if rule.get(
                "trial_id"
            ) == trial_id
        ]

    def evaluate(
        self,
        patient: dict,
        trial_id: str
    ):

        rules = self.get_rules(
            trial_id
        )

        results = []

        for rule in rules:

            if (
                rule.get("logic")
                == "AT_LEAST_N"
            ):

                result = (
                    self._evaluate_compound_rule(
                        patient,
                        rule
                    )
                )

            else:

                result = (
                    self._evaluate_atomic_rule(
                        patient,
                        rule
                    )
                )

            results.append(
                result
            )

        return results

    # ==========================================
    # NORMAL RULE
    # ==========================================

    def _evaluate_atomic_rule(
        self,
        patient,
        rule
    ):

        rule_id = rule[
            "rule_id"
        ]

        parameter = rule[
            "parameter"
        ]

        operator = rule.get(
            "operator"
        )

        threshold = rule.get(
            "threshold"
        )

        action = rule.get(
            "action"
        )

        observed = (
            resolve_patient_value(
                patient,
                parameter
            )
        )

        # --------------------------------------
        # Missing patient data
        # --------------------------------------

        if observed is MISSING:

            return {
                "rule_id":
                    rule_id,

                "parameter":
                    parameter,

                "status":
                    "UNKNOWN",

                "action":
                    action,

                "value":
                    None,

                "threshold":
                    threshold,

                "unit":
                    rule.get(
                        "unit"
                    ),

                "source_chunk_id":
                    rule.get(
                        "source_chunk_id"
                    ),

                "reason":
                    (
                        "Required patient "
                        "information is missing."
                    )
            }

        # --------------------------------------
        # Conditional rules
        # --------------------------------------

        if (
            action
            in CONDITIONAL_ACTIONS
        ):

            applicable = (
                self._conditional_rule_applies(
                    patient,
                    action
                )
            )

            if applicable is False:

                return {
                    "rule_id":
                        rule_id,

                    "parameter":
                        parameter,

                    "status":
                        "NOT_APPLICABLE",

                    "action":
                        action,

                    "value":
                        observed,

                    "threshold":
                        threshold,

                    "unit":
                        rule.get(
                            "unit"
                        ),

                    "source_chunk_id":
                        rule.get(
                            "source_chunk_id"
                        ),

                    "reason":
                        "Conditional pathway does not apply."
                }

            if applicable is None:

                return {
                    "rule_id":
                        rule_id,

                    "parameter":
                        parameter,

                    "status":
                        "UNKNOWN",

                    "action":
                        action,

                    "value":
                        observed,

                    "threshold":
                        threshold,

                    "unit":
                        rule.get(
                            "unit"
                        ),

                    "source_chunk_id":
                        rule.get(
                            "source_chunk_id"
                        ),

                    "reason":
                        (
                            "Cannot determine whether "
                            "conditional rule applies."
                        )
                }

        # --------------------------------------
        # Execute comparison
        # --------------------------------------

        try:

            if (
                operator
                in COLLECTION_OPERATORS
            ):

                matched = (
                    compare_collection(
                        observed,
                        operator,
                        threshold
                    )
                )

            else:

                matched = (
                    compare_scalar(
                        observed,
                        operator,
                        threshold
                    )
                )

        except (
            ValueError,
            TypeError
        ) as error:

            return {
                "rule_id":
                    rule_id,

                "parameter":
                    parameter,

                "status":
                    "UNKNOWN",

                "action":
                    action,

                "value":
                    observed,

                "threshold":
                    threshold,

                "unit":
                    rule.get(
                        "unit"
                    ),

                "source_chunk_id":
                    rule.get(
                        "source_chunk_id"
                    ),

                "reason":
                    f"Comparison failed: {error}"
            }

        # --------------------------------------
        # Interpret REQUIRE
        #
        # For REQUIRE:
        # condition must be TRUE.
        #
        # For EXCLUDE:
        # condition being TRUE is violation.
        # --------------------------------------

        if action == "REQUIRE":

            status = (
                "PASS"
                if matched
                else "VIOLATION"
            )

        elif action in CONDITIONAL_ACTIONS:

            status = (
                "PASS"
                if matched
                else "VIOLATION"
            )

        elif action == "EXCLUDE":

            status = (
                "VIOLATION"
                if matched
                else "PASS"
            )

        else:

            status = (
                "MATCH"
                if matched
                else "PASS"
            )

        return {
            "rule_id":
                rule_id,

            "parameter":
                parameter,

            "status":
                status,

            "action":
                action,

            "value":
                observed,

            "threshold":
                threshold,

            "unit":
                rule.get(
                    "unit"
                ),

            "source_chunk_id":
                rule.get(
                    "source_chunk_id"
                ),

            "reason":
                self._reason(
                    action,
                    matched
                )
        }

    # ==========================================
    # CONDITIONAL APPLICABILITY
    # ==========================================

    @staticmethod
    def _conditional_rule_applies(
        patient,
        action
    ):

        facts = patient.get(
            "protocol_facts",
            {}
        )

        if (
            action
            == "REQUIRE_IF_ACS_PATHWAY"
        ):

            return facts.get(
                "acs_pathway"
            )

        if (
            action
            == "REQUIRE_IF_PCI_PATHWAY"
        ):

            return facts.get(
                "pci_pathway"
            )

        if (
            action
            == "REQUIRE_IF_WOCBP"
        ):

            return facts.get(
                "woman_of_childbearing_potential"
            )

        return None

    # ==========================================
    # COMPOUND DOSAGE RULE
    # ==========================================

    def _evaluate_compound_rule(
        self,
        patient,
        rule
    ):

        conditions = rule.get(
            "conditions",
            []
        )

        required_matches = rule.get(
            "required_matches",
            0
        )

        matches = 0
        unknown = []
        condition_results = []

        for condition in conditions:

            parameter = condition[
                "parameter"
            ]

            observed = (
                resolve_patient_value(
                    patient,
                    parameter
                )
            )

            if observed is MISSING:

                unknown.append(
                    parameter
                )

                condition_results.append({
                    "parameter":
                        parameter,

                    "status":
                        "UNKNOWN"
                })

                continue

            try:

                matched = (
                    compare_scalar(
                        observed,
                        condition[
                            "operator"
                        ],
                        condition[
                            "threshold"
                        ]
                    )
                )

            except (
                ValueError,
                TypeError
            ):

                unknown.append(
                    parameter
                )

                condition_results.append({
                    "parameter":
                        parameter,

                    "status":
                        "UNKNOWN"
                })

                continue

            if matched:
                matches += 1

            condition_results.append({
                "parameter":
                    parameter,

                "value":
                    observed,

                "operator":
                    condition[
                        "operator"
                    ],

                "threshold":
                    condition[
                        "threshold"
                    ],

                "status":
                    (
                        "MATCH"
                        if matched
                        else "NO_MATCH"
                    )
            })

        # Can we already prove >= N criteria?
        if matches >= required_matches:

            dose = rule.get(
                "result_if_true"
            )

            status = "PASS"

            reason = (
                f"{matches} dose-reduction "
                "criteria matched."
            )

        else:

            # Missing fields could still change
            # the answer.

            possible_matches = (
                matches
                + len(unknown)
            )

            if (
                possible_matches
                >= required_matches
            ):

                return {
                    "rule_id":
                        rule["rule_id"],

                    "parameter":
                        rule["parameter"],

                    "status":
                        "UNKNOWN",

                    "action":
                        rule["action"],

                    "value":
                        None,

                    "threshold":
                        None,

                    "unit":
                        None,

                    "source_chunk_id":
                        rule.get(
                            "source_chunk_id"
                        ),

                    "condition_results":
                        condition_results,

                    "reason":
                        (
                            "Missing dose-reduction "
                            "criteria could change "
                            "the required dose."
                        )
                }

            dose = rule.get(
                "result_if_false"
            )

            status = "PASS"

            reason = (
                "Fewer than the required "
                "number of dose-reduction "
                "criteria matched."
            )

        return {
            "rule_id":
                rule["rule_id"],

            "parameter":
                rule["parameter"],

            "status":
                status,

            "action":
                rule["action"],

            "value":
                dose,

            "threshold":
                None,

            "unit":
                (
                    dose.get("unit")
                    if dose
                    else None
                ),

            "source_chunk_id":
                rule.get(
                    "source_chunk_id"
                ),

            "condition_results":
                condition_results,

            "reason":
                reason
        }

    @staticmethod
    def _reason(
        action,
        matched
    ):

        if action == "REQUIRE":

            if matched:
                return (
                    "Required inclusion "
                    "condition is satisfied."
                )

            return (
                "Required inclusion "
                "condition is not satisfied."
            )

        if (
            action
            in CONDITIONAL_ACTIONS
        ):

            if matched:
                return (
                    "Applicable conditional "
                    "requirement is satisfied."
                )

            return (
                "Applicable conditional "
                "requirement is not satisfied."
            )

        if action == "EXCLUDE":

            if matched:
                return (
                    "Exclusion condition "
                    "is present."
                )

            return (
                "Exclusion condition "
                "is not present."
            )

        return (
            "Rule evaluated."
        )


def derive_decision(
    results
):

    # ------------------------------------------
    # Any confirmed eligibility violation
    # results in FAIL.
    # ------------------------------------------

    violation = any(
        result.get("status")
        == "VIOLATION"

        for result
        in results
    )

    if violation:

        return (
            "FAIL",
            "INELIGIBLE",
            False
        )

    # ------------------------------------------
    # Unknown required data means REVIEW.
    # ------------------------------------------

    unknown = any(
        result.get("status")
        == "UNKNOWN"

        for result
        in results
    )

    if unknown:

        return (
            "REVIEW",
            "UNCERTAIN",
            True
        )

    if not results:

        return (
            "REVIEW",
            "UNCERTAIN",
            True
        )

    return (
        "PASS",
        "ELIGIBLE",
        False
    )

