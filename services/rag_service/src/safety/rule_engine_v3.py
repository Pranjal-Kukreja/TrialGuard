from __future__ import annotations
import argparse
import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# CONSTANTS / STATES
# ============================================================

MISSING = object()


class EvaluationState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


ELIGIBLE = "ELIGIBLE"
INELIGIBLE = "INELIGIBLE"
INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


# ============================================================
# PATIENT VALUE RESOLUTION
# ============================================================

def resolve_path(data: Any, path: Optional[str]) -> Any:
    """
    Resolve a dotted path from a nested dictionary.

    Example:
        demographics.age
        lab_results.platelets
        protocol_facts.days_since_pci

    Returns MISSING when the path cannot be resolved.

    IMPORTANT:
    This function does NOT search other branches and does NOT
    infer/guess values.
    """

    if path is None or path == "":
        return MISSING

    current = data

    for part in path.split("."):
        if not isinstance(current, dict):
            return MISSING

        if part not in current:
            return MISSING

        current = current[part]

    return current


def resolve_condition_value(
    patient: Dict[str, Any],
    parent_path: Optional[str],
    field: Optional[str],
) -> Any:
    """
    Resolve a condition field relative to a parent field_path.

    Example:

        parent_path = protocol_facts
        field = prior_mi

    resolves:

        protocol_facts.prior_mi

    If field itself is already dotted, it is treated as an absolute path.
    """

    if not field:
        return MISSING

    if "." in field:
        return resolve_path(patient, field)

    if parent_path:
        full_path = f"{parent_path}.{field}"
        return resolve_path(patient, full_path)

    # No parent path: only use the field as an explicit root path.
    return resolve_path(patient, field)


def unwrap_measurement(value: Any) -> Any:
    """
    Extract the scalar value from a structured clinical measurement.

    Supported:
        42

    and:
        {
            "value": 42,
            "unit": "mL/min"
        }

    Missing or malformed measurements remain unresolved.
    """

    if value is MISSING:
        return MISSING

    if isinstance(value, dict):
        if "value" not in value:
            return MISSING

        return value["value"]

    return value


def get_measurement_unit(value: Any) -> Optional[str]:
    """
    Return an explicit unit from a structured measurement.
    """
    if isinstance(value, dict):
        unit = value.get("unit")

        if isinstance(unit, str):
            return unit

    return None


# ============================================================
# GENERIC COMPARISON
# ============================================================

def compare_values(
    observed: Any,
    operator: str,
    expected: Any,
) -> Optional[bool]:
    """
    Returns:
        True  -> comparison matched
        False -> comparison did not match
        None  -> comparison could not be determined
    """

    if observed is MISSING or observed is None:
        return None

    try:
        if operator == "==":
            return observed == expected

        if operator == "!=":
            return observed != expected

        if operator == ">":
            return observed > expected

        if operator == ">=":
            return observed >= expected

        if operator == "<":
            return observed < expected

        if operator == "<=":
            return observed <= expected

        if operator.upper() == "IN":
            return observed in expected

        if operator.upper() == "NOT_IN":
            return observed not in expected

    except (TypeError, ValueError):
        return None

    return None


# ============================================================
# RESULT HELPERS
# ============================================================

