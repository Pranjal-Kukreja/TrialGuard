from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


MISSING = object()


def get_path(data: Any, path: str) -> Any:
    """
    Strict dotted-path lookup.

    Returns MISSING if the exact source path does not exist.
    No inference or fuzzy matching is performed.
    """
    if not path:
        return MISSING

    current = data

    for part in path.split("."):
        if not isinstance(current, dict):
            return MISSING

        if part not in current:
            return MISSING

        current = current[part]

    return current


def set_path(
    data: Dict[str, Any],
    path: str,
    value: Any,
) -> None:
    """
    Set a nested dotted path, creating dictionaries as necessary.
    """
    parts = path.split(".")
    current = data

    for part in parts[:-1]:
        existing = current.get(part)

        if not isinstance(existing, dict):
            current[part] = {}

        current = current[part]

    current[parts[-1]] = deepcopy(value)


def first_existing(
    source: Dict[str, Any],
    paths: Iterable[str],
) -> Any:
    """
    Return the first explicitly existing source path.

    IMPORTANT:
    Only use aliases that are genuinely equivalent in your own
    source schema. This function itself performs no inference.
    """
    for path in paths:
        value = get_path(source, path)

        if value is not MISSING:
            return value

    return MISSING


def copy_if_present(
    source: Dict[str, Any],
    target: Dict[str, Any],
    source_paths: Iterable[str],
    target_path: str,
) -> bool:
    """
    Copy the first explicitly present source value to the canonical
    target path.

    Returns True if a value was copied.
    """
    value = first_existing(source, source_paths)

    if value is MISSING:
        return False

    set_path(target, target_path, value)
    return True


def normalize_string_list(value: Any) -> Any:
    """
    Normalize a list/string collection without inventing values.
    """
    if value is MISSING:
        return MISSING

    if value is None:
        return None

    if isinstance(value, str):
        return [value]

    if isinstance(value, (list, tuple, set)):
        return list(value)

    return value


