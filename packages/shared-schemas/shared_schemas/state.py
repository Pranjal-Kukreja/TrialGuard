import operator
from typing import Annotated, Any, Dict, List, Optional, Union
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


# ---------------------------------------------------------------------------
# Reducer Utilities
# ---------------------------------------------------------------------------
def append_history_reducer(
    existing: Optional[List[Any]],
    incoming: Optional[List[Any]],
) -> List[Any]:
    """Generic history reducer that preserves chronology across modify cycles."""
    if existing is None:
        existing = []
    if incoming is None:
        incoming = []
    return existing + incoming


def replace_violations_reducer(
    existing: Optional[List[Dict[str, Any]]],
    incoming: Optional[List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """
    Authoritative violations reducer.
    Allows multi_agent_evaluation or HITL nodes to flush ([]), replace,
    or update active violations rather than permanently accumulating them.
    """
    if incoming is None:
        return existing or []
    return incoming


def pick_latest_str(existing: Optional[str], incoming: Optional[str]) -> Optional[str]:
    """Safety reducer preventing InvalidUpdateError on concurrent stage writes."""
    return incoming if incoming is not None else existing


# ---------------------------------------------------------------------------
# Patient Vital Signs & Measurements
# ---------------------------------------------------------------------------
class VitalSigns(TypedDict, total=False):
    heart_rate: Optional[float]
    blood_pressure_systolic: Optional[int]
    blood_pressure_diastolic: Optional[int]


# ---------------------------------------------------------------------------
# Patient Laboratory Results (conforms to patients_expanded.json)
# ---------------------------------------------------------------------------
class LabResults(TypedDict, total=False):
    ALT: Optional[float]
    AST: Optional[float]
    eGFR: Optional[float]
    ANC: Optional[float]
    platelets: Optional[float]
    hemoglobin: Optional[float]
    INR: Optional[float]
    total_bilirubin: Optional[float]
    serum_creatinine: Optional[float]
    creatinine_clearance: Optional[float]


# ---------------------------------------------------------------------------
# Cardiac Parameters
# ---------------------------------------------------------------------------
class CardiacFunction(TypedDict, total=False):
    LVEF: Optional[float]
    QTc: Optional[float]


# ---------------------------------------------------------------------------
# Protocol Facts (conforms directly to TrialGuard schema in patients_expanded)
# ---------------------------------------------------------------------------
class ProtocolFacts(TypedDict, total=False):
    oral_anticoagulation_required: Optional[bool]
    planned_or_existing_oral_anticoagulation: Optional[bool]
    acs_pathway: Optional[bool]
    days_since_acute_coronary_syndrome: Optional[int]
    pci_pathway: Optional[bool]
    days_since_PCI: Optional[int]
    planned_p2y12_duration: Optional[int]
    history_of_intracranial_hemorrhage: Optional[bool]
    ongoing_bleeding: Optional[bool]
    known_coagulopathy: Optional[bool]
    cabg_for_index_acs: Optional[bool]
    other_condition_requiring_chronic_anticoagulation: Optional[bool]
    drug_contraindication: Optional[List[str]]
    pregnant: Optional[bool]
    breastfeeding: Optional[bool]
    woman_of_childbearing_potential: Optional[bool]
    pregnancy_test_negative: Optional[bool]


# ---------------------------------------------------------------------------
# Complete Patient Data Model
# ---------------------------------------------------------------------------
class PatientData(TypedDict, total=False):
    patient_id: str
    internal_id: Optional[str]
    fhir_id: Optional[str]
    name: Optional[str]
    dob: Optional[str]
    cohort: Optional[str]
    age: int
    sex: str
    weight: Optional[float]
    diagnoses: Optional[List[str]]
    medications: Optional[List[str]]
    allergies: Optional[List[str]]

    lab_results: Optional[LabResults]
    vital_signs: Optional[VitalSigns]
    cardiac_function: Optional[CardiacFunction]

    medical_history: Optional[Union[List[str], Dict[str, Any]]]
    medical_history_narrative: Optional[str]

    current_symptoms: Optional[List[str]]
    pregnancy_test_result: Optional[str]
    consent_capacity: Optional[bool]
    ecog_status: Optional[int]
    last_systemic_therapy_date: Optional[str]

    protocol_facts: Optional[Union[ProtocolFacts, Dict[str, Any]]]


# ---------------------------------------------------------------------------
# Structured RAG Analysis Sub-models
# ---------------------------------------------------------------------------
class ThresholdSpec(TypedDict, total=False):
    min: Optional[float]
    max: Optional[float]
    unit: Optional[str]


class DifferenceDetail(TypedDict, total=False):
    amount: float
    boundary: float
    direction: str


class ProtocolViolation(TypedDict, total=False):
    rule_id: str
    parameter: str
    field_path: Optional[str]
    value: Optional[Any]
    threshold: Optional[ThresholdSpec]
    observed: Optional[Any]
    expected: Optional[Union[ThresholdSpec, bool, str, float]]
    difference: Optional[DifferenceDetail]
    unit: Optional[str]
    severity: str
    action: str
    source_chunk_id: str
    reason: str


class MatchedCriterion(TypedDict, total=False):
    rule_id: str
    criterion: str
    result: str
    value: Any
    threshold: Optional[ThresholdSpec]


class UnknownCriterion(TypedDict, total=False):
    rule_id: str
    criterion: str
    field_path: Optional[str]
    observed: Optional[Any]
    expected: Optional[Any]
    source_chunk_id: str
    reason: str


class EvidenceItem(TypedDict, total=False):
    source: str
    trial_id: Optional[str]
    drug: Optional[str]
    section: Optional[str]
    chunk_id: str
    text: str
    score: float


class ProtocolFinding(TypedDict, total=False):
    rule_id: str
    parameter: str
    status: str
    observed: Optional[Any]
    expected: Optional[Union[ThresholdSpec, bool, str, float]]
    difference: Optional[DifferenceDetail]
    severity: Optional[str]
    action: Optional[str]
    source_chunk_id: str
    reason: Optional[str]


class ActionItem(TypedDict, total=False):
    type: str
    status: str
    count: int


class RuleAnalysisPackage(TypedDict, total=False):
    purpose: str
    trial_id: str
    prescribed_action: str
    doctor_query: str
    patient: Dict[str, Any]
    protocol_findings: List[ProtocolFinding]
    action_items: List[ActionItem]
    instructions_for_downstream_agent: List[str]


class GenerationMetadata(TypedDict, total=False):
    llm_used: bool
    llm_model: Optional[str]
    fallback_used: bool


class RagAnalysisOutput(TypedDict, total=False):
    trial_id: str
    decision: str
    eligibility: str
    prescribed_action: str
    violations: List[ProtocolViolation]
    matched_criteria: List[MatchedCriterion]
    unknown_criteria: List[UnknownCriterion]
    evidence: List[EvidenceItem]
    safety_evidence: List[EvidenceItem]
    rag_query: str
    rule_analysis_package: RuleAnalysisPackage
    explanation: str
    confidence: float
    needs_human_review: bool
    generation_metadata: GenerationMetadata


# ---------------------------------------------------------------------------
# Specialized A2A Agent Sub-Models
# ---------------------------------------------------------------------------
class ExpectedValueSpec(TypedDict, total=False):
    operator: str
    value: Union[str, float, int]
    unit: Optional[str]


class ComplianceViolation(TypedDict, total=False):
    parameter: str
    observed: Any
    expected: ExpectedValueSpec
    protocol_text: str
    reason: str


class ComplianceVerdictRecord(TypedDict, total=False):
    iteration: int
    compliance_status: str  # COMPLIANT | NON_COMPLIANT | UNKNOWN
    valid: bool
    confidence: float
    violations: List[ComplianceViolation]
    explanation: str
    sources: List[Dict[str, Any]]
    prescribed_action: Optional[Dict[str, Any]]
    needs_human_review: bool


class SafetyViolation(TypedDict, total=False):
    rule_id: str
    parameter: str
    observed: Any
    expected: Any
    severity: str  # HARD | MODERATE | LOW
    reason: str


class SafetyVerdictRecord(TypedDict, total=False):
    iteration: int
    safety_status: str  # CLEARED | FLAGGED | CRITICAL | UNKNOWN
    risk_score: float
    contraindications_found: int
    violations: List[SafetyViolation]
    summary: str
    needs_human_review: bool


class FinancialException(TypedDict, total=False):
    billing_code: str
    procedure: str
    coverage_status: str
    reason: str


class FinancialVerdictRecord(TypedDict, total=False):
    iteration: int
    coverage_status: str  # COVERED | NOT_COVERED | REQUIRES_PRE_AUTH
    pre_auth_required: bool
    sponsor_billing_eligible: bool
    tier: str
    exceptions: List[FinancialException]
    explanation: str


class MultiAgentIterationSnapshot(TypedDict, total=False):
    iteration: int
    compliance: ComplianceVerdictRecord
    safety: SafetyVerdictRecord
    financial: FinancialVerdictRecord
    overall_action_permitted: bool


# ---------------------------------------------------------------------------
# Core LangGraph TrialState for Adjudication Pipeline
# ---------------------------------------------------------------------------
class TrialState(TypedDict, total=False):
    trial_id: str
    patient_id: Optional[str]
    cohort: Optional[str]
    prescribed_action: Optional[Union[str, Dict[str, Any]]]
    proposed_action: Optional[Union[str, Dict[str, Any]]]
    doctor_query: Optional[str]

    # Input & Stage-Entry Payloads
    patient: PatientData
    raw_fhir_patient: Optional[Dict[str, Any]]
    financial_context: Optional[Dict[str, Any]]
    relevant_policies: Optional[List[Dict[str, Any]]]

    # Structured RAG payload (primary input for downstream G1/G2/evaluators)
    rag_analysis: Optional[RagAnalysisOutput]
    rag_query: Optional[str]

    query: Optional[str]
    protocol_rules: List[Dict[str, Any]]

    # Guardrail Check Outputs
    guardrail_1_passed: Optional[bool]
    guardrail_2_passed: Optional[bool]

    # Reducer Lists
    messages: Annotated[List[AnyMessage], add_messages]
    audit_logs: Annotated[List[Dict[str, Any]], operator.add]
    violations: Annotated[List[Dict[str, Any]], replace_violations_reducer]  # Replaces operator.add
    matched_criteria: Annotated[List[Dict[str, Any]], operator.add]
    unknown_criteria: Annotated[List[Dict[str, Any]], operator.add]
    not_applicable_criteria: Annotated[List[Dict[str, Any]], operator.add]
    dosage_checks: Annotated[List[Dict[str, Any]], operator.add]
    safety_evidence: Annotated[List[Dict[str, Any]], operator.add]
    criteria_evaluations: Annotated[List[Dict[str, Any]], operator.add]
    evidence: Annotated[List[Dict[str, Any]], operator.add]

    # -------------------------------------------------------------
    # Specialized A2A Agent Verdict History Reducers
    # -------------------------------------------------------------
    compliance_verdict_history: Annotated[List[ComplianceVerdictRecord], append_history_reducer]
    safety_verdict_history: Annotated[List[SafetyVerdictRecord], append_history_reducer]
    financial_verdict_history: Annotated[List[FinancialVerdictRecord], append_history_reducer]
    multi_agent_iteration_history: Annotated[List[MultiAgentIterationSnapshot], append_history_reducer]

    # Evaluation and Adjudication Verdict Parameters
    evaluation: Optional[Dict[str, Any]]
    rag_evaluation: Optional[Dict[str, Any]]
    decision: Optional[str]
    eligibility: Optional[str]
    explanation: Optional[str]
    confidence: Optional[float]
    needs_human_review: Optional[bool]
    is_short_circuited: Optional[bool]

    # Trial Metadata & HITL Tracking
    trial_phase: Optional[str]
    trial_status: Optional[str]
    trial_results: Optional[Dict[str, Any]]
    compliance_needed: Optional[bool]
    toxicity_score: Optional[float]
    financial_approved: Optional[bool]
    agent_consensus: Optional[bool]
    final_decision: Optional[str]
    requires_hitl: Optional[bool]
    hitl_reason: Optional[str]
    hitl_approval_status: Optional[str]
    hitl_comments: Optional[str]
    modification: Optional[str]

    # Loop Counters & Stage Control
    refinement_iteration_count: int
    missing_data_query_count: int
    max_missing_data_retries: int
    agent_consensus_reached: bool
    active_evaluation_stage: Annotated[str, pick_latest_str]
    terminal_reason: Optional[str]
    error_message: Optional[str]
    raw_api_response: Optional[Dict[str, Any]]