def make_result(
    rule: Dict[str, Any],
    state: EvaluationState,
    reason: str,
    observed: Any = None,
    expected: Any = None,
    condition_results: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:

    result = {
        "rule_id": rule.get("rule_id"),
        "rule_type": rule.get("rule_type"),
        "criterion_type": rule.get("criterion_type"),
        "parameter": rule.get("parameter"),
        "field_path": rule.get("field_path"),
        "source_chunk_id": rule.get("source_chunk_id"),
        "action": rule.get("action"),
        "severity": rule.get("severity"),
        "evidence_required": rule.get("evidence_required", True),
        "state": state.value,
        "reason": reason,
        "observed": observed,
        "expected": expected,
    }

    if condition_results is not None:
        result["condition_results"] = condition_results

    return result


# ============================================================
# INCLUSION RULES
# ============================================================

def evaluate_numeric_range(
    rule: Dict[str, Any],
    patient: Dict[str, Any],
) -> Dict[str, Any]:

    raw_observed = resolve_path(
        patient,
        rule.get("field_path"),
    )

    observed = unwrap_measurement(
        raw_observed
    )

    if observed is MISSING or observed is None:
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            "Required numeric evidence is missing.",
        )

    minimum = rule.get("min")
    maximum = rule.get("max")

    rule_unit = rule.get("unit")
    observed_unit = get_measurement_unit(
        raw_observed
    )

    # If both sides explicitly provide units, do not silently
    # compare measurements whose units disagree.
    if (
        rule_unit
        and observed_unit
        and rule_unit != observed_unit
    ):
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            (
                f"Measurement unit mismatch: observed "
                f"{observed_unit}, expected {rule_unit}."
            ),
            observed=raw_observed,
            expected={
                "min": minimum,
                "max": maximum,
                "unit": rule_unit,
            },
        )

    try:
        if (
            minimum is not None
            and observed < minimum
        ):
            return make_result(
                rule,
                EvaluationState.FAIL,
                (
                    f"Observed value {observed} is below "
                    f"minimum {minimum}."
                ),
                observed=raw_observed,
                expected={
                    "min": minimum,
                    "max": maximum,
                    "unit": rule_unit,
                },
            )

        if (
            maximum is not None
            and observed > maximum
        ):
            return make_result(
                rule,
                EvaluationState.FAIL,
                (
                    f"Observed value {observed} is above "
                    f"maximum {maximum}."
                ),
                observed=raw_observed,
                expected={
                    "min": minimum,
                    "max": maximum,
                    "unit": rule_unit,
                },
            )

    except (TypeError, ValueError):
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            "Numeric evidence exists but could not be compared.",
            observed=raw_observed,
            expected={
                "min": minimum,
                "max": maximum,
                "unit": rule_unit,
            },
        )

    return make_result(
        rule,
        EvaluationState.PASS,
        "Numeric range requirement satisfied.",
        observed=raw_observed,
        expected={
            "min": minimum,
            "max": maximum,
            "unit": rule_unit,
        },
    )


def evaluate_exact_match(
    rule: Dict[str, Any],
    patient: Dict[str, Any],
) -> Dict[str, Any]:

    observed = resolve_path(patient, rule.get("field_path"))
    expected = rule.get("expected")

    if observed is MISSING or observed is None:
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            "Required evidence is missing.",
            expected=expected,
        )

    matched = observed == expected

    return make_result(
        rule,
        EvaluationState.PASS if matched else EvaluationState.FAIL,
        (
            "Expected value matched."
            if matched
            else "Expected value did not match."
        ),
        observed=observed,
        expected=expected,
    )


def evaluate_numeric_window_any(
    rule: Dict[str, Any],
    patient: Dict[str, Any],
) -> Dict[str, Any]:

    conditions = rule.get("conditions", [])
    parent_path = rule.get("field_path")

    condition_results = []

    pass_count = 0
    unknown_count = 0

    for condition in conditions:

        field = condition.get("field")
        operator = condition.get("operator")
        expected = condition.get("value")

        observed = resolve_condition_value(
            patient,
            parent_path,
            field,
        )

        comparison = compare_values(
            observed,
            operator,
            expected,
        )

        if comparison is True:
            state = EvaluationState.PASS
            pass_count += 1

        elif comparison is False:
            state = EvaluationState.FAIL

        else:
            state = EvaluationState.UNKNOWN
            unknown_count += 1

        condition_results.append(
            {
                "field": field,
                "resolved_path": (
                    field
                    if field and "." in field
                    else f"{parent_path}.{field}"
                    if parent_path
                    else field
                ),
                "operator": operator,
                "expected": expected,
                "observed": (
                    None if observed is MISSING else observed
                ),
                "state": state.value,
            }
        )

    # ANY / OR:
    # One confirmed match is enough.
    if pass_count > 0:
        return make_result(
            rule,
            EvaluationState.PASS,
            "At least one numeric window condition matched.",
            condition_results=condition_results,
        )

    # Nothing passed, but at least one condition is unresolved.
    if unknown_count > 0:
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            "No condition was confirmed and one or more conditions lack evidence.",
            condition_results=condition_results,
        )

    return make_result(
        rule,
        EvaluationState.FAIL,
        "None of the numeric window conditions matched.",
        condition_results=condition_results,
    )


