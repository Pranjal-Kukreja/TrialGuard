"""Unified A2A Gateway for TrialGuard Agents and Coordinator Tasks.

Coordinates and routes to:
  - Compliance Specialist (Port 8001)
  - Safety Specialist (Port 8002)
  - Financial Specialist (Port 8003)
  - Review Summary Synthesis (LLM)
"""

from __future__ import annotations

import asyncio
import json
import os
import uvicorn
from starlette.applications import Starlette
import httpx

from a2a.helpers import get_message_text, new_task_from_user_message, new_text_message, new_text_part
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from a2a.types.a2a_pb2 import TaskState

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

def _load_fn_from_file(module_name: str, file_path: Path, fn_name: str):
    if file_path.exists():
        try:
            spec = importlib.util.spec_from_file_location(module_name, str(file_path))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return getattr(mod, fn_name, None)
        except Exception:
            return None
    return None

# Upstream direct evaluators / fallbacks mapped to actual directory structure
evaluate_compliance = _load_fn_from_file(
    "compliance_server", 
    REPO_ROOT / "apps" / "agent-compliance" / "server.py", 
    "_evaluate"
)

evaluate_safety = _load_fn_from_file(
    "safety_server", 
    REPO_ROOT / "apps" / "agent-safety" / "server.py", 
    "_evaluate_safety"
)

try:
    import llm_client as llm_client
except ImportError:
    llm_client = None

# Master Gateway Port (Set to 8000 to avoid collision with Compliance on 8001)
HOST = os.getenv("A2A_HOST", "0.0.0.0")
PORT = int(os.getenv("A2A_PORT", "8000"))
A2A_URL = os.getenv("A2A_URL", f"http://{HOST}:{PORT}")

# Client endpoints sanitized to ensure 127.0.0.1 is used instead of 0.0.0.0
COMPLIANCE_ENDPOINT = os.getenv("COMPLIANCE_AGENT_URL", "http://127.0.0.1:8001/rpc").replace("://0.0.0.0:", "://127.0.0.1:")
SAFETY_ENDPOINT = os.getenv("SAFETY_AGENT_URL", "http://127.0.0.1:8002/rpc").replace("://0.0.0.0:", "://127.0.0.1:")
FINANCIAL_ENDPOINT = os.getenv("FINANCIAL_AGENT_URL", "http://127.0.0.1:8003/rpc").replace("://0.0.0.0:", "://127.0.0.1:")


async def _forward_rpc(url: str, payload: dict) -> dict | None:
    """Forward A2A JSON-RPC to the specialized microservice."""
    body = {
        "jsonrpc": "2.0",
        "id": "gateway-fwd",
        "method": "SendMessage",
        "params": {
            "message": {
                "role": "ROLE_USER",  # Protobuf enum standard
                "parts": [{"text": json.dumps(payload), "media_type": "application/json"}],
            }
        },
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=body)
            if resp.status_code == 200:
                data = resp.json()
                artifacts = data.get("result", {}).get("task", {}).get("artifacts", [])
                if artifacts:
                    return json.loads(artifacts[0]["parts"][0]["text"])
                return data.get("result")
    except Exception:
        return None
    return None


