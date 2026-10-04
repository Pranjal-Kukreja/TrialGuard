from typing import Any, Literal

from pydantic import BaseModel, Field


RuleType = Literal[
    "demographic",
    "lab",
    "diagnosis",
    "medication",
    "allergy",
    "temporal",
    "medical_history",
    "clinical_condition",
    "procedure",
    "contraindication",
    "pregnancy",
    "dosage"
]


Operator = Literal[
    ">",
    ">=",
    "<",
    "<=",
    "=",
    "==",
    "!=",
    "IN",
    "NOT_IN",
    "CONTAINS",
    "ANY_OF"
]


Action = Literal[
    "REQUIRE",
    "EXCLUDE",
    "WARN",
    "HOLD",
    "ESCALATE",
    "REQUIRE_IF_ACS_PATHWAY",
    "REQUIRE_IF_PCI_PATHWAY",
    "REQUIRE_IF_WOCBP",
    "DOSE_CHECK"
]


class AtomicCondition(BaseModel):

    parameter: str

    operator: Operator

    threshold: Any

    unit: str | None = None


class DoseResult(BaseModel):

    dose: float

    unit: str

    frequency: str


class ClinicalRule(BaseModel):

    rule_id: str

    trial_id: str

    rule_type: RuleType

    parameter: str

    # Normal/simple rule
    operator: Operator | None = None

    threshold: Any = None

    unit: str | None = None

    # Compound rule, e.g. apixaban dose
    logic: Literal[
        "AT_LEAST_N"
    ] | None = None

    required_matches: int | None = None

    conditions: list[
        AtomicCondition
    ] = Field(
        default_factory=list
    )

    result_if_true: DoseResult | None = None

    result_if_false: DoseResult | None = None

    action: Action

    source_chunk_id: str

    evidence_text: str


class RuleExtractionResult(BaseModel):

    rules: list[
        ClinicalRule
    ] = Field(
        default_factory=list
    )

    unresolved_criteria: list[
        str
    ] = Field(
        default_factory=list
    )