def normalize_patient(
    source: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert an already-extracted patient dictionary into the
    canonical patient structure used by rules.json.

    This normalizer intentionally does NOT:
    - infer diagnoses from free text
    - calculate clinical facts
    - equate ACS and PCI dates
    - assume absent conditions are False
    - assume missing medications/allergies mean none
    - perform fuzzy matching

    Missing source evidence remains missing.
    """

    patient: Dict[str, Any] = {}

    # ------------------------------------------------------------
    # IDENTITY
    # ------------------------------------------------------------

    patient_id = first_existing(
        source,
        [
            "patient_id",
            "id",
        ],
    )

    if patient_id is not MISSING:
        patient["patient_id"] = patient_id

    # ------------------------------------------------------------
    # DEMOGRAPHICS
    # ------------------------------------------------------------

    copy_if_present(
        source,
        patient,
        [
            "demographics.age",
            "age",
        ],
        "demographics.age",
    )

    # ------------------------------------------------------------
    # MEDICAL HISTORY
    # ------------------------------------------------------------

    copy_if_present(
        source,
        patient,
        [
            "medical_history.non_valvular_af_or_flutter",
            "non_valvular_af_or_flutter",
        ],
        "medical_history.non_valvular_af_or_flutter",
    )

    copy_if_present(
        source,
        patient,
        [
            "medical_history.history_intracranial_hemorrhage",
            "medical_history.history_of_intracranial_hemorrhage",
            "history_intracranial_hemorrhage",
            "history_of_intracranial_hemorrhage",
        ],
        "medical_history.history_intracranial_hemorrhage",
    )

    copy_if_present(
        source,
        patient,
        [
            "medical_history.ongoing_bleeding_or_coagulopathy",
            "ongoing_bleeding_or_coagulopathy",
        ],
        "medical_history.ongoing_bleeding_or_coagulopathy",
    )

    copy_if_present(
        source,
        patient,
        [
            "medical_history.bleeding_diathesis_or_coagulopathy",
            "bleeding_diathesis_or_coagulopathy",
        ],
        "medical_history.bleeding_diathesis_or_coagulopathy",
    )

    copy_if_present(
        source,
        patient,
        [
            "medical_history.significant_renal_or_liver_disease",
            "significant_renal_or_liver_disease",
        ],
        "medical_history.significant_renal_or_liver_disease",
    )

    # Preserve explicit dialysis representation if present.
    dialysis = first_existing(
        source,
        [
            "medical_history.dialysis",
            "dialysis",
        ],
    )

    if dialysis is not MISSING:
        set_path(
            patient,
            "medical_history.dialysis",
            deepcopy(dialysis),
        )

    # ------------------------------------------------------------
    # PROTOCOL FACTS
    # ------------------------------------------------------------

    protocol_mappings = {
        "planned_or_existing_oral_anticoagulation": [
            "protocol_facts.planned_or_existing_oral_anticoagulation",
            "planned_or_existing_oral_anticoagulation",
        ],

        "days_since_acs": [
            "protocol_facts.days_since_acs",
            "days_since_acs",
        ],

        "days_since_pci": [
            "protocol_facts.days_since_pci",
            "days_since_pci",
        ],

        "planned_p2y12_inhibitor": [
            "protocol_facts.planned_p2y12_inhibitor",
            "planned_p2y12_inhibitor",
        ],

        "recent_or_planned_cabg": [
            "protocol_facts.recent_or_planned_cabg",
            "recent_or_planned_cabg",
        ],

        "contraindication_to_vka_apixaban_p2y12_or_aspirin": [
            "protocol_facts.contraindication_to_vka_apixaban_p2y12_or_aspirin",
            "contraindication_to_vka_apixaban_p2y12_or_aspirin",
        ],

        "days_since_ua_nstemi_index_event": [
            "protocol_facts.days_since_ua_nstemi_index_event",
            "days_since_ua_nstemi_index_event",
        ],

        "medical_management_strategy_decided": [
            "protocol_facts.medical_management_strategy_decided",
            "medical_management_strategy_decided",
        ],

        "age": [
            "protocol_facts.age",
        ],

        "prior_mi": [
            "protocol_facts.prior_mi",
            "prior_mi",
        ],

        "diabetes": [
            "protocol_facts.diabetes",
            "diabetes",
        ],

        "prior_revascularization": [
            "protocol_facts.prior_revascularization",
            "prior_revascularization",
        ],

        "days_since_pci_or_cabg": [
            "protocol_facts.days_since_pci_or_cabg",
            "days_since_pci_or_cabg",
        ],

        "stemi_index_event": [
            "protocol_facts.stemi_index_event",
            "stemi_index_event",
        ],

        "nyha_class_iv_within_24h": [
            "protocol_facts.nyha_class_iv_within_24h",
            "nyha_class_iv_within_24h",
        ],

        "received_des": [
            "protocol_facts.received_des",
            "received_des",
        ],

        "months_post_pci_followup": [
            "protocol_facts.months_post_pci_followup",
            "months_post_pci_followup",
        ],

        "requires_continued_anticoagulation": [
            "protocol_facts.requires_continued_anticoagulation",
            "requires_continued_anticoagulation",
        ],

        "hours_since_acs_hospitalization": [
            "protocol_facts.hours_since_acs_hospitalization",
            "hours_since_acs_hospitalization",
        ],

        "unacceptable_bleeding_risk": [
            "protocol_facts.unacceptable_bleeding_risk",
            "unacceptable_bleeding_risk",
        ],
    }

    for canonical_name, source_paths in protocol_mappings.items():
        copy_if_present(
            source,
            patient,
            source_paths,
            f"protocol_facts.{canonical_name}",
        )

    # The TRILOGY rule currently expects protocol_facts.age.
    # Copying demographics.age here is safe because this is the
    # same patient age, not a new clinical inference.
    protocol_age = get_path(
        patient,
        "protocol_facts.age",
    )

    demographics_age = get_path(
        patient,
        "demographics.age",
    )

    if (
        protocol_age is MISSING
        and demographics_age is not MISSING
    ):
        set_path(
            patient,
            "protocol_facts.age",
            demographics_age,
        )

    # ------------------------------------------------------------
    # SCORE COMPOUND FIELDS
    #
    # Your current rules.json has no parent field_path for these,
    # so the V3 engine resolves them at the root.
    # ------------------------------------------------------------

    root_mappings = {
        "mi_during_followup": [
            "mi_during_followup",
            "protocol_facts.mi_during_followup",
        ],

        "repeat_revascularization_during_followup": [
            "repeat_revascularization_during_followup",
            "protocol_facts.repeat_revascularization_during_followup",
        ],

        "aspirin_current": [
            "aspirin_current",
            "protocol_facts.aspirin_current",
        ],

        "clopidogrel_current": [
            "clopidogrel_current",
            "protocol_facts.clopidogrel_current",
        ],

        "consent_capacity": [
            "consent_capacity",
            "protocol_facts.consent_capacity",
        ],
    }

    for target_path, source_paths in root_mappings.items():
        copy_if_present(
            source,
            patient,
            source_paths,
            target_path,
        )

    # ------------------------------------------------------------
    # LAB RESULTS
    # ------------------------------------------------------------

    copy_if_present(
        source,
        patient,
        [
            "lab_results.creatinine_clearance",
            "creatinine_clearance",
        ],
        "lab_results.creatinine_clearance",
    )

    copy_if_present(
        source,
        patient,
        [
            "lab_results.platelets",
            "platelets",
        ],
        "lab_results.platelets",
    )

    # ------------------------------------------------------------
    # REPRODUCTIVE STATUS
    # ------------------------------------------------------------

    copy_if_present(
        source,
        patient,
        [
            "reproductive_status.pregnant",
            "protocol_facts.pregnant",
            "pregnant",
        ],
        "reproductive_status.pregnant",
    )

    # ------------------------------------------------------------
    # MEDICATIONS
    # ------------------------------------------------------------

    medications = first_existing(
        source,
        [
            "medications",
        ],
    )

    medications = normalize_string_list(
        medications
    )

    if medications is not MISSING:
        patient["medications"] = medications

    # ------------------------------------------------------------
    # ALLERGIES
    # ------------------------------------------------------------

    allergies = first_existing(
        source,
        [
            "allergies",
        ],
    )

    allergies = normalize_string_list(
        allergies
    )

    if allergies is not MISSING:
        patient["allergies"] = allergies

    return patient


def load_json(path: Path) -> Dict[str, Any]:
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def save_json(
    data: Dict[str, Any],
    path: Path,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]

    input_path = (
        project_root
        / "data"
        / "processed"
        / "test_patient_complete.json"
    )

    output_path = (
        project_root
        / "data"
        / "processed"
        / "test_patient_normalized.json"
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input patient not found: {input_path}"
        )

    source = load_json(input_path)

    normalized = normalize_patient(
        source
    )

    save_json(
        normalized,
        output_path,
    )

    print("=" * 70)
    print("TrialGuard Patient Normalizer")
    print("=" * 70)
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print()
    print(json.dumps(
        normalized,
        indent=2,
        ensure_ascii=False,
    ))
    print("=" * 70)


if __name__ == "__main__":
    main()