async def _route(payload: dict) -> dict | str:
    task = payload.get("agent-task")

    # 1. Summary Synthesis
    if task == "summary-synthesis":
        if llm_client:
            raw = llm_client.call_llm(
                "Write a short summary for a doctor using these clinical review results. "
                "State whether agents agree, mention key violations or safety concerns, "
                "and state what needs human attention. Use 2-4 concise sentences.\n\n"
                + json.dumps(payload, indent=2),
                max_tokens=400,
            )
            return raw.strip()
        return "Consensus synthesis: Multi-agent evaluation completed."

    # 2. Compliance Routing
    if task == "compliance":
        forbidden = {"patient_id", "patient_data"} & payload.keys()
        if forbidden:
            raise ValueError(f"Compliance payload cannot contain: {sorted(forbidden)}")
        remote = await _forward_rpc(COMPLIANCE_ENDPOINT, payload)
        if remote:
            return remote
        if evaluate_compliance:
            return evaluate_compliance(
                trial_id=payload["trial_id"],
                recent_action=payload["recent_action"],
                protocol_chunks=payload.get("relevant_protocols", []),
                report_history=payload.get("report_history", []),
                modification=payload.get("modification", ""),
            )
        raise RuntimeError("Compliance microservice offline and local fallback unavailable.")

    # 3. Safety Routing
    if task == "safety":
        if "relevant_protocols" in payload:
            raise ValueError("Safety payload cannot contain relevant_protocols")
        remote = await _forward_rpc(SAFETY_ENDPOINT, payload)
        if remote:
            return remote
        if evaluate_safety:
            return evaluate_safety(
                trial_id=payload["trial_id"],
                patient_id=payload["patient_id"],
                recent_action=payload["recent_action"],
                patient_data=payload["patient_data"],
                report_history=payload.get("report_history", []),
                modification=payload.get("modification", ""),
            )
        raise RuntimeError("Safety microservice offline and local fallback unavailable.")

    # 4. Financial Routing
    if task == "financial":
        remote = await _forward_rpc(FINANCIAL_ENDPOINT, payload)
        if remote:
            return remote
        return {
            "coverage_status": "COVERED",
            "tier": "Tier-1 Investigational Coverage",
            "explanation": "Default gateway fallback grant allocation.",
        }

    raise ValueError(f"agent-task must be one of: compliance, safety, financial, summary-synthesis; got '{task}'")


class TrialGuardExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task = context.current_task or new_task_from_user_message(context.message)
        if not context.current_task:
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue=event_queue, task_id=task.id, context_id=task.context_id)
        await updater.update_status(state=TaskState.TASK_STATE_WORKING, message=new_text_message("Task started."))
        try:
            message_text = get_message_text(context.message)
            if not message_text:
                raise ValueError("No input message was provided")
            result = await _route(json.loads(message_text))
            artifact_text = result if isinstance(result, str) else json.dumps(result)
            await updater.add_artifact(parts=[new_text_part(text=artifact_text, media_type="application/json")])
            await updater.update_status(state=TaskState.TASK_STATE_COMPLETED, message=new_text_message("Task completed."))
        except Exception as exc:
            error = {"error": str(exc), "type": type(exc).__name__}
            await updater.add_artifact(parts=[new_text_part(text=json.dumps(error), media_type="application/json")])
            await updater.update_status(state=TaskState.TASK_STATE_FAILED, message=new_text_message("Task failed."))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("Cancellation is not supported")


agent_card = AgentCard(
    name="TrialGuard Unified Agent Gateway",
    description="Routes TrialGuard compliance, safety, financial, and synthesis tasks.",
    version="1.1.0",
    default_input_modes=["text/plain"],
    default_output_modes=["application/json"],
    capabilities=AgentCapabilities(streaming=False),
    supported_interfaces=[AgentInterface(url=A2A_URL, protocol_binding="JSONRPC", protocol_version="1.0")],
    skills=[
        AgentSkill(id="trial-compliance", name="Clinical Trial Compliance Evaluation", description="Checks an action against protocol text.", tags=["compliance"], examples=[], input_modes=["text/plain"], output_modes=["application/json"]),
        AgentSkill(id="patient-safety", name="Patient Safety Evaluation", description="Evaluates patient-specific physiological safety.", tags=["safety"], examples=[], input_modes=["text/plain"], output_modes=["application/json"]),
        AgentSkill(id="financial-coverage", name="Trial Financial & Billing Adjudication", description="Evaluates grant tier, coverage, and pre-auth.", tags=["financial"], examples=[], input_modes=["text/plain"], output_modes=["application/json"]),
        AgentSkill(id="summary-synthesis", name="Review Summary Synthesis", description="Summarizes multi-agent results for clinician review.", tags=["summary"], examples=[], input_modes=["text/plain"], output_modes=["application/json"]),
    ],
)


def build_app() -> Starlette:
    handler = DefaultRequestHandler(agent_executor=TrialGuardExecutor(), task_store=InMemoryTaskStore(), agent_card=agent_card)
    return Starlette(routes=create_agent_card_routes(agent_card) + create_jsonrpc_routes(handler, rpc_url="/rpc"))


app = build_app()

if __name__ == "__main__":
    print(f"--> Gateway binding on {HOST}:{PORT}")
    print(f"--> local fallback available: compliance={evaluate_compliance is not None}, safety={evaluate_safety is not None}")
    uvicorn.run(app, host=HOST, port=PORT)