def evaluate_inclusion_any(
    rule: Dict[str, Any],
    patient: Dict[str, Any],
) -> Dict[str, Any]:

    parent_path = rule.get("field_path")
    conditions = rule.get("conditions")

    # --------------------------------------------------------
    # MODE 1: conditions array
    # --------------------------------------------------------

    if conditions:

        minimum_matches = rule.get("minimum_matches", 1)

        condition_results = []

        pass_count = 0
        unknown_count = 0

        for condition in conditions:

            field = condition.get("field")
            operator = condition.get("operator")
            expected = condition.get("value")

            observed = resolve_condition_value(
                patient,
                parent_path,
                field,
            )

            comparison = compare_values(
                observed,
                operator,
                expected,
            )

            if comparison is True:
                state = EvaluationState.PASS
                pass_count += 1

            elif comparison is False:
                state = EvaluationState.FAIL

            else:
                state = EvaluationState.UNKNOWN
                unknown_count += 1

            condition_results.append(
                {
                    "field": field,
                    "operator": operator,
                    "expected": expected,
                    "observed": (
                        None if observed is MISSING else observed
                    ),
                    "state": state.value,
                }
            )

        if pass_count >= minimum_matches:
            return make_result(
                rule,
                EvaluationState.PASS,
                (
                    f"{pass_count} condition(s) matched; "
                    f"{minimum_matches} required."
                ),
                condition_results=condition_results,
            )

        # Could missing evidence still make the rule pass?
        if pass_count + unknown_count >= minimum_matches:
            return make_result(
                rule,
                EvaluationState.UNKNOWN,
                "Missing evidence could affect the inclusion-any result.",
                condition_results=condition_results,
            )

        return make_result(
            rule,
            EvaluationState.FAIL,
            (
                f"Only {pass_count} condition(s) matched; "
                f"{minimum_matches} required."
            ),
            condition_results=condition_results,
        )

    # --------------------------------------------------------
    # MODE 2: required_values
    # Used by ATLAS antiplatelet rule
    # --------------------------------------------------------

    required_values = rule.get("required_values", [])

    observed = resolve_path(
        patient,
        rule.get("field_path"),
    )

    if observed is MISSING or observed is None:
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            "Required collection evidence is missing.",
            expected=required_values,
        )

    if isinstance(observed, str):
        observed_values = [observed]

    elif isinstance(observed, (list, tuple, set)):
        observed_values = list(observed)

    else:
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            "Observed value is not a supported collection.",
            observed=observed,
            expected=required_values,
        )

    matched_values = [
        value
        for value in required_values
        if value in observed_values
    ]

    if matched_values:
        return make_result(
            rule,
            EvaluationState.PASS,
            "At least one required value is present.",
            observed=observed_values,
            expected=required_values,
        )

    return make_result(
        rule,
        EvaluationState.FAIL,
        "None of the required values are present.",
        observed=observed_values,
        expected=required_values,
    )


