from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class PatientData(BaseModel):
    model_config = ConfigDict(
        extra="allow"
    )

    patient_id: str

    age: int | None = None
    sex: str | None = None
    weight: float | None = None

    demographics: dict[str, Any] | None = None

    diagnoses: list[str] | None = None

    medications: list[str] | None = None

    allergies: list[str] | None = None

    lab_results: dict[str, Any] | None = None

    vital_signs: dict[str, Any] | None = None

    cardiac_function: dict[str, Any] | None = None

    medical_history: Any = None

    reproductive_status: dict[str, Any] | None = None

    current_symptoms: list[str] | None = None

    consent_capacity: bool | None = None

    pregnancy_test_result: str | None = None

    ecog_status: int | None = None

    last_systemic_therapy_date: str | None = None

    protocol_facts: dict[str, Any] = Field(
        default_factory=dict
    )


Patient = PatientData


class TrialGuardRequest(BaseModel):
    trial_id: str
    patient: PatientData
    query: str = (
        "Check whether this patient "
        "is eligible for the trial."
    )


class Violation(BaseModel):
    rule_id: str
    parameter: str
    value: Any = None
    threshold: Any = None
    unit: str | None = None
    action: str
    reason: str


class MatchedCriterion(BaseModel):
    criterion: str
    result: Literal["PASS", "FAIL"]
    value: Any = None


class Evidence(BaseModel):
    source: str
    trial_id: str
    section: str
    chunk_id: str
    text: str


class ComplianceResult(BaseModel):
    trial_id: str

    decision: Literal[
        "PASS",
        "FAIL",
        "REVIEW"
    ]

    eligibility: Literal[
        "ELIGIBLE",
        "INELIGIBLE",
        "UNCERTAIN"
    ]

    violations: list[Violation] = Field(
        default_factory=list
    )

    matched_criteria: list[MatchedCriterion] = Field(
        default_factory=list
    )

    unknown_criteria: list[str] = Field(
        default_factory=list
    )

    evidence: list[Evidence] = Field(
        default_factory=list
    )

    explanation: str

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    needs_human_review: bool