"""
Guardrail rule definitions for Guardrail 2 (protocol_verification_node).

Relaxed Baseline Rules:
  - High safety ceilings designed ONLY to catch immediate catastrophic failures.
  - Allows borderline or complex patients to pass through to downstream agents.
  - Aligned with standard clinical reference units, patients_expanded.json fixtures,
    and RAG rule evaluation outputs (RagAnalysisOutput / RuleAnalysisPackage).
"""

from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Relaxed Baseline Catastrophic Safety Boundaries
# ---------------------------------------------------------------------------
# Note: For numeric ranges, [min, max] defines the SAFE physiological corridor.
# Any observed value outside this corridor triggers an immediate HARD violation.
# ---------------------------------------------------------------------------
BASELINE_SAFETY_RULES: List[Dict[str, Any]] = [
    # Hepatic Function
    {
        "rule_id": "SAFETY_HEPATIC_ALT",
        "criterion": "ALT",
        "parameter": "ALT",
        "field_path": "lab_results.ALT",
        "rule_type": "numeric_range",
        "severity": "HARD",
        "action": "EXCLUDE",
        "max": 200.0,
        "unit": "U/L",
        "source_chunk_id": "SAFETY-BASELINE-HEPATIC",
        "reason": "Hepatic enzyme ALT exceeds 5x upper limit of normal safety boundary (200 U/L).",
    },
    {
        "rule_id": "SAFETY_HEPATIC_AST",
        "criterion": "AST",
        "parameter": "AST",
        "field_path": "lab_results.AST",
        "rule_type": "numeric_range",
        "severity": "HARD",
        "action": "EXCLUDE",
        "max": 200.0,
        "unit": "U/L",
        "source_chunk_id": "SAFETY-BASELINE-HEPATIC",
        "reason": "Hepatic enzyme AST exceeds 5x upper limit of normal safety boundary (200 U/L).",
    },
    {
        "rule_id": "SAFETY_HEPATIC_BILIRUBIN",
        "criterion": "total_bilirubin",
        "parameter": "total_bilirubin",
        "field_path": "lab_results.total_bilirubin",
        "rule_type": "numeric_range",
        "severity": "HARD",
        "action": "EXCLUDE",
        "max": 4.0,
        "unit": "mg/dL",
        "source_chunk_id": "SAFETY-BASELINE-HEPATIC",
        "reason": "Total bilirubin exceeds severe hyperbilirubinemia threshold (4.0 mg/dL).",
    },

    # Renal Function
    {
        "rule_id": "SAFETY_RENAL_EGFR",
        "criterion": "eGFR",
        "parameter": "eGFR",
        "field_path": "lab_results.eGFR",
        "rule_type": "numeric_range",
        "severity": "HARD",
        "action": "EXCLUDE",
        "min": 15.0,  # Below 15 indicates dialysis/end-stage renal disease
        "unit": "mL/min/1.73m2",
        "source_chunk_id": "SAFETY-BASELINE-RENAL",
        "reason": "eGFR below 15 mL/min/1.73m2 indicates severe end-stage renal insufficiency.",
    },
    {
        "rule_id": "SAFETY_RENAL_CREATININE",
        "criterion": "serum_creatinine",
        "parameter": "serum_creatinine",
        "field_path": "lab_results.serum_creatinine",
        "rule_type": "numeric_range",
        "severity": "HARD",
        "action": "EXCLUDE",
        "max": 4.5,
        "unit": "mg/dL",
        "source_chunk_id": "SAFETY-BASELINE-RENAL",
        "reason": "Serum creatinine exceeds critical physiological ceiling of 4.5 mg/dL.",
    },

    # Hematologic Function
    {
        "rule_id": "SAFETY_HEME_ANC",
        "criterion": "ANC",
        "parameter": "ANC",
        "field_path": "lab_results.ANC",
        "rule_type": "numeric_range",
        "severity": "HARD",
        "action": "EXCLUDE",
        "min": 500.0,
        "unit": "/uL",
        "source_chunk_id": "SAFETY-BASELINE-HEME",
        "reason": "Absolute neutrophil count below 500/uL indicates agranulocytosis risk.",
    },
    {
        "rule_id": "SAFETY_HEME_PLATELETS",
        "criterion": "platelets",
        "parameter": "platelets",
        "field_path": "lab_results.platelets",
        "rule_type": "numeric_range",
        "severity": "HARD",
        "action": "EXCLUDE",
        "min": 25000.0,
        "unit": "/uL",
        "source_chunk_id": "SAFETY-BASELINE-HEME",
        "reason": "Platelet count below 25,000/uL indicates imminent spontaneous hemorrhage hazard.",
    },
    {
        "rule_id": "SAFETY_HEME_HEMOGLOBIN",
        "criterion": "hemoglobin",
        "parameter": "hemoglobin",
        "field_path": "lab_results.hemoglobin",
        "rule_type": "numeric_range",
        "severity": "HARD",
        "action": "EXCLUDE",
        "min": 7.0,
        "unit": "g/dL",
        "source_chunk_id": "SAFETY-BASELINE-HEME",
        "reason": "Hemoglobin below 7.0 g/dL violates life-threatening transfusion floor.",
    },

    # Coagulation Function
    {
        "rule_id": "SAFETY_COAG_INR",
        "criterion": "INR",
        "parameter": "INR",
        "field_path": "lab_results.INR",
        "rule_type": "numeric_range",
        "severity": "HARD",
        "action": "EXCLUDE",
        "max": 3.5,
        "unit": "ratio",
        "source_chunk_id": "SAFETY-BASELINE-COAG",
        "reason": "INR exceeds safe threshold (> 3.5) for clinical trial intervention.",
    },

    # Cardiac Function
    {
        "rule_id": "SAFETY_CARDIAC_QTC",
        "criterion": "QTc",
        "parameter": "QTc",
        "field_path": "cardiac_function.QTc",
        "rule_type": "numeric_range",
        "severity": "HARD",
        "action": "EXCLUDE",
        "max": 520.0,
        "unit": "ms",
        "source_chunk_id": "SAFETY-BASELINE-CARDIAC",
        "reason": "Corrected QT interval > 520 ms indicates prohibitive ventricular arrhythmia risk.",
    },
    {
        "rule_id": "SAFETY_CARDIAC_LVEF",
        "criterion": "LVEF",
        "parameter": "LVEF",
        "field_path": "cardiac_function.LVEF",
        "rule_type": "numeric_range",
        "severity": "HARD",
        "action": "EXCLUDE",
        "min": 30.0,
        "unit": "%",
        "source_chunk_id": "SAFETY-BASELINE-CARDIAC",
        "reason": "LVEF below 30% reflects decompensated systolic heart failure.",
    },

    # Demographics & Regulatory Safety
    {
        "rule_id": "SAFETY_ADULT_AGE",
        "criterion": "age",
        "parameter": "age",
        "field_path": "age",
        "rule_type": "numeric_range",
        "severity": "HARD",
        "action": "EXCLUDE",
        "min": 18,
        "max": 100,
        "unit": "years",
        "source_chunk_id": "SAFETY-BASELINE-DEMO",
        "reason": "Patient is outside adult safety boundaries (18-100 years).",
    },
    {
        "rule_id": "SAFETY_PREGNANCY_TEST",
        "criterion": "pregnancy_test_result",
        "parameter": "pregnancy_test_result",
        "field_path": "pregnancy_test_result",
        "rule_type": "exact_match",
        "severity": "HARD",
        "action": "EXCLUDE",
        "expected": "negative",
        "applies_if": {
            "sex": "female",
            "protocol_facts.woman_of_childbearing_potential": True,
        },
        "source_chunk_id": "SAFETY-BASELINE-REPRO",
        "reason": "Positive or non-negative pregnancy test in woman of childbearing potential.",
    },
    {
        "rule_id": "SAFETY_CONSENT_CAPACITY",
        "criterion": "consent_capacity",
        "parameter": "consent_capacity",
        "field_path": "consent_capacity",
        "rule_type": "exact_match",
        "severity": "HARD",
        "action": "EXCLUDE",
        "expected": True,
        "source_chunk_id": "SAFETY-BASELINE-CONSENT",
        "reason": "Lack of legal informed consent capacity without authorized representative.",
    },
]