def evaluate_compound(
    rule: Dict[str, Any],
    patient: Dict[str, Any],
) -> Dict[str, Any]:

    conditions = rule.get("conditions", [])
    operator = rule.get("operator", "AND").upper()
    parent_path = rule.get("field_path")

    condition_results = []

    pass_count = 0
    fail_count = 0
    unknown_count = 0

    for condition in conditions:

        field = condition.get("field")
        comparison_operator = condition.get("operator")
        expected = condition.get("value")

        observed = resolve_condition_value(
            patient,
            parent_path,
            field,
        )

        comparison = compare_values(
            observed,
            comparison_operator,
            expected,
        )

        if comparison is True:
            state = EvaluationState.PASS
            pass_count += 1

        elif comparison is False:
            state = EvaluationState.FAIL
            fail_count += 1

        else:
            state = EvaluationState.UNKNOWN
            unknown_count += 1

        condition_results.append(
            {
                "field": field,
                "operator": comparison_operator,
                "expected": expected,
                "observed": (
                    None if observed is MISSING else observed
                ),
                "state": state.value,
            }
        )

    # --------------------------------------------------------
    # AND
    # --------------------------------------------------------

    if operator == "AND":

        if fail_count > 0:
            return make_result(
                rule,
                EvaluationState.FAIL,
                "One or more compound AND conditions failed.",
                condition_results=condition_results,
            )

        if unknown_count > 0:
            return make_result(
                rule,
                EvaluationState.UNKNOWN,
                "One or more compound AND conditions lack evidence.",
                condition_results=condition_results,
            )

        return make_result(
            rule,
            EvaluationState.PASS,
            "All compound AND conditions passed.",
            condition_results=condition_results,
        )

    # --------------------------------------------------------
    # OR
    # --------------------------------------------------------

    if operator == "OR":

        if pass_count > 0:
            return make_result(
                rule,
                EvaluationState.PASS,
                "At least one compound OR condition passed.",
                condition_results=condition_results,
            )

        if unknown_count > 0:
            return make_result(
                rule,
                EvaluationState.UNKNOWN,
                "Compound OR result cannot be determined from available evidence.",
                condition_results=condition_results,
            )

        return make_result(
            rule,
            EvaluationState.FAIL,
            "All compound OR conditions failed.",
            condition_results=condition_results,
        )

    return make_result(
        rule,
        EvaluationState.UNKNOWN,
        f"Unsupported compound operator: {operator}",
        condition_results=condition_results,
    )


# ============================================================
# EXCLUSION RULES
#
# PASS = exclusion NOT triggered
# FAIL = exclusion IS triggered
# UNKNOWN = cannot determine
# ============================================================

def evaluate_numeric_exclusion(
    rule: Dict[str, Any],
    patient: Dict[str, Any],
) -> Dict[str, Any]:

    raw_observed = resolve_path(
        patient,
        rule.get("field_path"),
    )

    observed = unwrap_measurement(
        raw_observed
    )

    threshold = rule.get("threshold")
    operator = rule.get("operator")
    rule_unit = rule.get("unit")

    if observed is MISSING or observed is None:
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            "Exclusion evidence is missing.",
            expected={
                "operator": operator,
                "threshold": threshold,
                "unit": rule_unit,
            },
        )

    observed_unit = get_measurement_unit(
        raw_observed
    )

    if (
        rule_unit
        and observed_unit
        and rule_unit != observed_unit
    ):
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            (
                f"Measurement unit mismatch: observed "
                f"{observed_unit}, expected {rule_unit}."
            ),
            observed=raw_observed,
            expected={
                "operator": operator,
                "threshold": threshold,
                "unit": rule_unit,
            },
        )

    triggered = compare_values(
        observed,
        operator,
        threshold,
    )

    if triggered is None:
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            "Exclusion evidence could not be compared.",
            observed=raw_observed,
            expected={
                "operator": operator,
                "threshold": threshold,
                "unit": rule_unit,
            },
        )

    if triggered:
        return make_result(
            rule,
            EvaluationState.FAIL,
            "Exclusion criterion triggered.",
            observed=raw_observed,
            expected={
                "operator": operator,
                "threshold": threshold,
                "unit": rule_unit,
            },
        )

    return make_result(
        rule,
        EvaluationState.PASS,
        "Exclusion criterion not triggered.",
        observed=raw_observed,
        expected={
            "operator": operator,
            "threshold": threshold,
            "unit": rule_unit,
        },
    )


