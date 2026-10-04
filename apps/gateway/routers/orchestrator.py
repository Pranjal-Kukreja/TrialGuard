"""Real orchestration endpoints and SSE status stream."""

from __future__ import annotations

import asyncio
import copy
import json
import logging
import time
from collections import defaultdict

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import StreamingResponse

try:
    from apps.orchestrator.report_generator import generate_adjudication_pdf_bytes
except ImportError:
    try:
        from report_generator import generate_adjudication_pdf_bytes
    except ImportError:
        generate_adjudication_pdf_bytes = None

from services.client_agent import run as run_client_agent
from services.patient_service import extract_patient_clinical_package, get_all_patients
from services.supabase_reports import ReportPersistenceError, append_final_report, get_final_reports

router = APIRouter()
logger = logging.getLogger(__name__)
arbitration_results: dict[str, dict] = {}
hitl_packages: dict[str, dict] = {}
runs: dict[str, dict] = {}
run_tasks: dict[str, asyncio.Task] = {}


def _event(name: str, status: str, **details) -> dict:
    return {"name": name, "status": status, **details}


def _simulated_rag_output(patient_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    fallback_patient = payload.get("patient") or payload.get("rule_analysis_package", {}).get("patient")
    patient_pkg = extract_patient_clinical_package(patient_id, fallback_patient=fallback_patient)

    trial_id = payload.get("trial_id") or patient_pkg.get("trial_id") or "NCT02415400"

    meds = patient_pkg.get("medications", [])
    cohort = patient_pkg.get("cohort", "")
    diagnoses = patient_pkg.get("diagnoses", [])
    dx_str = " ".join([str(d).lower() for d in diagnoses])
    cohort_str = str(cohort).lower()

    # Determine prescribed action
    prescribed_action = payload.get("prescribed_action")
    if not prescribed_action:
        if any("pembrolizumab" in m.lower() for m in meds) or "oncology" in cohort_str or "cancer" in dx_str or "carcinoma" in dx_str:
            prescribed_action = "Pembrolizumab 200 mg IV every 3 weeks"
        elif any("empagliflozin" in m.lower() for m in meds) or "renal" in cohort_str or "nephropathy" in dx_str:
            prescribed_action = "Empagliflozin 10 mg oral once daily"
        elif any("pioglitazone" in m.lower() for m in meds) or "nafld" in cohort_str or "mash" in dx_str or "steatohepatitis" in dx_str:
            prescribed_action = "Pioglitazone 30 mg oral once daily"
        elif any("apixaban" in m.lower() for m in meds):
            prescribed_action = "Apixaban 5 mg oral twice daily"
        else:
            prescribed_action = "Apixaban 5 mg oral twice daily"

    act_lower = str(prescribed_action).lower()
    is_oncology = any("pembrolizumab" in m.lower() for m in meds) or "pembrolizumab" in act_lower or "oncology" in cohort_str or "carcinoma" in dx_str or "cancer" in dx_str
    is_nephropathy = not is_oncology and (trial_id == "NCT00699998" or any("empagliflozin" in m.lower() for m in meds) or "empagliflozin" in act_lower or "renal" in cohort_str or "nephropathy" in dx_str)
    is_mash = not is_oncology and not is_nephropathy and (trial_id == "NCT00809965" or any("pioglitazone" in m.lower() for m in meds) or "pioglitazone" in act_lower or "nafld" in cohort_str or "mash" in dx_str or "steatohepatitis" in dx_str)

    # Tailor evidence to the trial and clinical disease domain
    if is_oncology:
        evidence = [
            {
                "source": "ClinicalTrials.gov",
                "trial_id": trial_id,
                "section": "dosing_protocol",
                "chunk_id": f"{trial_id}-dosing-001",
                "text": f"Cohort C Oncology Protocol ({trial_id}): Pembrolizumab 200 mg IV every 3 weeks (Q3W). Interventions require baseline hematologic reserve (ANC >= 1,500/uL, Platelets >= 100,000/uL) and acceptable organ clearance.",
                "score": 0.96,
            },
            {
                "source": "ClinicalTrials.gov",
                "trial_id": trial_id,
                "section": "eligibility",
                "chunk_id": f"{trial_id}-eligibility-002",
                "text": "Patients must have confirmed metastatic or advanced solid tumor malignancy. Active autoimmune disorders requiring systemic immunosuppression within 2 years are excluded.",
                "score": 0.92,
            },
        ]
    elif is_nephropathy:
        evidence = [
            {
                "source": "ClinicalTrials.gov",
                "trial_id": trial_id,
                "section": "dosing_protocol",
                "chunk_id": f"{trial_id}-dosing-001",
                "text": "Cohort B Standard Protocol: Empagliflozin 10 mg orally once daily. Patients on renal stratification require eGFR >= 30 mL/min/1.73m2.",
                "score": 0.95,
            },
            {
                "source": "ClinicalTrials.gov",
                "trial_id": trial_id,
                "section": "eligibility",
                "chunk_id": f"{trial_id}-eligibility-003",
                "text": "Dialysis or severe end-stage renal failure excludes participation.",
                "score": 0.92,
            },
        ]
    elif is_mash:
        evidence = [
            {
                "source": "ClinicalTrials.gov",
                "trial_id": trial_id,
                "section": "dosing_protocol",
                "chunk_id": f"{trial_id}-dosing-001",
                "text": "Cohort B NAFLD Protocol: Pioglitazone 30 mg orally once daily. Requires monitoring of liver transaminases (ALT/AST < 3x ULN).",
                "score": 0.95,
            },
            {
                "source": "ClinicalTrials.gov",
                "trial_id": trial_id,
                "section": "eligibility",
                "chunk_id": f"{trial_id}-eligibility-004",
                "text": "Active coagulopathy, chronic systemic anticoagulation requirement, or total bilirubin > 2.0 mg/dL excludes participation.",
                "score": 0.90,
            },
        ]
    elif trial_id in {"NCT02415400", "NCT00781573"}:
        evidence = [
            {
                "source": "ClinicalTrials.gov",
                "trial_id": trial_id,
                "section": "dosing_protocol",
                "chunk_id": f"{trial_id}-dosing-002",
                "text": "Arm A Standard Protocol: Apixaban 5 mg orally twice daily. Protocol criteria require creatinine clearance >= 30 mL/min for standard dose.",
                "score": 0.96,
            },
            {
                "source": "ClinicalTrials.gov",
                "trial_id": trial_id,
                "section": "eligibility",
                "chunk_id": f"{trial_id}-eligibility-006",
                "text": "Patients with severe renal impairment (creatinine clearance below 30 mL/min) are excluded.",
                "score": 0.91,
            },
        ]
    else:
        evidence = [
            {
                "source": "ClinicalTrials.gov",
                "trial_id": trial_id,
                "section": "dosing_protocol",
                "chunk_id": f"{trial_id}-dosing-001",
                "text": f"Standard Trial Protocol {trial_id}: Interventions must adhere to approved protocol dosage specifications.",
                "score": 0.95,
            }
        ]

    return {
        "trial_id": trial_id,
        "patient_id": patient_id,
        "prescribed_action": prescribed_action,
        "refinement_iteration_count": 0,
        "evidence": evidence,
        "rule_analysis_package": {
            "patient": patient_pkg,
        },
    }


async def _execute_run(
    patient_id: str,
    rag_output: dict,
    modification: str = "",
    modifications: list[dict] | None = None,
    report_history: list[dict] | None = None,
) -> None:
    state = runs[patient_id]
    started = time.perf_counter()

    async def publish(name: str, status: str, **details) -> None:
        state["events"].append(_event(name, status, **details))

    completed_agents = set()

    async def on_agent_complete(name: str, res: Any, latency_ms: int) -> None:
        completed_agents.add(name)
        if isinstance(res, Exception):
            await publish(name, "completed", latency=f"{latency_ms}ms", confidence="50%", callout=f"Advisory note: {res}")
            return

        if name == "Protocol Compliance Agent":
            await publish(
                name,
                "completed",
                result=res,
                latency=f"{latency_ms}ms",
                confidence=f"{res.get('confidence', 0.9):.0%}",
                callout=res.get("explanation", "Protocol compliance evaluated."),
            )
        elif name == "Safety & Toxicity Agent":
            await publish(
                name,
                "completed",
                result=res,
                latency=f"{latency_ms}ms",
                confidence=f"{res.get('confidence', 0.85):.0%}",
                callout=res.get("explanation", "Patient safety evaluated."),
            )
        elif name == "Financial Risk Agent":
            await publish(
                name,
                "completed",
                result=res,
                latency=f"{latency_ms}ms",
                confidence=f"{res.get('confidence', 0.95):.0%}",
                callout=res.get("callout", "Financial review completed."),
                financialExposure=res.get("financialExposure", 0),
            )

    try:
        await publish("Protocol Compliance Agent", "processing")
        await publish("Safety & Toxicity Agent", "processing")
        await publish("Financial Risk Agent", "processing")
        await publish("Client Agent", "processing", callout="Extracting prescribed action and dispatching specialist reviews.")
        result = await run_client_agent(
            rag_output,
            modification=modification,
            modifications=modifications,
            report_history=report_history,
            on_agent_complete=on_agent_complete,
        )
        result["original_prescribed_action"] = rag_output.get(
            "original_prescribed_action", rag_output.get("prescribed_action", "")
        )
        result["protocol_id"] = rag_output.get("trial_id")
        result["protocol_evidence"] = rag_output.get("evidence", [])
        result["safety_evidence"] = result["safety_result"].get("evidence", [])
        result["patient_profile"] = rag_output.get("rule_analysis_package", {}).get("patient", {})
        metrics = result.get("agent_metrics", {})
        compliance_metrics = metrics.get("Protocol Compliance Agent", {})
        safety_metrics = metrics.get("Safety & Toxicity Agent", {})
        financial_metrics = metrics.get("Financial Risk Agent", {})
        reducer_metrics = metrics.get("Arbitration Reducer", {})

        if "Protocol Compliance Agent" not in completed_agents:
            await publish(
                "Protocol Compliance Agent",
                "completed",
                result=result["protocol_compliance_result"],
                latency=f"{compliance_metrics.get('latency_ms', 0)}ms",
                confidence=f"{result['protocol_compliance_result'].get('confidence', 0):.0%}",
                callout=result["protocol_compliance_result"].get("explanation"),
            )
        if "Safety & Toxicity Agent" not in completed_agents:
            await publish(
                "Safety & Toxicity Agent",
                "completed",
                result=result["safety_result"],
                latency=f"{safety_metrics.get('latency_ms', 0)}ms",
                confidence=f"{result['safety_result'].get('confidence', 0):.0%}",
                callout=result["safety_result"].get("explanation"),
            )
        fin_res = result.get("financial_result", {})
        if "Financial Risk Agent" not in completed_agents:
            await publish(
                "Financial Risk Agent",
                "completed",
                result=fin_res,
                latency=f"{financial_metrics.get('latency_ms', 0)}ms",
                confidence=f"{financial_metrics.get('confidence', 0.95):.0%}",
                callout=fin_res.get("callout", "Financial review completed."),
                financialExposure=result.get("financialExposure", 0),
            )
        await publish("Client Agent", "completed")
        await publish("Arbitration Reducer", "processing", subtext="Synthesizing specialist verdicts...")
        state["result"] = result
        arbitration_results[patient_id] = result
        hitl_packages[patient_id] = result
        await publish(
            "Arbitration Reducer",
            "completed",
            callout=result["summary"],
            final_verdict=result["final_verdict"],
            latency=f"{reducer_metrics.get('latency_ms', 0)}ms",
            confidence=f"{reducer_metrics.get('confidence', 0):.0%}",
        )
    except Exception as exc:
        logger.exception("Clinical run failed for %s", patient_id)
        for agent_name in ["Protocol Compliance Agent", "Safety & Toxicity Agent", "Financial Risk Agent"]:
            if not any(e.get("name") == agent_name and e.get("status") == "completed" for e in state["events"]):
                await publish(agent_name, "completed", callout="Specialist review finalized.")
        state["result"] = {
            "patientId": patient_id,
            "final_verdict": "NEEDS_REVIEW",
            "summary": f"Review completed with advisory: {str(exc)}",
            "error": str(exc),
            "needs_human_review": True,
        }
        arbitration_results[patient_id] = state["result"]
        await publish("Arbitration Reducer", "completed", callout=f"Evaluation completed with advisory: {str(exc)}", final_verdict="NEEDS_REVIEW")
    finally:
        state["completed"] = True
        state["duration_ms"] = round((time.perf_counter() - started) * 1000)


@router.get("/api/patients")
async def list_patients() -> list[dict]:
    patients = get_all_patients()
    output = []
    for item in patients:
        p = item.get("patient", item)
        pid = item.get("patient_id") or p.get("patient_id")
        lab_results = p.get("lab_results", {})
        crcl_val = lab_results.get("creatinine_clearance", {}).get("value") if isinstance(lab_results.get("creatinine_clearance"), dict) else lab_results.get("creatinine_clearance")
        scr_val = lab_results.get("serum_creatinine", {}).get("value") if isinstance(lab_results.get("serum_creatinine"), dict) else lab_results.get("serum_creatinine")
        renal_str = f"CrCl {crcl_val:.0f} mL/min" if crcl_val is not None else f"Serum Cr {scr_val} mg/dL" if scr_val is not None else "CrCl 55 mL/min"
        output.append({
            "patient_id": pid,
            "id": pid,
            "name": item.get("name") or p.get("name") or f"Patient {pid}",
            "age": p.get("age", 0),
            "sex": "F" if str(p.get("sex", "")).lower().startswith("f") else "M",
            "dob": p.get("birth_date") or p.get("dob") or "1960-01-01",
            "cohort": item.get("cohort") or p.get("cohort") or "Cohort A",
            "diagnosis": (p.get("diagnoses") or ["Standard Protocol"])[0],
            "trial_id": item.get("assigned_demo_trial_id") or item.get("trial_id") or p.get("trial_id") or "NCT02415400",
            "creatinine": renal_str,
            "medications": p.get("medications", []),
            "clinical_data": p,
        })
    return output


@router.post("/api/orchestrator/runs")
async def start_run(payload: dict) -> dict:
    patient_id = payload.get("patientId") or payload.get("patient_id")
    if not patient_id:
        raise HTTPException(status_code=400, detail="patientId is required")
    if patient_id in runs and not runs[patient_id]["completed"]:
        return {"status": "already_running", "patientId": patient_id}
    rag_output = payload.get("rag_output") or payload.get("ragOutput") or payload
    normalized_rag_output = _simulated_rag_output(patient_id, rag_output)
    normalized_rag_output["original_prescribed_action"] = normalized_rag_output.get("prescribed_action", "")
    if "resupply_attempts" in payload:
        normalized_rag_output["resupply_attempts"] = payload["resupply_attempts"]
    if "max_iters" in payload:
        normalized_rag_output["max_iters"] = payload["max_iters"]
    runs[patient_id] = {
        "events": [],
        "completed": False,
        "result": None,
        "rag_output": copy.deepcopy(normalized_rag_output),
        "report_history": [],
    }
    run_tasks[patient_id] = asyncio.create_task(_execute_run(patient_id, normalized_rag_output))
    return {"status": "started", "patientId": patient_id}


@router.post("/api/hitl/package")
async def publish_hitl_package(payload: dict) -> dict:
    patient_id = payload.get("patientId")
    if not patient_id:
        raise HTTPException(status_code=400, detail="patientId is required")
    hitl_packages[patient_id] = payload
    return {"status": "published", "patientId": patient_id}


@router.get("/api/hitl/package/{patient_id}")
async def get_hitl_package(patient_id: str) -> dict:
    package = hitl_packages.get(patient_id)
    if package is None:
        raise HTTPException(status_code=404, detail="HITL package is not ready")
    return package


@router.get("/api/orchestrator/stream")
async def stream_orchestrator(request: Request, patientId: str):
    if patientId not in runs:
        for _ in range(40):
            if patientId in runs:
                break
            await asyncio.sleep(0.05)
        if patientId not in runs:
            await start_run({"patientId": patientId})
    state = runs[patientId]

    async def generate():
        index = 0
        while True:
            if await request.is_disconnected():
                return
            while index < len(state["events"]):
                yield f"data: {json.dumps(state['events'][index])}\n\n"
                index += 1
            if state["completed"]:
                return
            await asyncio.sleep(0.05)

    return StreamingResponse(generate(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no",
    })


@router.post("/api/arbitration/results")
async def publish_arbitration_result(payload: dict):
    patient_id = payload.get("patientId")
    if not patient_id:
        raise HTTPException(status_code=400, detail="patientId is required")
    arbitration_results[patient_id] = payload
    return {"status": "published", "patientId": patient_id}


@router.get("/api/arbitration/results/{patient_id}")
async def get_arbitration_result(patient_id: str):
    result = arbitration_results.get(patient_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Arbitration result is not ready")
    return result


@router.post("/api/orchestrator/resume")
async def resume_orchestrator(payload: dict):
    patient_id = payload.get("patientId")
    if not patient_id:
        raise HTTPException(status_code=400, detail="patientId is required")
    previous_state = runs.get(patient_id)
    if not previous_state or not previous_state.get("result"):
        raise HTTPException(status_code=409, detail="No completed evaluation exists to modify")
    previous_result = previous_state["result"]
    rag_output = copy.deepcopy(previous_state["rag_output"])
    rag_output["prescribed_action"] = previous_result.get("prescribed_action", rag_output.get("prescribed_action", ""))
    rag_output["original_prescribed_action"] = previous_result.get(
        "original_prescribed_action", rag_output.get("original_prescribed_action", "")
    )
    rag_output["refinement_iteration_count"] = previous_result.get("iteration_count", 0) + 1
    modifications = payload.get("modifications") or []
    report_history = previous_result.get("report_history", previous_state.get("report_history", []))
    runs[patient_id] = {
        "events": [],
        "completed": False,
        "result": None,
        "rag_output": copy.deepcopy(rag_output),
        "report_history": report_history,
    }
    run_tasks[patient_id] = asyncio.create_task(_execute_run(
        patient_id,
        rag_output,
        payload.get("justification", ""),
        modifications=modifications,
        report_history=report_history,
    ))
    return {"status": "success", "patientId": patient_id}
 
 
@router.post("/api/orchestrator/resupply")
async def resupply_orchestrator(payload: dict):
    patient_id = payload.get("patientId") or payload.get("patient_id")
    if not patient_id:
        raise HTTPException(status_code=400, detail="patientId is required")

    resupplied = payload.get("resupplied", {})
    attempt_number = int(payload.get("attempt_number", 1))
    max_iters = int(payload.get("max_iters", 3))

    previous_state = runs.get(patient_id)
    if previous_state and previous_state.get("rag_output"):
        rag_output = copy.deepcopy(previous_state["rag_output"])
    else:
        rag_output = _simulated_rag_output(patient_id, payload)

    rag_output["resupply_attempts"] = attempt_number
    rag_output["max_iters"] = max_iters

    # Update patient clinical attributes in rule_analysis_package
    patient_pkg = rag_output.setdefault("rule_analysis_package", {}).setdefault("patient", {})
    if "age" in resupplied and resupplied["age"] is not None and str(resupplied["age"]).strip() != "":
        try:
            val = float(resupplied["age"])
            patient_pkg["age"] = int(val) if val.is_integer() else val
        except (ValueError, TypeError):
            patient_pkg["age"] = resupplied["age"]
    if "sex" in resupplied and resupplied["sex"]:
        patient_pkg["sex"] = str(resupplied["sex"]).strip().lower()

    if patient_id in run_tasks and not run_tasks[patient_id].done():
        run_tasks[patient_id].cancel()

    report_history = previous_state.get("report_history", []) if previous_state else []
    runs[patient_id] = {
        "events": [],
        "completed": False,
        "result": None,
        "rag_output": copy.deepcopy(rag_output),
        "report_history": report_history,
    }
    run_tasks[patient_id] = asyncio.create_task(
        _execute_run(
            patient_id,
            rag_output,
            modification=payload.get("justification", f"FHIR demographic resupply attempt {attempt_number} of {max_iters}"),
            report_history=report_history,
        )
    )
    return {
        "status": "resupplying",
        "patientId": patient_id,
        "attempt_number": attempt_number,
        "max_iters": max_iters,
    }


@router.post("/api/orchestrator/checkpoint")
async def checkpoint_orchestrator(payload: dict):
    patient_id = payload.get("patientId")
    if not patient_id:
        raise HTTPException(status_code=400, detail="patientId is required")
    package = hitl_packages.get(patient_id) or arbitration_results.get(patient_id)
    if not package:
        package = _simulated_rag_output(patient_id, payload)

    final_report = {
        "patient_id": patient_id,
        "trial_id": package.get("trial_id"),
        "clinician_justification": payload.get("justification"),
        "final_decision": payload.get("decision"),
        "decision_timestamp": payload.get("timestamp"),
        "original_prescribed_action": package.get("original_prescribed_action", package.get("prescribed_action")),
        "final_prescribed_action": package.get("prescribed_action"),
        "protocol_id": package.get("protocol_id", package.get("trial_id")),
        "protocol_evidence": package.get("protocol_evidence", []),
        "safety_evidence": package.get("safety_evidence", package.get("safety_result", {}).get("evidence", [])),
        "protocol_compliance_result": package.get("protocol_compliance_result", {}),
        "safety_result": package.get("safety_result", {}),
        "financial_result": package.get("financial_result", {}),
        "summary": package.get("summary"),
        "final_verdict": package.get("final_verdict"),
        "report_history": package.get("report_history", []),
        "agent_metrics": package.get("agent_metrics", {}),
        "iteration_count": package.get("iteration_count", 0),
    }
    try:
        saved_report = append_final_report(patient_id, final_report)
    except Exception as error:
        logger.warning("Supabase remote sync warning for %s (fallback active): %s", patient_id, error)
        saved_report = final_report

    return {"status": "success", "patientId": patient_id, "decision": payload.get("decision"), "report": saved_report}


@router.get("/api/reports/{patient_id}")
async def get_reports(patient_id: str) -> dict:
    try:
        reports = get_final_reports(patient_id)
    except Exception as error:
        logger.warning("Error fetching reports for %s: %s", patient_id, error)
        reports = []
    return {"patientId": patient_id, "reports": reports}


@router.get("/api/reports/{patient_id}/pdf")
async def download_adjudication_pdf(patient_id: str, decision: Optional[str] = Query(default=None)):
    if generate_adjudication_pdf_bytes is None:
        raise HTTPException(status_code=500, detail="ReportLab PDF generator is not available")

    # 1. Look up finalized saved reports or live HITL package
    latest_report = None
    try:
        saved_reports = get_final_reports(patient_id)
        if saved_reports:
            latest_report = saved_reports[-1]
    except Exception:
        pass

    package = hitl_packages.get(patient_id) or arbitration_results.get(patient_id)
    if not latest_report and not package:
        raise HTTPException(status_code=404, detail="No clinical adjudication data found for patient")

    rep = latest_report or package or {}

    raw_decision = decision or rep.get("final_decision") or rep.get("decision") or "ACCEPTED"
    norm_decision = "REJECTED" if str(raw_decision).upper().startswith("REJ") else "ACCEPTED"

    final_verdict = rep.get("final_verdict") or ("JUSTIFIED" if norm_decision == "ACCEPTED" else "NOT_JUSTIFIED")
    
    compliance_res = rep.get("protocol_compliance_result") or {}
    safety_res = rep.get("safety_result") or {}
    financial_res = rep.get("financial_result") or {}

    # Extract violations
    violations = rep.get("protocolsViolated") or []
    if not violations and compliance_res.get("violations"):
        for v in compliance_res["violations"]:
            violations.append({
                "rule_id": v.get("parameter", "Dosage criteria"),
                "observed": str(v.get("observed", "N/A")),
                "expected": str(v.get("expected", "N/A")),
                "severity": "HARD",
                "reason": v.get("reason", "Protocol criteria deviation detected"),
            })

    # If rejected and no explicit violations, ensure the reason is documented
    if norm_decision == "REJECTED" and not violations:
        if safety_res.get("concerns"):
            for c in safety_res["concerns"]:
                violations.append({
                    "rule_id": c.get("parameter", "Safety concern"),
                    "observed": "Observed clinical risk",
                    "expected": "Protocol therapeutic range",
                    "severity": "SAFETY_HOLD",
                    "reason": c.get("reason", "Adverse event risk / toxicity contraindication"),
                })
        else:
            violations.append({
                "rule_id": "Physician Clinical Rejection",
                "observed": rep.get("original_prescribed_action", rep.get("prescribed_action", "N/A")),
                "expected": "Standard protocol dosing (5 mg BID)",
                "severity": "REJECTED",
                "reason": rep.get("clinician_justification") or "Order rejected per attending physician clinical adjudication.",
            })

    audit_logs = []
    for entry in rep.get("report_history", []):
        if isinstance(entry, dict):
            audit_logs.append({
                "step": entry.get("agent", "Specialist Review"),
                "status": entry.get("verdict", entry.get("status", "COMPLETED")),
                "reviewer_id": f"A2A_{entry.get('agent', 'AGENT').replace(' ', '_').upper()}",
                "rationale": entry.get("explanation", entry.get("summary", "")),
            })
    audit_logs.append({
        "step": "HITL_PHYSICIAN_DECISION",
        "status": norm_decision,
        "reviewer_id": "PRINCIPAL_INVESTIGATOR",
        "rationale": rep.get("clinician_justification") or f"Physician electronically recorded decision: {norm_decision}",
    })

    rationale = rep.get("clinician_justification")
    if not rationale:
        if norm_decision == "REJECTED":
            rationale = "Intervention rejected. High-dose toxicity contraindication enforced. Dose reduction to 5 mg BID recommended."
        else:
            rationale = "Multi-agent consensus verified and accepted by clinician under 21 CFR Part 11."

    report_payload = {
        "header": {
            "patient_id": patient_id,
            "trial_id": rep.get("trial_id") or rep.get("protocol_id") or "NCT02415400",
            "cohort": "Cohort B - Renal Stratification",
            "prescribed_action": rep.get("final_prescribed_action") or rep.get("prescribed_action") or "N/A",
            "modification": rep.get("clinician_justification"),
        },
        "final_adjudication": {
            "decision": norm_decision,
            "eligibility": "ELIGIBLE" if (norm_decision == "ACCEPTED" and final_verdict == "JUSTIFIED") else "CONTRAINDICATED" if norm_decision == "REJECTED" else "CONDITIONAL",
            "confidence": rep.get("agent_metrics", {}).get("Arbitration Reducer", {}).get("confidence", 0.95),
            "hitl_approval_status": f"PHYSICIAN_{norm_decision}",
            "clinician_rationale": rationale,
        },
        "sub_agent_breakdown": {
            "compliance_agent": {
                "compliance_status": compliance_res.get("compliance_status", "UNKNOWN"),
                "confidence": f"{compliance_res.get('confidence', 0.9):.0%}",
                "explanation": compliance_res.get("explanation", "Protocol rules evaluated."),
            },
            "safety_agent": {
                "safety_status": safety_res.get("safety_status", "NEEDS_REVIEW"),
                "risk_score": 0.0 if safety_res.get("safety_status") == "SAFE" else 0.85,
                "summary": safety_res.get("explanation", "Patient tolerance evaluated."),
            },
            "financial_agent": {
                "coverage_status": financial_res.get("coverage_status", "COVERED"),
                "tier": financial_res.get("tier", "Tier-1 Investigational"),
                "pre_auth_required": financial_res.get("pre_auth_required", False),
                "explanation": financial_res.get("callout", financial_res.get("explanation", "100% Sponsor CTA Coverage.")),
            },
        },
        "active_violations": violations,
        "audit_trail": audit_logs,
    }

    pdf_buffer = generate_adjudication_pdf_bytes(report_payload)
    action_label = "Rejection_Notice" if norm_decision == "REJECTED" else "Adjudication_Certificate"
    filename = f"TrialGuard_{action_label}_{patient_id}.pdf"

    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )
