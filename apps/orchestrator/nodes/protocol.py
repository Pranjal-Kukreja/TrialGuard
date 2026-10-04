"""
Protocol baseline verification (Guardrail 2) and ClinicalTrials.gov status checks.

Updated to synchronize with the complete HITL & Audit pipeline:
  - Universal Review Integration: Non-catastrophic protocol violations, deviations,
    and soft violations defer to the HITL escalation stage rather than preemptively
    short-circuiting prior to multi-agent adjudication.
  - Catastrophic G2 Boundary Guards: Reserves hard short-circuiting strictly for 
    life-threatening laboratory and physiological safety breaches.
  - Canonical CriterionRecord & ProtocolViolation field normalization (syncs observed,
    expected, difference, parameter, and rule_id).
  - Preserves retrospective clinical evaluation for completed benchmarks ('COMPLETED', 'ACTIVE_NOT_RECRUITING').
"""

import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional
import requests
from shared_schemas.state import TrialState

try:
    from shared_schemas.rules import get_protocol_rules
except ImportError:
    try:
        from apps.orchestrator.rules import get_protocol_rules
    except ImportError:
        from rules import get_protocol_rules

NCT_REGEX = re.compile(r"^NCT\d{8}$", re.IGNORECASE)

KNOWN_RULE_TYPES = {
    "numeric_range",
    "exclusion_list",
    "inclusion_list",
    "exact_match",
    "empty_list",
    "date_since_gte",
}

ALL_CLINICAL_TRIALS_STATUSES = {
    "ACTIVE",
    "ACTIVE_NOT_RECRUITING",
    "COMPLETED",
    "ENROLLING_BY_INVITATION",
    "NOT_YET_RECRUITING",
    "RECRUITING",
    "SUSPENDED",
    "TERMINATED",
    "WITHDRAWN",
    "AVAILABLE",
    "NO_LONGER_AVAILABLE",
    "TEMPORARILY_NOT_AVAILABLE",
    "APPROVED_FOR_MARKETING",
    "WITHDRAWN_BEFORE_ENROLLMENT",
    "OPEN",
    "UNKNOWN",
}

OPEN_RECRUITING_STATUSES = {
    "RECRUITING",
    "NOT_YET_RECRUITING",
    "ENROLLING_BY_INVITATION",
    "OPEN",
    "ACTIVE",
}

EVALUABLE_BENCHMARK_STATUSES = OPEN_RECRUITING_STATUSES | {
    "COMPLETED",
    "ACTIVE_NOT_RECRUITING",
}

TERMINAL_CLOSED_STATUSES = ALL_CLINICAL_TRIALS_STATUSES - EVALUABLE_BENCHMARK_STATUSES

# Catastrophic safety identifiers that warrant hard short-circuiting prior to sub-agent evaluation
CATASTROPHIC_SAFETY_PREFIXES = ("SAFETY_HEPATIC_", "SAFETY_RENAL_", "SAFETY_HEME_", "SAFETY_CARDIAC_")


def fetch_protocol_rules(trial_id: str) -> List[Dict[str, Any]]:
    return get_protocol_rules(trial_id)


def extract_nested_value(data: Dict[str, Any], path: Any) -> Any:
    """
    Extracts a value given a dot-delimited path or list.
    Supports auto-discovery across common patient sub-dictionaries 
    ('protocol_facts', 'lab_results', 'vital_signs', 'cardiac_function')
    and handles list indexing safely.
    """
    if isinstance(path, str):
        path = path.split(".")
    if not isinstance(path, list):
        return None

    curr = data
    for key in path:
        if isinstance(curr, dict) and key in curr:
            curr = curr[key]
        elif isinstance(curr, list) and key.isdigit() and int(key) < len(curr):
            curr = curr[int(key)]
        else:
            curr = None
            break

    # Fallback 1: Check standard nested buckets
    if curr is None:
        terminal_key = path[-1]
        for bucket in ("protocol_facts", "lab_results", "vital_signs", "cardiac_function"):
            sub_dict = data.get(bucket)
            if isinstance(sub_dict, dict) and terminal_key in sub_dict:
                curr = sub_dict[terminal_key]
                break

    # Fallback 2: Check top-level
    if curr is None and len(path) > 1:
        last_key = path[-1]
        if last_key in data:
            curr = data[last_key]

    # Unwrap {'value': ..., 'unit': ...} dicts
    if isinstance(curr, dict) and "value" in curr:
        return curr["value"]

    return curr