def evaluate_exact_exclusion(
    rule: Dict[str, Any],
    patient: Dict[str, Any],
) -> Dict[str, Any]:

    observed = resolve_path(
        patient,
        rule.get("field_path"),
    )

    disallowed = rule.get("disallowed_value")

    if observed is MISSING:
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            "Exclusion evidence is missing.",
            expected=disallowed,
        )

    triggered = observed == disallowed

    if triggered:
        return make_result(
            rule,
            EvaluationState.FAIL,
            "Disallowed value is present; exclusion triggered.",
            observed=observed,
            expected=disallowed,
        )

    return make_result(
        rule,
        EvaluationState.PASS,
        "Disallowed value is not present.",
        observed=observed,
        expected=disallowed,
    )


def evaluate_exclusion_any(
    rule: Dict[str, Any],
    patient: Dict[str, Any],
) -> Dict[str, Any]:

    observed = resolve_path(
        patient,
        rule.get("field_path"),
    )

    disallowed_values = rule.get(
        "disallowed_values",
        [],
    )

    if observed is MISSING or observed is None:
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            "Collection evidence for exclusion is missing.",
            expected=disallowed_values,
        )

    if isinstance(observed, str):
        observed_values = [observed]

    elif isinstance(observed, (list, tuple, set)):
        observed_values = list(observed)

    elif isinstance(observed, dict):
        # Only use explicit values from the dictionary.
        observed_values = [
            value
            for value in observed.values()
            if isinstance(value, str)
        ]

    else:
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            "Observed exclusion value is not a supported collection.",
            observed=observed,
            expected=disallowed_values,
        )

    matches = [
        value
        for value in disallowed_values
        if value in observed_values
    ]

    if matches:
        return make_result(
            rule,
            EvaluationState.FAIL,
            f"Disallowed value(s) found: {matches}",
            observed=observed_values,
            expected=disallowed_values,
        )

    return make_result(
        rule,
        EvaluationState.PASS,
        "No disallowed values were found.",
        observed=observed_values,
        expected=disallowed_values,
    )


