"""Internal A2A-compatible JSON-RPC adapter for specialist agents."""

from __future__ import annotations

import json
import os
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services import compliance_agent, safety_agent, financial_agent
from services.io_trace import record_trace
from services.llm_client import call_llm, parse_json_response

router = APIRouter()


class AgentCapabilities(BaseModel):
    streaming: bool = False
    pushNotifications: bool = False


class AgentSkill(BaseModel):
    id: str
    name: str
    description: str
    tags: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    inputModes: list[str] = Field(default_factory=lambda: ["text/plain"])
    outputModes: list[str] = Field(default_factory=lambda: ["application/json"])


class AgentInterface(BaseModel):
    url: str
    protocolBinding: Literal["JSONRPC"] = "JSONRPC"
    protocolVersion: str = "1.0"


class AgentCard(BaseModel):
    name: str
    description: str
    version: str
    defaultInputModes: list[str]
    defaultOutputModes: list[str]
    capabilities: AgentCapabilities
    supportedInterfaces: list[AgentInterface]
    skills: list[AgentSkill]


A2A_URL = os.getenv("A2A_URL", "http://localhost:8000/a2a")

agent_card = AgentCard(
    name="TrialGuard Unified Agent Gateway",
    description="Routes TrialGuard protocol compliance, patient safety, financial coverage, and arbitration tasks.",
    version="1.0.0",
    defaultInputModes=["text/plain"],
    defaultOutputModes=["application/json"],
    capabilities=AgentCapabilities(streaming=False, pushNotifications=False),
    supportedInterfaces=[AgentInterface(url=A2A_URL)],
    skills=[
        AgentSkill(
            id="trial-compliance",
            name="Clinical Trial Compliance Evaluation",
            description="Checks a proposed action against supplied clinical trial protocol evidence.",
            tags=["clinical-trial", "compliance"],
        ),
        AgentSkill(
            id="patient-safety",
            name="Patient Safety Evaluation",
            description="Evaluates patient-specific safety using the supplied patient data and action.",
            tags=["patient", "safety", "toxicity"],
        ),
        AgentSkill(
            id="financial-risk",
            name="Financial & Coverage Risk Evaluation",
            description="Evaluates clinical trial research billing, insurance coverage, and prior authorization.",
            tags=["financial", "billing", "coverage"],
        ),
        AgentSkill(
            id="summary-synthesis",
            name="Review Summary Synthesis",
            description="Arbitrates specialist results into a final human-review verdict.",
            tags=["summary", "arbitration", "human-review"],
        ),
    ],
)

TASK_TO_SKILL = {
    "compliance": "trial-compliance",
    "safety": "patient-safety",
    "financial": "financial-risk",
    "summary-synthesis": "summary-synthesis",
}


@router.get("/.well-known/agent-card.json")
async def get_agent_card() -> dict:
    return agent_card.model_dump(by_alias=True)


@router.get("/.well-known/agent.json")
async def get_agent_card_legacy() -> dict:
    return agent_card.model_dump(by_alias=True)


@router.get("/agent-card")
async def get_agent_card_compatibility() -> dict:
    return agent_card.model_dump(by_alias=True)


def route_task(payload: dict) -> dict:
    task = payload.get("agent-task")
    if task == "compliance":
        if {"patient_id", "patient_data"} & payload.keys():
            raise ValueError("Compliance payload cannot contain patient data")
        return compliance_agent.evaluate(
            payload["trial_id"], payload["recent_action"], payload["relevant_protocols"],
            payload.get("report_history", []), payload.get("modification", ""),
        )
    if task == "safety":
        if "relevant_protocols" in payload:
            raise ValueError("Safety payload cannot contain protocol chunks")
        return safety_agent.evaluate(
            payload["trial_id"], payload["patient_id"], payload["recent_action"],
            payload["patient_data"], payload.get("report_history", []), payload.get("modification", ""),
        )
    if task == "financial":
        return financial_agent.evaluate(
            payload.get("trial_id", "NCT02415400"),
            payload.get("patient_id"),
            payload.get("recent_action", {}),
            financial_context=payload.get("financial_context"),
            policies=payload.get("relevant_policies"),
            report_history=payload.get("report_history", []),
            modification=payload.get("modification", ""),
        )
    if task == "summary-synthesis":
        return synthesize(payload)
    raise ValueError(f"Unknown agent-task: {task}. Must be compliance, safety, financial, or summary-synthesis")