def _rule_applies(rule: Dict[str, Any], patient: Dict[str, Any]) -> bool:
    conditions = rule.get("applies_if")
    if not conditions:
        return True

    for path, expected in conditions.items():
        actual = extract_nested_value(patient, path)
        if actual is None or str(actual).lower() != str(expected).lower():
            return False
    return True


def _validate_rule(rule: Dict[str, Any]) -> Optional[str]:
    rule_type = rule.get("rule_type")
    if rule_type not in KNOWN_RULE_TYPES:
        return f"unsupported or missing rule_type: '{rule_type}'"
    if rule_type == "numeric_range" and rule.get("min") is None and rule.get("max") is None:
        return "numeric_range rule defines neither 'min' nor 'max'"
    if rule_type == "exclusion_list" and not rule.get("disallowed_values"):
        return "exclusion_list rule missing a non-empty 'disallowed_values'"
    if rule_type == "inclusion_list" and not rule.get("required_values"):
        return "inclusion_list rule missing a non-empty 'required_values'"
    if rule_type == "exact_match" and "expected" not in rule:
        return "exact_match rule missing an 'expected' value"
    if rule_type == "date_since_gte" and rule.get("min_days") is None:
        return "date_since_gte rule missing 'min_days'"
    return None


def protocol_verification_node(state: TrialState) -> Dict[str, Any]:
    """
    Guardrail 2 (G2): Baseline Safety & Protocol Rule Verification.
    
    Inspects upstream `rag_analysis` findings and evaluates baseline criteria.
    Permits protocol deviations (e.g., PCI timing, dosing adjustments) to proceed
    to sub-agent evaluation and downstream clinician HITL review.
    """
    trial_id = state.get("trial_id") or "UNKNOWN_TRIAL"
    patient = state.get("patient") or state.get("raw_fhir_patient") or {}
    rules = state.get("protocol_rules") or fetch_protocol_rules(trial_id)
    rag_analysis = state.get("rag_analysis") or {}

    # Isolate new findings to avoid exponential reducer duplication
    new_violations: List[Dict[str, Any]] = []
    new_matched: List[Dict[str, Any]] = []
    new_unknown: List[Dict[str, Any]] = []
    not_applicable_criteria: List[Dict[str, Any]] = []
    evidence_chunks: List[Dict[str, Any]] = []

    # Track already evaluated rules from state and RAG analysis
    seen_rule_ids = set()
    for v in state.get("violations", []):
        seen_rule_ids.add(v.get("rule_id"))
    for m in state.get("matched_criteria", []):
        seen_rule_ids.add(m.get("rule_id"))
    for u in state.get("unknown_criteria", []):
        seen_rule_ids.add(u.get("rule_id"))

    # Ingest from current rag_analysis payload if not yet tracked
    if rag_analysis.get("violations"):
        for v in rag_analysis["violations"]:
            r_id = v.get("rule_id")
            if r_id not in seen_rule_ids:
                v_dict = dict(v)
                if v_dict.get("observed") is None and v_dict.get("value") is not None:
                    v_dict["observed"] = v_dict["value"]
                new_violations.append(v_dict)
                seen_rule_ids.add(r_id)

    if rag_analysis.get("matched_criteria"):
        for m in rag_analysis["matched_criteria"]:
            r_id = m.get("rule_id")
            if r_id not in seen_rule_ids:
                m_dict = dict(m)
                if m_dict.get("observed") is None and m_dict.get("value") is not None:
                    m_dict["observed"] = m_dict["value"]
                new_matched.append(m_dict)
                seen_rule_ids.add(r_id)

    if rag_analysis.get("unknown_criteria"):
        for u in rag_analysis["unknown_criteria"]:
            r_id = u.get("rule_id")
            if r_id not in seen_rule_ids:
                new_unknown.append(dict(u))
                seen_rule_ids.add(r_id)

    # 2. Evaluate remaining Baseline & Trial Protocol Rules
    for idx, rule in enumerate(rules):
        rule_id = rule.get("rule_id") or f"RULE_{idx}"
        if rule_id in seen_rule_ids:
            continue

        param = rule.get("parameter", "unknown_parameter")
        field_path = rule.get("field_path", param)
        rule_type = rule.get("rule_type")
        unit = rule.get("unit", "")
        severity = rule.get("severity", "HARD")
        action = rule.get("action", "EXCLUDE")
        chunk_id = rule.get("source_chunk_id", f"{trial_id}-eligibility-{idx:03d}")

        if rule.get("evidence"):
            evidence_chunks.append(rule["evidence"])

        validation_error = _validate_rule(rule)
        if validation_error:
            new_unknown.append({
                "rule_id": rule_id,
                "criterion": param,
                "reason": f"Misconfigured rule '{rule_id}': {validation_error}.",
                "source_chunk_id": chunk_id,
                "result": "UNKNOWN",
            })
            continue

        if not _rule_applies(rule, patient):
            not_applicable_criteria.append({
                "rule_id": rule_id,
                "criterion": param,
                "reason": "Rule condition 'applies_if' not met for patient.",
            })
            continue

        try:
            val = extract_nested_value(patient, field_path)

            if val is None:
                formatted_path = field_path if isinstance(field_path, str) else ".".join(field_path)
                new_unknown.append({
                    "rule_id": rule_id,
                    "criterion": param,
                    "field_path": formatted_path,
                    "observed": None,
                    "expected": rule.get("expected") or rule.get("min") or rule.get("max"),
                    "source_chunk_id": chunk_id,
                    "reason": f"Parameter '{param}' (path: {formatted_path}) missing from patient payload.",
                    "result": "UNKNOWN",
                })
                continue

            if rule_type == "numeric_range":
                try:
                    num_val = float(val)
                except (ValueError, TypeError):
                    new_unknown.append({
                        "rule_id": rule_id,
                        "criterion": param,
                        "observed": val,
                        "source_chunk_id": chunk_id,
                        "reason": f"Parameter '{param}' expected numeric value, got: '{val}'.",
                        "result": "UNKNOWN",
                    })
                    continue

                max_val = rule.get("max")
                min_val = rule.get("min")

                if max_val is not None and num_val > float(max_val):
                    diff_amt = round(num_val - float(max_val), 2)
                    reason_str = f"{param} ({num_val} {unit}) exceeds max threshold of {max_val} {unit}."
                    new_violations.append({
                        "rule_id": rule_id,
                        "parameter": param,
                        "field_path": field_path,
                        "value": num_val,
                        "observed": num_val,
                        "threshold": {"max": float(max_val), "unit": unit},
                        "expected": {"max": float(max_val), "unit": unit},
                        "difference": {"amount": diff_amt, "boundary": float(max_val), "direction": "above_maximum"},
                        "unit": unit,
                        "severity": severity,
                        "action": action,
                        "source_chunk_id": chunk_id,
                        "reason": reason_str,
                    })
                elif min_val is not None and num_val < float(min_val):
                    diff_amt = round(num_val - float(min_val), 2)
                    reason_str = f"{param} ({num_val} {unit}) is below min threshold of {min_val} {unit}."
                    new_violations.append({
                        "rule_id": rule_id,
                        "parameter": param,
                        "field_path": field_path,
                        "value": num_val,
                        "observed": num_val,
                        "threshold": {"min": float(min_val), "unit": unit},
                        "expected": {"min": float(min_val), "unit": unit},
                        "difference": {"amount": diff_amt, "boundary": float(min_val), "direction": "below_minimum"},
                        "unit": unit,
                        "severity": severity,
                        "action": action,
                        "source_chunk_id": chunk_id,
                        "reason": reason_str,
                    })
                else:
                    new_matched.append({
                        "rule_id": rule_id,
                        "criterion": param,
                        "result": "PASS",
                        "value": num_val,
                        "observed": num_val,
                        "threshold": {"min": min_val, "max": max_val, "unit": unit},
                        "reason": f"{param} satisfies required safety range.",
                    })

            elif rule_type == "exclusion_list":
                disallowed = [str(d).lower() for d in rule.get("disallowed_values", [])]
                patient_items = [str(i).lower() for i in val] if isinstance(val, list) else [str(val).lower()]
                found_violations = [item for item in patient_items if item in disallowed]

                if found_violations:
                    for violation_item in found_violations:
                        reason_str = f"{param} contains prohibited entry: '{violation_item}'."
                        new_violations.append({
                            "rule_id": rule_id,
                            "parameter": param,
                            "field_path": field_path,
                            "value": violation_item,
                            "observed": violation_item,
                            "severity": severity,
                            "action": action,
                            "source_chunk_id": chunk_id,
                            "reason": reason_str,
                        })
                else:
                    new_matched.append({
                        "rule_id": rule_id,
                        "criterion": param,
                        "result": "PASS",
                        "value": val,
                        "observed": val,
                        "reason": f"No prohibited entries found for {param}.",
                    })

            elif rule_type == "exact_match":
                expected = rule.get("expected")
                if str(val).lower() != str(expected).lower():
                    reason_str = f"{param} '{val}' does not match required value '{expected}'."
                    new_violations.append({
                        "rule_id": rule_id,
                        "parameter": param,
                        "field_path": field_path,
                        "value": val,
                        "observed": val,
                        "expected": expected,
                        "severity": severity,
                        "action": action,
                        "source_chunk_id": chunk_id,
                        "reason": reason_str,
                    })
                else:
                    new_matched.append({
                        "rule_id": rule_id,
                        "criterion": param,
                        "result": "PASS",
                        "value": val,
                        "observed": val,
                        "threshold": {"expected": expected},
                        "reason": f"{param} matches expected value.",
                    })

            elif rule_type == "empty_list":
                items = val if isinstance(val, list) else ([val] if val else [])
                if items:
                    reason_str = f"{param} contains contraindicated entries: {items}."
                    new_violations.append({
                        "rule_id": rule_id,
                        "parameter": param,
                        "field_path": field_path,
                        "value": items,
                        "observed": items,
                        "severity": severity,
                        "action": action,
                        "source_chunk_id": chunk_id,
                        "reason": reason_str,
                    })
                else:
                    new_matched.append({
                        "rule_id": rule_id,
                        "criterion": param,
                        "result": "PASS",
                        "value": [],
                        "observed": [],
                        "reason": f"No contraindicated entries for {param}.",
                    })

            elif rule_type == "date_since_gte":
                try:
                    date_str = str(val).split("T")[0].strip()
                    reference_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    new_unknown.append({
                        "rule_id": rule_id,
                        "criterion": param,
                        "observed": val,
                        "source_chunk_id": chunk_id,
                        "reason": f"Expected ISO date, got: '{val}'.",
                        "result": "UNKNOWN",
                    })
                    continue

                days_elapsed = (date.today() - reference_date).days
                min_days = rule.get("min_days", 0)

                if days_elapsed < min_days:
                    reason_str = f"Only {days_elapsed} day(s) elapsed, requires minimum {min_days}-day washout."
                    new_violations.append({
                        "rule_id": rule_id,
                        "parameter": param,
                        "field_path": field_path,
                        "value": days_elapsed,
                        "observed": days_elapsed,
                        "threshold": {"min_days": min_days},
                        "severity": severity,
                        "action": action,
                        "source_chunk_id": chunk_id,
                        "reason": reason_str,
                    })
                else:
                    new_matched.append({
                        "rule_id": rule_id,
                        "criterion": param,
                        "result": "PASS",
                        "value": days_elapsed,
                        "observed": days_elapsed,
                        "reason": f"{param} satisfies minimum washout period.",
                    })

        except Exception as exc:
            new_unknown.append({
                "rule_id": rule_id,
                "criterion": param,
                "source_chunk_id": chunk_id,
                "reason": f"Unexpected error during evaluation: {exc}",
                "result": "UNKNOWN",
            })

    # Consolidate all historical and newly uncovered violations
    total_violations = state.get("violations", []) + new_violations
    total_unknown = state.get("unknown_criteria", []) + new_unknown

    has_catastrophic_failure = any(
        v.get("rule_id", "").startswith(CATASTROPHIC_SAFETY_PREFIXES) for v in total_violations
    )
    has_violations = len(total_violations) > 0
    decision = "FAIL" if has_violations else "PASS"
    eligibility = "INELIGIBLE" if has_violations else "ELIGIBLE"

    if has_violations:
        explanation = f"Protocol deviations noted: {total_violations[0]['reason']}"
    elif total_unknown:
        explanation = f"Eligibility indeterminate: {len(total_unknown)} criteria unresolved."
    else:
        explanation = "Patient satisfies baseline safety and protocol criteria."

    base_confidence = 0.96
    confidence_penalty = (len(total_unknown) * 0.08) + (0.05 if has_violations else 0.0)
    confidence = max(0.40, round(base_confidence - confidence_penalty, 2)) if (total_unknown or has_violations) else base_confidence

    requires_hitl = bool(total_unknown or has_violations)
    hitl_reason = None
    if requires_hitl:
        if total_unknown:
            hitl_reason = f"Indeterminate criteria ({len(total_unknown)} missing parameters)."
        elif has_violations:
            hitl_reason = f"Protocol deviation requiring review: {total_violations[0]['reason']}"
        else:
            hitl_reason = f"Adjudication confidence below safety threshold ({confidence:.2f} < 0.85)."

    audit_entry = {
        "step": "protocol_verification",
        "status": "failed" if has_violations else "passed",
        "new_violations_count": len(new_violations),
        "total_violations_count": len(total_violations),
        "catastrophic_failure": has_catastrophic_failure,
        "confidence": confidence,
        "requires_hitl": requires_hitl,
    }

    # Only new_* delta items returned to prevent exponential duplicate appending by LangGraph reducers
    return {
        "trial_id": trial_id,
        "decision": decision,
        "eligibility": eligibility,
        "guardrail_2_passed": not has_catastrophic_failure,
        "violations": new_violations,
        "matched_criteria": new_matched,
        "unknown_criteria": new_unknown,
        "not_applicable_criteria": not_applicable_criteria,
        "evidence": evidence_chunks,
        "explanation": explanation,
        "confidence": confidence,
        "needs_human_review": requires_hitl,
        "requires_hitl": requires_hitl,
        "hitl_reason": hitl_reason,
        "is_short_circuited": has_catastrophic_failure,
        "active_evaluation_stage": "protocol_boundaries_verified",
        "audit_logs": [audit_entry],
    }