# ---------------------------------------------------------------------------
# Trial-Specific Rules Layered Over Baseline Rules
# ---------------------------------------------------------------------------
TRIAL_SPECIFIC_RULES: Dict[str, List[Dict[str, Any]]] = {
    # AUGUSTUS Trial (Antithrombotic Therapy in AF with ACS/PCI)
    "NCT02415400": [
        {
            "rule_id": "NCT02415400_INC_AGE",
            "criterion": "age",
            "parameter": "age",
            "field_path": "age",
            "rule_type": "numeric_range",
            "min": 18,
            "unit": "years",
            "severity": "HARD",
            "action": "INCLUDE",
            "source_chunk_id": "NCT02415400-eligibility-001",
            "reason": "Patient must be at least 18 years of age.",
        },
        {
            "rule_id": "NCT02415400_INC_PCI_TIMING",
            "criterion": "days_since_PCI",
            "parameter": "days_since_PCI",
            "field_path": "protocol_facts.days_since_PCI",
            "rule_type": "numeric_range",
            "max": 14,
            "unit": "days",
            "severity": "HARD",
            "action": "INCLUDE",
            "source_chunk_id": "NCT02415400-eligibility-001",
            "reason": "PCI with stent must have occurred within prior 14 days.",
        },
        {
            "rule_id": "NCT02415400_INC_ACS_TIMING",
            "criterion": "days_since_acute_coronary_syndrome",
            "parameter": "days_since_acute_coronary_syndrome",
            "field_path": "protocol_facts.days_since_acute_coronary_syndrome",
            "rule_type": "numeric_range",
            "max": 14,
            "unit": "days",
            "severity": "HARD",
            "action": "INCLUDE",
            "source_chunk_id": "NCT02415400-eligibility-001",
            "reason": "Presentation with ACS must have occurred within prior 14 days.",
        },
        {
            "rule_id": "NCT02415400_EXC_CREATININE",
            "criterion": "serum_creatinine",
            "parameter": "serum_creatinine",
            "field_path": "lab_results.serum_creatinine",
            "rule_type": "numeric_range",
            "max": 2.5,  # Values > 2.5 violate the protocol ceiling
            "unit": "mg/dL",
            "severity": "HARD",
            "action": "EXCLUDE",
            "source_chunk_id": "NCT02415400-eligibility-006",
            "reason": "Serum creatinine > 2.5 mg/dL indicates severe renal impairment.",
        },
        {
            "rule_id": "NCT02415400_EXC_SEVERE_RENAL",
            "criterion": "creatinine_clearance",
            "parameter": "creatinine_clearance",
            "field_path": "lab_results.creatinine_clearance",
            "rule_type": "numeric_range",
            "min": 30.0,  # Values < 30 violate the protocol floor
            "unit": "mL/min",
            "severity": "HARD",
            "action": "EXCLUDE",
            "source_chunk_id": "NCT02415400-eligibility-006",
            "reason": "Severe renal insufficiency (CrCl < 30 mL/min) is an exclusion criterion.",
        },
        {
            "rule_id": "NCT02415400_INC_ORAL_ANTICOAG",
            "criterion": "oral_anticoagulation_required",
            "parameter": "oral_anticoagulation_required",
            "field_path": "protocol_facts.oral_anticoagulation_required",
            "rule_type": "exact_match",
            "expected": True,
            "severity": "HARD",
            "action": "INCLUDE",
            "source_chunk_id": "NCT02415400-eligibility-001",
            "reason": "Requires physician-determined need for long-term oral anticoagulation therapy.",
        },
        {
            "rule_id": "NCT02415400_EXC_INTRACRANIAL_HEMORRHAGE",
            "criterion": "history_of_intracranial_hemorrhage",
            "parameter": "history_of_intracranial_hemorrhage",
            "field_path": "protocol_facts.history_of_intracranial_hemorrhage",
            "rule_type": "exact_match",
            "expected": False,
            "severity": "HARD",
            "action": "EXCLUDE",
            "source_chunk_id": "NCT02415400-eligibility-003",
            "reason": "Prior history of intracranial hemorrhage excludes oral anticoagulation protocol.",
        },
        {
            "rule_id": "NCT02415400_EXC_ONGOING_BLEEDING",
            "criterion": "ongoing_bleeding",
            "parameter": "ongoing_bleeding",
            "field_path": "protocol_facts.ongoing_bleeding",
            "rule_type": "exact_match",
            "expected": False,
            "severity": "HARD",
            "action": "EXCLUDE",
            "source_chunk_id": "NCT02415400-eligibility-004",
            "reason": "Active clinically significant bleeding is an absolute contraindication.",
        },
        {
            "rule_id": "NCT02415400_EXC_COAGULOPATHY",
            "criterion": "known_coagulopathy",
            "parameter": "known_coagulopathy",
            "field_path": "protocol_facts.known_coagulopathy",
            "rule_type": "exact_match",
            "expected": False,
            "severity": "HARD",
            "action": "EXCLUDE",
            "source_chunk_id": "NCT02415400-eligibility-005",
            "reason": "Known pre-existing coagulopathy presents prohibitive hemorrhagic risk.",
        },
        {
            "rule_id": "NCT02415400_EXC_CABG_INDEX",
            "criterion": "cabg_for_index_acs",
            "parameter": "cabg_for_index_acs",
            "field_path": "protocol_facts.cabg_for_index_acs",
            "rule_type": "exact_match",
            "expected": False,
            "severity": "SOFT",
            "action": "EXCLUDE",
            "source_chunk_id": "NCT02415400-eligibility-007",
            "reason": "Coronary artery bypass graft (CABG) surgery planned for index event.",
        },
        {
            "rule_id": "NCT02415400_EXC_OTHER_ANTICOAGULATION",
            "criterion": "other_condition_requiring_chronic_anticoagulation",
            "parameter": "other_condition_requiring_chronic_anticoagulation",
            "field_path": "protocol_facts.other_condition_requiring_chronic_anticoagulation",
            "rule_type": "exact_match",
            "expected": False,
            "severity": "HARD",
            "action": "EXCLUDE",
            "source_chunk_id": "NCT02415400-eligibility-008",
            "reason": "Concomitant indication mandating persistent non-study chronic anticoagulation.",
        },
        {
            "rule_id": "NCT02415400_EXC_DRUG_CONTRAINDICATION",
            "criterion": "drug_contraindication",
            "parameter": "drug_contraindication",
            "field_path": "protocol_facts.drug_contraindication",
            "rule_type": "empty_list",
            "severity": "HARD",
            "action": "EXCLUDE",
            "source_chunk_id": "NCT02415400-eligibility-009",
            "reason": "Documented hypersensitivity or contraindication to protocol study drugs.",
        },
        {
            "rule_id": "NCT02415400_INC_P2Y12_DURATION",
            "criterion": "planned_p2y12_duration",
            "parameter": "planned_p2y12_duration",
            "field_path": "protocol_facts.planned_p2y12_duration",
            "rule_type": "numeric_range",
            "min": 6,
            "unit": "months",
            "severity": "SOFT",
            "action": "INCLUDE",
            "source_chunk_id": "NCT02415400-eligibility-002",
            "reason": "Planned duration of P2Y12 inhibitor therapy must be at least 6 months.",
        },
    ],

    # FDA Phase II Renal Safety Protocol
    "FDA-CTP-2024-1187": [
        {
            "rule_id": "RENAL_SAFE_EGFR",
            "criterion": "eGFR",
            "parameter": "eGFR",
            "field_path": "lab_results.eGFR",
            "rule_type": "numeric_range",
            "severity": "HARD",
            "action": "EXCLUDE",
            "min": 30.0,
            "unit": "mL/min/1.73m2",
            "source_chunk_id": "FDA-CTP-2024-1187-sec4",
            "reason": "eGFR below 30 mL/min/1.73m2 violates Phase II renal safety floor.",
        },
        {
            "rule_id": "RENAL_SAFE_CREATININE",
            "criterion": "serum_creatinine",
            "parameter": "serum_creatinine",
            "field_path": "lab_results.serum_creatinine",
            "rule_type": "numeric_range",
            "severity": "HARD",
            "action": "EXCLUDE",
            "max": 2.0,
            "unit": "mg/dL",
            "source_chunk_id": "FDA-CTP-2024-1187-sec4",
            "reason": "Serum creatinine above 2.0 mg/dL violates Phase II safety protocol.",
        },
    ],

    # Hepatic Decompensation Trial
    "NCT05930860": [
        {
            "rule_id": "NCT05930860_EXCL_HEPATIC_DECOMP",
            "criterion": "diagnoses",
            "parameter": "diagnoses",
            "field_path": "diagnoses",
            "rule_type": "exclusion_list",
            "severity": "HARD",
            "action": "EXCLUDE",
            "disallowed_values": ["decompensated cirrhosis"],
            "source_chunk_id": "NCT05930860-excl-01",
            "reason": "Decompensated liver cirrhosis is an exclusion criterion.",
        },
    ],

    # Default baseline
    "NCT00000000": [
        {
            "rule_id": "ONC_ECOG_STATUS",
            "criterion": "ecog_status",
            "parameter": "ecog_status",
            "field_path": "ecog_status",
            "rule_type": "numeric_range",
            "severity": "SOFT",
            "action": "INCLUDE",
            "max": 2,
            "unit": "ECOG",
            "source_chunk_id": "NCT00000000-ecog",
            "reason": "ECOG performance status must be 0, 1, or 2.",
        },
    ],
}


def get_protocol_rules(trial_id: Optional[str]) -> List[Dict[str, Any]]:
    """
    Returns baseline catastrophic safety boundaries combined with
    trial-specific protocol criteria matched by normalized exact prefix/key.
    """
    if not trial_id or not trial_id.strip():
        return list(BASELINE_SAFETY_RULES)

    clean_id = trial_id.strip().upper()
    matched_rules: List[Dict[str, Any]] = []

    # Priority 1: Exact key match
    if clean_id in TRIAL_SPECIFIC_RULES:
        matched_rules = TRIAL_SPECIFIC_RULES[clean_id]
    else:
        # Priority 2: Substring key match (only if clean_id is non-trivial)
        for key, specific_rules in TRIAL_SPECIFIC_RULES.items():
            if len(clean_id) >= 6 and (key in clean_id or clean_id in key):
                matched_rules = specific_rules
                break

    return list(BASELINE_SAFETY_RULES) + list(matched_rules)