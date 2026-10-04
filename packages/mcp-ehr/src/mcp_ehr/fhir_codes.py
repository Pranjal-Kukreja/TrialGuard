"""
Shared config between seed_data.py (writer) and fhir_client.py (reader).

We tag every Observation we create with our own custom coding system
instead of guessing real LOINC codes from memory -- this guarantees the
writer and reader agree on field names exactly, with zero risk of a
misremembered LOINC code breaking the round-trip.

Updated to synchronize with the new trial_id, cohort, dob, medical_history,
and extended protocol ground-truth parameters across TrialGuard pipelines.
"""

from typing import Dict, Optional, Tuple

CODE_SYSTEM = "https://techquest-hackathon.local/lab-codes"

# ---------------------------------------------------------------------------
# field_name -> (bucket, value_type, default_unit)
# bucket: Which PatientData sub-dictionary this belongs to (or None for root).
# value_type: Directs serializer/parser to valueQuantity, valueInteger,
#             valueBoolean, valueString, or valueDateTime.
# default_unit: Clinical unit symbol for UCUM / Observation.valueQuantity.unit
# ---------------------------------------------------------------------------
FIELD_ROUTES: Dict[str, Tuple[Optional[str], str, Optional[str]]] = {
    # -----------------------------------------------------------------------
    # lab_results
    # -----------------------------------------------------------------------
    "ALT": ("lab_results", "quantity", "U/L"),
    "AST": ("lab_results", "quantity", "U/L"),
    "eGFR": ("lab_results", "quantity", "mL/min/1.73m2"),
    "ANC": ("lab_results", "quantity", "/uL"),
    "platelets": ("lab_results", "quantity", "/uL"),
    "hemoglobin": ("lab_results", "quantity", "g/dL"),
    "INR": ("lab_results", "quantity", "ratio"),
    "total_bilirubin": ("lab_results", "quantity", "mg/dL"),
    "serum_creatinine": ("lab_results", "quantity", "mg/dL"),
    "creatinine_clearance": ("lab_results", "quantity", "mL/min"),

    # -----------------------------------------------------------------------
    # vital_signs
    # -----------------------------------------------------------------------
    "heart_rate": ("vital_signs", "quantity", "beats/min"),
    "blood_pressure_systolic": ("vital_signs", "integer", "mmHg"),
    "blood_pressure_diastolic": ("vital_signs", "integer", "mmHg"),

    # -----------------------------------------------------------------------
    # cardiac_function
    # -----------------------------------------------------------------------
    "LVEF": ("cardiac_function", "quantity", "%"),
    "QTc": ("cardiac_function", "quantity", "ms"),

    # -----------------------------------------------------------------------
    # Top-level PatientData & Cohort Demographics
    # -----------------------------------------------------------------------
    "weight": (None, "quantity", "kg"),
    "dob": (None, "string", None),
    "birth_date": (None, "string", None),
    "cohort": (None, "string", None),
    "trial_id": (None, "string", None),
    "assigned_demo_trial_id": (None, "string", None),
    "ecog_status": (None, "integer", "score"),
    "consent_capacity": (None, "boolean", None),
    "pregnancy_test_result": (None, "string", None),
    "last_systemic_therapy_date": (None, "dateTime", None),
    "medical_history_narrative": (None, "string", None),
    "medical_history": (None, "string", None),

    # -----------------------------------------------------------------------
    # protocol_facts (TrialGuard Ground Truths from patients_expanded.json)
    # -----------------------------------------------------------------------
    "oral_anticoagulation_required": ("protocol_facts", "boolean", None),
    "planned_or_existing_oral_anticoagulation": ("protocol_facts", "boolean", None),
    "acs_pathway": ("protocol_facts", "boolean", None),
    "days_since_acute_coronary_syndrome": ("protocol_facts", "integer", "days"),
    "pci_pathway": ("protocol_facts", "boolean", None),
    "days_since_PCI": ("protocol_facts", "integer", "days"),
    "planned_p2y12_duration": ("protocol_facts", "integer", "months"),
    "history_of_intracranial_hemorrhage": ("protocol_facts", "boolean", None),
    "prior_bleeding": ("protocol_facts", "boolean", None),
    "ongoing_bleeding": ("protocol_facts", "boolean", None),
    "known_coagulopathy": ("protocol_facts", "boolean", None),
    "cabg_for_index_acs": ("protocol_facts", "boolean", None),
    "other_condition_requiring_chronic_anticoagulation": ("protocol_facts", "boolean", None),
    "drug_contraindication": ("protocol_facts", "string", None),
    "pregnant": ("protocol_facts", "boolean", None),
    "breastfeeding": ("protocol_facts", "boolean", None),
    "woman_of_childbearing_potential": ("protocol_facts", "boolean", None),
    "pregnancy_test_negative": ("protocol_facts", "boolean", None),
}

# Tag added to every resource we create so synthetic data can be isolated
HACKATHON_TAG_SYSTEM = "https://techquest-hackathon.local/tags"
HACKATHON_TAG_CODE = "trialguard-ai-seed"


def get_field_route(field_name: str) -> Optional[Tuple[Optional[str], str, Optional[str]]]:
    """Helper to safely fetch (bucket, value_type, default_unit) tuple."""
    return FIELD_ROUTES.get(field_name)


def get_bucket_for_field(field_name: str) -> Optional[str]:
    """Returns the PatientData target dictionary (or None for top-level)."""
    route = FIELD_ROUTES.get(field_name)
    return route[0] if route else None


def get_value_type_for_field(field_name: str) -> str:
    """Returns the expected FHIR value type (quantity, integer, boolean, string, dateTime)."""
    route = FIELD_ROUTES.get(field_name)
    return route[1] if route else "string"


def get_default_unit_for_field(field_name: str) -> Optional[str]:
    """Returns the standard clinical unit for the given observation."""
    route = FIELD_ROUTES.get(field_name)
    return route[2] if route else None