def route_after_g2(state: TrialState) -> str:
    """Routes to short-circuit ONLY on catastrophic failures; otherwise continues to trial status check."""
    if state.get("is_short_circuited") or not state.get("guardrail_2_passed", True):
        return "short_circuit_node"
    return "clinical_trial_status_check"


def short_circuit_node(state: TrialState) -> Dict[str, Any]:
    """Catastrophic safety exit: Marks ineligibility and routes directly to terminal audit."""
    violations = state.get("violations", [])
    trial_status = state.get("trial_status")

    if violations:
        terminal_reason = "catastrophic_safety_violation"
        explanation = state.get("explanation", "Patient breached catastrophic physiological boundaries.")
        final_decision = "REJECTED"
    elif trial_status and trial_status not in EVALUABLE_BENCHMARK_STATUSES:
        terminal_reason = "trial_not_open_for_enrollment"
        explanation = f"Trial status '{trial_status}' is closed or terminated."
        final_decision = "REJECTED"
    else:
        terminal_reason = "unspecified_short_circuit"
        explanation = state.get("error_message", "Execution halted by safety guardrail.")
        final_decision = "REJECTED"

    audit_entry = {
        "step": "short_circuit_node",
        "status": "closed",
        "terminal_reason": terminal_reason,
        "final_decision": final_decision,
        "trial_status": trial_status,
        "violations_count": len(violations),
    }

    return {
        "trial_status": trial_status or "CLOSED",
        "final_decision": final_decision,
        "decision": "REJECTED",
        "eligibility": "INELIGIBLE",
        "terminal_reason": terminal_reason,
        "error_message": explanation,
        "is_short_circuited": True,
        "requires_hitl": False,
        "needs_human_review": False,
        "active_evaluation_stage": "short_circuited_terminal",
        "audit_logs": [audit_entry],
    }


