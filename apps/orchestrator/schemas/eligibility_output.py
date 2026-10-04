from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field, model_validator


class ThresholdSpec(BaseModel):
    min: Optional[float] = Field(default=None, description="Minimum acceptable numeric boundary")
    max: Optional[float] = Field(default=None, description="Maximum acceptable numeric boundary")
    unit: Optional[str] = Field(default=None, description="Standard clinical measurement unit")


class DifferenceDetail(BaseModel):
    amount: float = Field(description="Absolute deviation from the boundary")
    boundary: float = Field(description="Threshold boundary that was violated")
    direction: Literal["above", "below"] = Field(description="Direction of boundary violation")


class CriterionRecord(BaseModel):
    rule_id: str = Field(description="Unique rule identifier (e.g., NCT02415400_INC_AGE_001)")
    criterion: str = Field(description="Target parameter name (e.g., age, serum_creatinine)")
    result: Literal["PASS", "FAIL", "UNKNOWN"] = Field(
        description="Evaluation outcome for this criterion"
    )
    observed: Optional[Any] = Field(
        default=None, description="Observed patient value (canonical field matching state schema)"
    )
    value: Optional[Any] = Field(
        default=None, description="Legacy alias for observed patient value"
    )
    expected: Optional[Any] = Field(
        default=None, description="Expected value, threshold object, or operator spec"
    )
    threshold: Optional[ThresholdSpec] = Field(
        default=None, description="Structured numerical range threshold"
    )
    difference: Optional[DifferenceDetail] = Field(
        default=None, description="Calculated deviation details if boundary breached"
    )
    unit: Optional[str] = Field(
        default=None, description="Measurement unit (e.g., years, mg/dL, mL/min)"
    )
    severity: Literal["HARD", "SOFT", "MODERATE", "LOW"] = Field(
        default="HARD", description="Exclusion severity for protocol violations"
    )
    action: Optional[Literal["INCLUDE", "EXCLUDE"]] = Field(
        default=None, description="Rule intent: INCLUDE requires match, EXCLUDE forbids match"
    )
    source_chunk_id: Optional[str] = Field(
        default=None, description="RAG protocol citation chunk identifier"
    )
    reason: Optional[str] = Field(
        default=None, description="Clinical rationale and grounding for this finding"
    )

    @model_validator(mode="before")
    @classmethod
    def populate_observed_from_value(cls, data: Any) -> Any:
        """Allow legacy 'value' input while canonicalizing to 'observed'."""
        if isinstance(data, dict):
            if data.get("observed") is None and data.get("value") is not None:
                data["observed"] = data["value"]
            elif data.get("value") is None and data.get("observed") is not None:
                data["value"] = data["observed"]
        return data


class NotApplicableCriterion(BaseModel):
    rule_id: str = Field(description="Unique identifier of the rule bypassed")
    criterion: str = Field(description="Target parameter name")
    reason: str = Field(
        default="", description="Clinical rationale why this rule is non-applicable"
    )


class LLMProtocolEvaluation(BaseModel):
    verdict: Literal[
        "APPROVED", "REJECTED", "NEEDS_REVIEW",
        "ELIGIBLE", "INELIGIBLE", "INDETERMINATE"
    ] = Field(
        description="Final evaluation verdict from the clinical LLM"
    )
    eligibility: Optional[Literal["ELIGIBLE", "INELIGIBLE", "INDETERMINATE"]] = Field(
        default=None, description="Normalized patient protocol eligibility"
    )
    violations: List[CriterionRecord] = Field(
        default_factory=list, description="Criteria resulting in hard or soft protocol failures"
    )
    matched_criteria: List[CriterionRecord] = Field(
        default_factory=list, description="Criteria successfully satisfied"
    )
    unknown_criteria: List[CriterionRecord] = Field(
        default_factory=list, description="Criteria unable to be evaluated due to missing EHR data"
    )
    not_applicable_criteria: List[NotApplicableCriterion] = Field(
        default_factory=list, description="Criteria bypassed due to cohort, arm, or pathway gating"
    )
    summary: str = Field(
        description="Doctor-facing clinical rationale summarizing the adjudication"
    )
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Deterministic or model confidence score"
    )
    needs_human_review: bool = Field(
        default=False, description="Flag signaling required human-in-the-loop review"
    )

    def model_post_init(self, __context: Any) -> None:
        """Auto-computes eligibility and human review status if omitted."""
        if self.eligibility is None:
            if self.verdict in ("APPROVED", "ELIGIBLE"):
                self.eligibility = "ELIGIBLE"
            elif self.verdict in ("REJECTED", "INELIGIBLE"):
                self.eligibility = "INELIGIBLE"
            else:
                self.eligibility = "INDETERMINATE"

        # Force review if uncertain OR if violations exist
        if not self.needs_human_review:
            if (
                self.verdict in ("NEEDS_REVIEW", "INDETERMINATE")
                or len(self.unknown_criteria) > 0
                or len(self.violations) > 0
            ):
                self.needs_human_review = True