def synthesize(payload: dict) -> dict:
    compliance = payload.get("compliance_result", {})
    safety = payload.get("safety_result", {})
    financial = payload.get("financial_result", {})
    
    compliance_status = compliance.get("compliance_status", "UNKNOWN")
    safety_status = safety.get("safety_status", "NEEDS_REVIEW")
    coverage_status = financial.get("coverage_status", "COVERED")
    
    computed_verdict = (
        "NOT_JUSTIFIED" if compliance_status == "NON_COMPLIANT" or safety_status == "UNSAFE"
        else "JUSTIFIED" if compliance_status == "COMPLIANT" and safety_status == "SAFE" and coverage_status == "COVERED"
        else "NEEDS_REVIEW"
    )

    prompt = (
        "Return ONLY valid JSON with exactly final_verdict and summary. "
        "final_verdict must be JUSTIFIED, NOT_JUSTIFIED, or NEEDS_REVIEW. "
        "Use NOT_JUSTIFIED for a material violation or unsafe condition, "
        "NEEDS_REVIEW for uncertainty, and JUSTIFIED only when all support proceeding. "
        "Write 2-4 concise sentences for a doctor. Evaluate the current results:\n" +
        str({"compliance_result": compliance, "safety_result": safety, "financial_result": financial, "report_history": payload.get("report_history", [])})
    )
    
    try:
        result = parse_json_response(call_llm(prompt, max_tokens=400))
        summary = result.get("summary", "").strip()
        if not summary:
            summary = f"Multi-agent review verdict is {computed_verdict}. Compliance: {compliance_status}, Safety: {safety_status}, Coverage: {coverage_status}."
        return {
            "final_verdict": computed_verdict,
            "summary": summary,
        }
    except Exception:
        return {
            "final_verdict": computed_verdict,
            "summary": f"Adjudication completed with verdict {computed_verdict}. Protocol compliance evaluated as {compliance_status}, patient safety as {safety_status}, and research billing as {coverage_status}."
        }


@router.post("/a2a")
@router.post("/rpc")
async def a2a_jsonrpc(envelope: dict) -> dict:
    params = envelope.get("params", {})
    message = params.get("message", {})
    parts = message.get("parts", [])
    text = next((part.get("text") for part in parts if part.get("text")), None)
    if not text:
        raise ValueError("A2A message has no text part")
    agent_input = json.loads(text)
    agent_name = {
        "compliance": "Protocol Compliance Agent",
        "safety": "Safety & Toxicity Agent",
        "financial": "Financial Risk Agent",
        "summary-synthesis": "Arbitration Reducer",
    }.get(agent_input.get("agent-task"), agent_input.get("agent-task", "Unknown Agent"))
    skill_id = TASK_TO_SKILL.get(agent_input.get("agent-task"))
    if skill_id is None:
        raise ValueError(f"Unknown A2A task: {agent_input.get('agent-task')}")
    record_trace(agent_name, "input", agent_input, source="a2a")
    try:
        result = route_task(agent_input)
    except Exception as error:
        record_trace(agent_name, "error", {"type": type(error).__name__, "message": str(error)}, source="a2a")
        raise
    record_trace(agent_name, "output", result, source="a2a")
    return {
        "jsonrpc": "2.0",
        "id": envelope.get("id"),
        "result": {
            "skillId": skill_id,
            "artifacts": [{"parts": [{"text": json.dumps(result)}]}],
        },
    }