def fetch_clinicaltrials_gov_status(nct_id: str) -> Dict[str, Any]:
    """Retrieves trial enrollment status from open API with resilient fallbacks for synthetic trials."""
    nct_id = str(nct_id).strip().upper()
    if not NCT_REGEX.match(nct_id) or "0000" in nct_id:
        return {"status": "ACTIVE", "payload": {}}

    url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}"
    try:
        response = requests.get(url, headers={"accept": "application/json"}, timeout=3)
        if response.status_code == 200:
            data = response.json()
            status = data.get("protocolSection", {}).get("statusModule", {}).get("overallStatus", "ACTIVE")
            return {"status": status.upper().strip(), "payload": data}
        # Fallback to ACTIVE for synthetic / mock studies or 404s
        return {"status": "ACTIVE", "payload": {}}
    except Exception:
        return {"status": "ACTIVE", "payload": {}}


def clinical_trial_status_check_node(state: TrialState) -> Dict[str, Any]:
    trial_id = state.get("trial_id", "UNKNOWN_TRIAL")
    raw_status = state.get("trial_status")
    api_payload = {}

    if not raw_status or raw_status in ("UNKNOWN", "OPEN", "ACTIVE"):
        api_result = fetch_clinicaltrials_gov_status(trial_id)
        raw_status = api_result["status"]
        api_payload = api_result["payload"]

    normalized_status = str(raw_status).upper().strip()
    is_valid_enum = normalized_status in ALL_CLINICAL_TRIALS_STATUSES or normalized_status == "ACTIVE"
    is_evaluable = normalized_status in EVALUABLE_BENCHMARK_STATUSES

    # Short-circuit only if catastrophic failure or non-evaluable closed status
    already_short_circuited = state.get("is_short_circuited", False)
    should_short_circuit = already_short_circuited or (not is_evaluable)

    audit_entry = {
        "step": "clinical_trial_status_check",
        "status": "passed" if is_evaluable else "failed",
        "trial_id": trial_id,
        "retrieved_status": normalized_status,
        "is_valid_enum": is_valid_enum,
        "is_evaluable": is_evaluable,
        "is_actively_recruiting": normalized_status in OPEN_RECRUITING_STATUSES,
    }

    return {
        "trial_status": normalized_status,
        "trial_status_evaluable": is_evaluable,
        "is_short_circuited": should_short_circuit,
        "active_evaluation_stage": "trial_status_verified",
        "audit_logs": [audit_entry],
        "raw_api_response": api_payload,
    }


def parallel_processing_fan_out(state: TrialState) -> Dict[str, Any]:
    return {
        "active_evaluation_stage": "parallel_agent_fan_out",
        "audit_logs": [{"step": "parallel_processing_fan_out", "status": "started"}],
    }


def route_after_trial_status(state: TrialState) -> str:
    """Directs to short-circuit ONLY on catastrophic failures or closed trials; otherwise fans out."""
    if state.get("is_short_circuited"):
        return "short_circuit_node"
    return "parallel_processing_fan_out"