def evaluate_clinical_condition_exclusion(
    rule: Dict[str, Any],
    patient: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Evaluate an explicitly represented boolean clinical condition.

    Supports either:
        field_path = "medical_history"
        parameter = "significant_renal_or_liver_disease"

    resulting in:
        medical_history.significant_renal_or_liver_disease

    OR an already-complete path:
        field_path = "protocol_facts.unacceptable_bleeding_risk"

    No fuzzy matching or clinical inference is performed.
    """

    field_path = rule.get("field_path")
    parameter = rule.get("parameter")
    disallowed = rule.get("disallowed_value", True)

    if not field_path:
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            "Clinical condition rule has no field_path.",
            expected=disallowed,
        )

    # If field_path already ends with the parameter, it is
    # already the complete path.
    if (
        parameter
        and field_path.split(".")[-1] == parameter
    ):
        explicit_path = field_path

    elif parameter:
        explicit_path = f"{field_path}.{parameter}"

    else:
        explicit_path = field_path

    observed = resolve_path(
        patient,
        explicit_path,
    )

    if observed is MISSING:
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            (
                "Clinical condition evidence is missing at "
                f"{explicit_path}."
            ),
            expected=disallowed,
        )

    triggered = observed == disallowed

    if triggered:
        return make_result(
            rule,
            EvaluationState.FAIL,
            "Clinical exclusion condition is present.",
            observed=observed,
            expected=disallowed,
        )

    return make_result(
        rule,
        EvaluationState.PASS,
        "Clinical exclusion condition is not present.",
        observed=observed,
        expected=disallowed,
    )
# ============================================================
# RULE DISPATCH
# ============================================================

RULE_EVALUATORS = {
    "numeric_range": evaluate_numeric_range,
    "exact_match": evaluate_exact_match,
    "numeric_window_any": evaluate_numeric_window_any,
    "inclusion_any": evaluate_inclusion_any,
    "compound": evaluate_compound,
    "numeric_exclusion": evaluate_numeric_exclusion,
    "exact_exclusion": evaluate_exact_exclusion,
    "exclusion_any": evaluate_exclusion_any,
    "clinical_condition_exclusion": evaluate_clinical_condition_exclusion,
}


def evaluate_rule(
    rule: Dict[str, Any],
    patient: Dict[str, Any],
) -> Dict[str, Any]:

    rule_type = rule.get("rule_type")

    evaluator = RULE_EVALUATORS.get(rule_type)

    if evaluator is None:
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            f"Unsupported rule type: {rule_type}",
        )

    try:
        return evaluator(rule, patient)

    except Exception as exc:
        # Do not accidentally turn evaluator errors into eligibility.
        return make_result(
            rule,
            EvaluationState.UNKNOWN,
            f"Rule evaluation error: {type(exc).__name__}: {exc}",
        )


# ============================================================
# TRIAL AGGREGATION
# ============================================================

def _evaluate_trial_definition(
    trial_id: str,
    trial: Dict[str, Any],
    patient: Dict[str, Any],
) -> Dict[str, Any]:

    rules = trial.get("rules", [])

    results = [
        evaluate_rule(rule, patient)
        for rule in rules
    ]

    inclusion_results = [
        result
        for result in results
        if result.get("criterion_type") == "inclusion"
    ]

    exclusion_results = [
        result
        for result in results
        if result.get("criterion_type") == "exclusion"
    ]

    # --------------------------------------------------------
    # 1. Definitive exclusion wins.
    # --------------------------------------------------------

    triggered_exclusions = [
        result
        for result in exclusion_results
        if result["state"] == EvaluationState.FAIL.value
    ]

    if triggered_exclusions:
        status = INELIGIBLE
        decision_reason = (
            "At least one exclusion criterion was definitively triggered."
        )

    else:

        # ----------------------------------------------------
        # 2. Failed required inclusion -> INELIGIBLE
        # ----------------------------------------------------

        failed_inclusions = [
            result
            for result in inclusion_results
            if result["state"] == EvaluationState.FAIL.value
        ]

        if failed_inclusions:
            status = INELIGIBLE
            decision_reason = (
                "At least one required inclusion criterion was not satisfied."
            )

        else:

            # ------------------------------------------------
            # 3. Missing/unknown required evidence
            # ------------------------------------------------

            unresolved = [
                result
                for result in results
                if (
                    result["state"]
                    == EvaluationState.UNKNOWN.value
                    and result.get(
                        "evidence_required",
                        True,
                    )
                )
            ]

            if unresolved:
                status = INSUFFICIENT_EVIDENCE
                decision_reason = (
                    "One or more required criteria could not be "
                    "determined from available evidence."
                )

            else:

                # --------------------------------------------
                # 4. Everything required is satisfied.
                # --------------------------------------------

                status = ELIGIBLE
                decision_reason = (
                    "All required inclusion criteria were satisfied "
                    "and no exclusion criterion was triggered."
                )

    return {
        "trial_id": trial_id,
        "trial_name": trial.get("name"),
        "support_level": trial.get("support_level"),
        "status": status,
        "reason": decision_reason,
        "summary": {
            "total_rules": len(results),
            "inclusion_rules": len(inclusion_results),
            "exclusion_rules": len(exclusion_results),
            "pass": sum(
                r["state"] == EvaluationState.PASS.value
                for r in results
            ),
            "fail": sum(
                r["state"] == EvaluationState.FAIL.value
                for r in results
            ),
            "unknown": sum(
                r["state"] == EvaluationState.UNKNOWN.value
                for r in results
            ),
        },
        "rule_results": results,
    }


def evaluate_trial(
    trial_id: str,
    patient: Dict[str, Any],
    rules_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """
    Programmatic entry point for evaluating one trial.

    The adapter loads the rules document, selects ``trial_id``, and
    returns that trial's eligibility result without invoking the CLI.

    The legacy three-argument form ``(trial_id, trial, patient)`` is
    still accepted for compatibility with existing callers.
    """

    if isinstance(rules_path, dict):
        return _evaluate_trial_definition(
            trial_id,
            patient,
            rules_path,
        )

    if rules_path is None:
        rules_file = (
            Path(__file__).resolve().parents[2]
            / "data"
            / "processed"
            / "rules"
            / "rules.json"
        )
    else:
        rules_file = Path(rules_path)

        if not rules_file.is_absolute():
            rules_file = (
                Path(__file__).resolve().parents[2]
                / rules_file
            )

    rules_document = load_json(rules_file)
    trial = rules_document.get("trials", {}).get(trial_id)

    if trial is None:
        raise KeyError(
            f"Trial not found in rules document: {trial_id}"
        )

    return _evaluate_trial_definition(
        trial_id,
        trial,
        patient,
    )


# ============================================================
# ALL TRIALS
# ============================================================

def evaluate_all_trials(
    rules_document: Dict[str, Any],
    patient: Dict[str, Any],
) -> Dict[str, Any]:

    trials = rules_document.get("trials", {})

    trial_results = {}

    for trial_id, trial in trials.items():
        trial_results[trial_id] = _evaluate_trial_definition(
            trial_id,
            trial,
            patient,
        )

    return {
        "schema_version": rules_document.get(
            "schema_version"
        ),
        "patient_id": (
            patient.get("patient_id")
            or patient.get("id")
        ),
        "trials": trial_results,
    }


# ============================================================
# FILE LOADING
# ============================================================

def load_json(path: Path) -> Dict[str, Any]:

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_rules(
    path: Path = Path(
        "data/processed/rules/rules.json"
    ),
) -> Dict[str, Any]:

    return load_json(path)


# ============================================================
# COMMAND-LINE TEST
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "TrialGuard Patient-to-Trial "
            "Eligibility Engine V3"
        )
    )

    parser.add_argument(
        "--patient",
        default="data/processed/test_patient_normalized.json",
        help="Path to patient JSON relative to project root.",
    )

    parser.add_argument(
        "--rules",
        default="data/processed/rules/rules.json",
        help="Path to rules JSON relative to project root.",
    )

    parser.add_argument(
        "--output",
        default="data/processed/eligibility_result_v3.json",
        help="Output JSON path relative to project root.",
    )

    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]

    rules_path = project_root / args.rules
    patient_path = project_root / args.patient
    output_path = project_root / args.output

    print("=" * 70)
    print("TrialGuard Eligibility Engine V3")
    print("=" * 70)

    print(f"\nRules:   {rules_path}")
    print(f"Patient: {patient_path}")

    if not rules_path.exists():
        raise FileNotFoundError(
            f"Rules file not found: {rules_path}"
        )

    if not patient_path.exists():
        raise FileNotFoundError(
            f"Patient file not found: {patient_path}"
        )

    rules_document = load_json(
        rules_path
    )

    patient = load_json(
        patient_path
    )

    result = evaluate_all_trials(
        rules_document,
        patient,
    )

    print("\nRESULTS")
    print("-" * 70)

    for trial_id, trial_result in result["trials"].items():

        print(
            f"\n{trial_id} - "
            f"{trial_result['trial_name']}"
        )

        print(
            f"Status: {trial_result['status']}"
        )

        print(
            f"Reason: {trial_result['reason']}"
        )

        summary = trial_result["summary"]

        print(
            "Rules: "
            f"{summary['total_rules']} total, "
            f"{summary['pass']} PASS, "
            f"{summary['fail']} FAIL, "
            f"{summary['unknown']} UNKNOWN"
        )

        print("\nRule details:")

        for rule_result in trial_result["rule_results"]:
            print(
                f"  {rule_result['rule_id']}: "
                f"{rule_result['state']} - "
                f"{rule_result['reason']}"
            )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("\n" + "=" * 70)
    print(f"Full result written to:\n{output_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()