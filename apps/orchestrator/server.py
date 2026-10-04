"""
Clinical Adjudication Orchestrator Server.
Exposes endpoints for patient lookup, asynchronous multi-agent trial adjudication,
real-time session tracking, PDF report downloads, and HITL modify cycles.
"""

import copy
import io
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Path Resolution & Package Imports
# ---------------------------------------------------------------------------
CURRENT_FILE = Path(__file__).resolve()
REPO_ROOT = CURRENT_FILE.parents[2]

ORCHESTRATOR_DIR = CURRENT_FILE.parent
MCP_EHR_DIR = (REPO_ROOT / "packages" / "mcp-ehr" / "src" / "mcp_ehr").resolve()
SHARED_SCHEMAS_BASE = (REPO_ROOT / "packages" / "shared-schemas").resolve()
SHARED_SCHEMAS_PKG = (SHARED_SCHEMAS_BASE / "shared_schemas").resolve()

for p in [str(REPO_ROOT), str(ORCHESTRATOR_DIR), str(MCP_EHR_DIR), str(SHARED_SCHEMAS_BASE), str(SHARED_SCHEMAS_PKG)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from fhir_client import get_patient, list_patients_for_ui
except ImportError as e:
    raise RuntimeError(f"Failed to import fhir_client from {MCP_EHR_DIR}: {e}")

try:
    from shared_schemas.state import (
        CardiacFunction,
        ComplianceVerdictRecord,
        FinancialVerdictRecord,
        LabResults,
        MultiAgentIterationSnapshot,
        PatientData,
        ProtocolFacts,
        SafetyVerdictRecord,
        TrialState,
        VitalSigns,
    )
except ImportError:
    from state import (
        CardiacFunction,
        ComplianceVerdictRecord,
        FinancialVerdictRecord,
        LabResults,
        MultiAgentIterationSnapshot,
        PatientData,
        ProtocolFacts,
        SafetyVerdictRecord,
        TrialState,
        VitalSigns,
    )

try:
    from apps.orchestrator.report_generator import generate_adjudication_pdf_bytes
except ImportError:
    try:
        from report_generator import generate_adjudication_pdf_bytes
    except ImportError:
        generate_adjudication_pdf_bytes = None

try:
    from apps.orchestrator.graph import app_graph as adjudication_graph
except ImportError:
    try:
        from apps.orchestrator.graph import build_graph
        adjudication_graph = build_graph()
    except ImportError:
        from graph import app_graph as adjudication_graph

# ---------------------------------------------------------------------------
# FastAPI & Session Store
# ---------------------------------------------------------------------------
app = FastAPI(
    title="TrialGuard Clinical Adjudication Orchestrator API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSION_RESULTS: Dict[str, Dict[str, Any]] = {}
SESSION_STATES: Dict[str, TrialState] = {}


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class AdjudicationSubmission(BaseModel):
    patient_id: str = Field(..., description="Patient name, alias, or FHIR ID")
    protocol_id: Optional[str] = Field(default=None, description="Trial protocol identifier")
    proposed_action: str = Field(..., description="Doctor's proposed intervention text")
    name: Optional[str] = None
    cohort: Optional[str] = None


class HitlModificationSubmission(BaseModel):
    updated_action: str = Field(..., description="Modified drug regimen or procedure")
    updated_facts: Optional[Dict[str, Any]] = Field(default=None, description="Clinician-updated protocol facts")
    clinician_notes: Optional[str] = Field(default=None, description="Modification rationale")


class PatientLookupItem(BaseModel):
    patient_id: str
    fhir_id: str
    name: str
    label: str
    age: Optional[int] = None
    sex: Optional[str] = None
    dob: Optional[str] = None
    trial_id: Optional[str] = None
    cohort: Optional[str] = None
    diagnoses: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Normalization Helpers
# ---------------------------------------------------------------------------
def _extract_float(val: Any) -> Optional[float]:
    if isinstance(val, dict):
        val = val.get("value")
    if val is None or str(val).strip().lower() in ("none", "null", ""):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _extract_int(val: Any) -> Optional[int]:
    if isinstance(val, dict):
        val = val.get("value")
    if val is None or str(val).strip().lower() in ("none", "null", ""):
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _normalize_sex(raw_sex: Any) -> str:
    s = str(raw_sex or "").strip().lower()
    if s in ["female", "f"]:
        return "female"
    if s in ["male", "m"]:
        return "male"
    return str(raw_sex) if raw_sex else "unknown"


def normalize_to_patient_data(raw: Dict[str, Any]) -> PatientData:
    raw_vitals = raw.get("vital_signs") or {}
    vitals: VitalSigns = {
        "heart_rate": _extract_float(raw_vitals.get("heart_rate")),
        "blood_pressure_systolic": _extract_int(raw_vitals.get("blood_pressure_systolic")),
        "blood_pressure_diastolic": _extract_int(raw_vitals.get("blood_pressure_diastolic")),
    }

    raw_labs = raw.get("lab_results") or {}
    labs: LabResults = {
        "ALT": _extract_float(raw_labs.get("ALT")),
        "AST": _extract_float(raw_labs.get("AST")),
        "eGFR": _extract_float(raw_labs.get("eGFR")),
        "ANC": _extract_float(raw_labs.get("ANC")),
        "platelets": _extract_float(raw_labs.get("platelets")),
        "hemoglobin": _extract_float(raw_labs.get("hemoglobin")),
        "INR": _extract_float(raw_labs.get("INR")),
        "total_bilirubin": _extract_float(raw_labs.get("total_bilirubin")),
        "serum_creatinine": _extract_float(raw_labs.get("serum_creatinine")),
        "creatinine_clearance": _extract_float(raw_labs.get("creatinine_clearance")),
    }

    raw_cardiac = raw.get("cardiac_function") or {}
    cardiac: CardiacFunction = {
        "LVEF": _extract_float(raw_cardiac.get("LVEF")),
        "QTc": _extract_float(raw_cardiac.get("QTc")),
    }

    raw_facts = raw.get("protocol_facts") or {}
    facts: ProtocolFacts = {
        "oral_anticoagulation_required": raw_facts.get("oral_anticoagulation_required") or raw_facts.get("planned_or_existing_oral_anticoagulation"),
        "acs_pathway": raw_facts.get("acs_pathway"),
        "days_since_acute_coronary_syndrome": _extract_int(raw_facts.get("days_since_acute_coronary_syndrome")),
        "pci_pathway": raw_facts.get("pci_pathway"),
        "days_since_PCI": _extract_int(raw_facts.get("days_since_PCI")),
        "planned_p2y12_duration": _extract_int(raw_facts.get("planned_p2y12_duration")),
        "history_of_intracranial_hemorrhage": raw_facts.get("history_of_intracranial_hemorrhage", False),
        "ongoing_bleeding": raw_facts.get("ongoing_bleeding", False),
        "known_coagulopathy": raw_facts.get("known_coagulopathy", False),
        "cabg_for_index_acs": raw_facts.get("cabg_for_index_acs", False),
        "other_condition_requiring_chronic_anticoagulation": raw_facts.get("other_condition_requiring_chronic_anticoagulation", False),
        "drug_contraindication": raw_facts.get("drug_contraindication") or [],
        "pregnant": raw_facts.get("pregnant", False),
        "breastfeeding": raw_facts.get("breastfeeding", False),
        "woman_of_childbearing_potential": raw_facts.get("woman_of_childbearing_potential", False),
        "pregnancy_test_negative": raw_facts.get("pregnancy_test_negative", True),
    }

    return {
        "patient_id": str(raw.get("patient_id") or raw.get("internal_id") or "UNKNOWN"),
        "internal_id": str(raw.get("internal_id")) if raw.get("internal_id") else None,
        "fhir_id": str(raw.get("fhir_id")) if raw.get("fhir_id") else None,
        "name": raw.get("name"),
        "dob": raw.get("dob") or raw.get("birth_date"),
        "cohort": raw.get("cohort"),
        "age": int(raw.get("age", 50)),
        "sex": _normalize_sex(raw.get("sex")),
        "weight": _extract_float(raw.get("weight")),
        "diagnoses": raw.get("diagnoses") or [],
        "medications": raw.get("medications") or [],
        "allergies": raw.get("allergies") or [],
        "lab_results": labs,
        "vital_signs": vitals,
        "cardiac_function": cardiac,
        "medical_history": raw.get("medical_history") or [],
        "medical_history_narrative": raw.get("medical_history_narrative"),
        "current_symptoms": raw.get("current_symptoms") or [],
        "pregnancy_test_result": raw.get("pregnancy_test_result", "negative"),
        "consent_capacity": raw.get("consent_capacity", True),
        "ecog_status": _extract_int(raw.get("ecog_status")) or 1,
        "last_systemic_therapy_date": raw.get("last_systemic_therapy_date"),
        "protocol_facts": facts,
    }


def build_initial_trial_state(
    patient_data: PatientData, 
    raw_patient: Dict[str, Any], 
    protocol_id: str, 
    proposed_action: str
) -> TrialState:
    pid = patient_data.get("patient_id")
    cohort = patient_data.get("cohort") or "Cohort A - Standard Protocol"
    return {
        "trial_id": protocol_id,
        "patient_id": pid,
        "cohort": cohort,
        "prescribed_action": proposed_action,
        "proposed_action": proposed_action,
        "doctor_query": f"Analyze whether this prescribed action '{proposed_action}' is valid for patient {pid}.",
        "patient": patient_data,
        "raw_fhir_patient": raw_patient,
        "financial_context": {
            "payer_id": "SPONSOR_TRIAL_EXPENSE",
            "insurance_plan": "Clinical Core Grant",
            "coverage_tier": "Tier-1 Investigational",
        },
        "relevant_policies": [],
        "rag_analysis": None,
        "rag_query": None,
        "query": proposed_action,
        "protocol_rules": [],
        "guardrail_1_passed": None,
        "guardrail_2_passed": None,
        "messages": [],
        "audit_logs": [
            {
                "timestamp": time.time(),
                "event": "SESSION_INITIALIZED",
                "patient_id": pid,
                "trial_id": protocol_id,
                "action": proposed_action,
            }
        ],
        "violations": [],
        "matched_criteria": [],
        "unknown_criteria": [],
        "not_applicable_criteria": [],
        "dosage_checks": [],
        "safety_evidence": [],
        "criteria_evaluations": [],
        "evidence": [],
        
        # Multi-Agent Reducer Histories
        "compliance_verdict_history": [],
        "safety_verdict_history": [],
        "financial_verdict_history": [],
        "multi_agent_iteration_history": [],

        "evaluation": None,
        "rag_evaluation": None,
        "decision": None,
        "eligibility": None,
        "explanation": None,
        "confidence": None,
        "needs_human_review": False,
        "is_short_circuited": False,
        "trial_phase": "Phase II",
        "trial_status": "ACTIVE",
        "trial_results": None,
        "compliance_needed": False,
        "toxicity_score": 0.0,
        "financial_approved": True,
        "agent_consensus": False,
        "final_decision": None,
        "requires_hitl": False,
        "hitl_reason": None,
        "hitl_approval_status": "PENDING",
        "hitl_comments": None,
        "modification": None,  # Properly declared in TrialState
        "refinement_iteration_count": 0,
        "missing_data_query_count": 0,
        "max_missing_data_retries": 2,
        "agent_consensus_reached": False,
        "active_evaluation_stage": "INITIAL_INGESTION",
        "terminal_reason": None,
        "error_message": None,
        "raw_api_response": None,
    }


# ---------------------------------------------------------------------------
# Background Graph Execution
# ---------------------------------------------------------------------------
async def run_adjudication_workflow(session_id: str, state_payload: TrialState) -> None:
    patient = state_payload["patient"]
    print("\n" + "=" * 80)
    print(f"🚀 [STARTING ADJUDICATION PIPELINE] Session: {session_id}")
    print(f"   Patient : {patient.get('name')} ({patient.get('patient_id')} / FHIR #{patient.get('fhir_id')})")
    print(f"   Cohort  : {state_payload.get('cohort')}")
    print(f"   Trial   : {state_payload.get('trial_id')}")
    print(f"   Action  : {state_payload.get('prescribed_action')}")
    print(f"   Mod     : {state_payload.get('modification') or '(Fresh Attempt)'}")
    print("=" * 80)

    history_reducer_keys = {
        "compliance_verdict_history",
        "safety_verdict_history",
        "financial_verdict_history",
        "multi_agent_iteration_history",
        "audit_logs",
    }

    try:
        config = {"configurable": {"thread_id": session_id}}
        for output in adjudication_graph.stream(state_payload, stream_mode="updates", config=config):
            for node_name, node_update in output.items():
                print(f"\n  ▶ [NODE EXECUTED: {node_name.upper()}]")
                
                # Apply history reducer logic without destructive key overwrites
                for r_key in history_reducer_keys:
                    if r_key in node_update and node_update[r_key]:
                        existing = accumulated_state.get(r_key, [])
                        accumulated_state[r_key] = existing + node_update[r_key]

                # Update non-history fields (including violations replacement)
                filtered_update = {k: v for k, v in node_update.items() if k not in history_reducer_keys}
                accumulated_state.update(filtered_update)

                stage = node_update.get("active_evaluation_stage")
                if stage:
                    print(f"     Stage: {stage}")

                # Sub-Agent Outputs
                if "compliance_verdict_history" in node_update and node_update["compliance_verdict_history"]:
                    comp = node_update["compliance_verdict_history"][-1]
                    print(f"     📜 Compliance Check: {comp.get('compliance_status')} (Confidence: {comp.get('confidence')})")

                if "safety_verdict_history" in node_update and node_update["safety_verdict_history"]:
                    safe = node_update["safety_verdict_history"][-1]
                    print(f"     🧪 Safety Check: {safe.get('safety_status')} (Risk: {safe.get('risk_score')})")

                if "financial_verdict_history" in node_update and node_update["financial_verdict_history"]:
                    fin = node_update["financial_verdict_history"][-1]
                    print(f"     💳 Financial Check: {fin.get('coverage_status')} (Tier: {fin.get('tier')})")

                # Violations
                violations = node_update.get("violations")
                if violations:
                    print(f"     ⚠️  Active Violations ({len(violations)}):")
                    for v in violations:
                        rule = v.get("rule_id") or v.get("parameter")
                        desc = v.get("reason") or str(v)
                        print(f"        - [{v.get('severity', 'HARD')}] {rule}: {desc}")

                stage_decision = node_update.get("decision") or node_update.get("final_decision")
                if stage_decision:
                    print(f"     ⚖️  Verdict: {stage_decision}")

        final_decision = (
            accumulated_state.get("final_decision")
            or accumulated_state.get("decision")
            or (accumulated_state.get("rag_analysis") or {}).get("decision")
            or "UNKNOWN"
        )
        eligibility = (
            accumulated_state.get("eligibility")
            or (accumulated_state.get("rag_analysis") or {}).get("eligibility")
        )

        SESSION_STATES[session_id] = accumulated_state

        SESSION_RESULTS[session_id] = {
            "status": "COMPLETED",
            "decision": final_decision,
            "eligibility": eligibility,
            "requires_hitl": accumulated_state.get("requires_hitl", False),
            "hitl_status": accumulated_state.get("hitl_approval_status"),
            "hitl_reason": accumulated_state.get("hitl_reason"),
            "violations": accumulated_state.get("violations", []),
            "compliance_history": accumulated_state.get("compliance_verdict_history", []),
            "safety_history": accumulated_state.get("safety_verdict_history", []),
            "financial_history": accumulated_state.get("financial_verdict_history", []),
            "multi_agent_history": accumulated_state.get("multi_agent_iteration_history", []),
            "active_stage": accumulated_state.get("active_evaluation_stage"),
            "patient": accumulated_state.get("patient"),
        }

        print("\n" + "=" * 80)
        print("🏁 [WORKFLOW SEALED]")
        print(f"   Verdict     : {final_decision} ({eligibility})")
        print(f"   Refinements : {accumulated_state.get('refinement_iteration_count', 0)}")
        print("=" * 80 + "\n")

    except Exception as exc:
        SESSION_RESULTS[session_id] = {"status": "FAILED", "error": str(exc)}
        print(f"\n❌ [WORKFLOW FAILED]: {exc}\n")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok", "service": "orchestrator", "version": "1.0.0"}


@app.get("/api/patients", response_model=List[PatientLookupItem])
def search_patients(
    query: Optional[str] = Query(default="", description="Fuzzy search query"),
    limit: int = Query(default=15, ge=1, le=50),
) -> List[PatientLookupItem]:
    try:
        clean_q = query.strip() if query else None
        raw_results = list_patients_for_ui(query=clean_q)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed querying patient list: {exc}")

    output: List[PatientLookupItem] = []
    for r in raw_results[:limit]:
        pid = str(r.get("internal_id") or r.get("patient_id"))
        fid = str(r.get("fhir_id", pid))
        name = r.get("name", f"Patient {pid}")
        output.append(
            PatientLookupItem(
                patient_id=pid,
                fhir_id=fid,
                name=name,
                label=r.get("display_label", f"{pid} - {name}"),
                age=r.get("age"),
                sex=r.get("sex"),
                dob=r.get("dob"),
                trial_id=r.get("trial_id"),
                cohort=r.get("cohort"),
                diagnoses=r.get("diagnoses", []),
            )
        )
    return output


@app.post("/api/adjudicate")
async def initiate_adjudication(
    req: AdjudicationSubmission, background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    clean_id = req.patient_id.strip()
    if not clean_id:
        raise HTTPException(status_code=400, detail="patient_id is required")

    resolved_id = clean_id
    if not clean_id.upper().startswith(("P0", "PT-")) and not clean_id.isdigit():
        matches = list_patients_for_ui(query=clean_id)
        if matches:
            resolved_id = str(matches[0].get("internal_id") or matches[0].get("patient_id"))

    try:
        raw_patient = get_patient(resolved_id)
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"FHIR retrieval failure: {exc}")

    patient_data: PatientData = normalize_to_patient_data(raw_patient)
    if req.cohort:
        patient_data["cohort"] = req.cohort

    protocol_id = req.protocol_id or raw_patient.get("trial_id") or "NCT02415400"

    trial_state: TrialState = build_initial_trial_state(
        patient_data=patient_data,
        raw_patient=raw_patient,
        protocol_id=protocol_id,
        proposed_action=req.proposed_action,
    )

    session_id = f"adj-{patient_data.get('patient_id', 'pt').lower()}-{int(time.time())}"
    SESSION_RESULTS[session_id] = {"status": "IN_PROGRESS"}
    SESSION_STATES[session_id] = trial_state

    background_tasks.add_task(
        run_adjudication_workflow,
        session_id=session_id,
        state_payload=trial_state,
    )

    return {
        "status": "initiated",
        "session_id": session_id,
        "trial_id": protocol_id,
        "cohort": trial_state.get("cohort"),
        "patient": {
            "patient_id": patient_data.get("patient_id"),
            "fhir_id": patient_data.get("fhir_id"),
            "name": patient_data.get("name"),
            "age": patient_data.get("age"),
            "dob": patient_data.get("dob"),
        },
        "message": f"Resolved '{req.patient_id}' -> #{patient_data.get('fhir_id')} ({patient_data.get('name')}). Adjudication pipeline started.",
    }


@app.post("/api/adjudicate/{session_id}/modify")
async def modify_and_readjudicate(
    session_id: str,
    mod: HitlModificationSubmission,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    """Allows clinician to submit a modified regimen and re-trigger sub-agent evaluation."""
    if session_id not in SESSION_STATES:
        raise HTTPException(status_code=404, detail="Session state not found for modification")

    state = copy.deepcopy(SESSION_STATES[session_id])
    state["refinement_iteration_count"] = state.get("refinement_iteration_count", 0) + 1
    state["prescribed_action"] = mod.updated_action
    state["proposed_action"] = mod.updated_action
    
    # Crucial: Register modification string for downstream microservices
    mod_rationale = mod.clinician_notes or f"Action adjusted to {mod.updated_action}"
    state["modification"] = mod_rationale
    state["hitl_comments"] = mod_rationale

    if mod.updated_facts and "patient" in state:
        state["patient"].setdefault("protocol_facts", {})
        state["patient"]["protocol_facts"].update(mod.updated_facts)

    state["audit_logs"].append({
        "timestamp": time.time(),
        "step": "hitl_modification",
        "action": mod.updated_action,
        "modification": mod_rationale,
        "notes": mod_rationale,
        "iteration": state["refinement_iteration_count"],
    })

    SESSION_RESULTS[session_id] = {"status": "IN_PROGRESS"}
    SESSION_STATES[session_id] = state

    background_tasks.add_task(
        run_adjudication_workflow,
        session_id=session_id,
        state_payload=state,
    )

    return {
        "status": "re_evaluating",
        "session_id": session_id,
        "iteration": state["refinement_iteration_count"],
        "action": mod.updated_action,
        "modification": mod_rationale,
    }


@app.get("/api/adjudicate/{session_id}")
def get_adjudication_status(session_id: str) -> Dict[str, Any]:
    if session_id not in SESSION_RESULTS:
        raise HTTPException(status_code=404, detail="Session not found")
    return SESSION_RESULTS[session_id]


@app.get("/api/adjudicate/{session_id}/pdf")
def download_pdf_report(session_id: str):
    """Generates and streams a 21 CFR Part 11 compliant audit PDF for the session."""
    if session_id not in SESSION_STATES:
        raise HTTPException(status_code=404, detail="Adjudication session not found")

    if generate_adjudication_pdf_bytes is None:
        raise HTTPException(status_code=500, detail="ReportLab PDF generator is not installed or configured")

    state = SESSION_STATES[session_id]

    comp_latest = state.get("compliance_verdict_history", [{}])[-1] if state.get("compliance_verdict_history") else {}
    safe_latest = state.get("safety_verdict_history", [{}])[-1] if state.get("safety_verdict_history") else {}
    fin_latest = state.get("financial_verdict_history", [{}])[-1] if state.get("financial_verdict_history") else {}

    report_payload = {
        "header": {
            "patient_id": state.get("patient_id"),
            "trial_id": state.get("trial_id"),
            "cohort": state.get("cohort"),
            "prescribed_action": state.get("prescribed_action"),
            "modification": state.get("modification"),
        },
        "final_adjudication": {
            "decision": state.get("final_decision") or state.get("decision", "UNKNOWN"),
            "eligibility": state.get("eligibility", "PENDING"),
            "confidence": state.get("confidence", 0.95),
            "hitl_approval_status": state.get("hitl_approval_status", "PENDING"),
            "clinician_rationale": state.get("hitl_comments") or "Automated multi-agent consensus sealed.",
        },
        "sub_agent_breakdown": {
            "compliance_agent": comp_latest,
            "safety_agent": safe_latest,
            "financial_agent": fin_latest,
        },
        "active_violations": state.get("violations", []),
        "audit_trail": state.get("audit_logs", []),
    }

    pdf_buffer = generate_adjudication_pdf_bytes(report_payload)
    filename = f"TrialGuard_Adjudication_{state.get('patient_id', 'report')}.pdf"

    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)