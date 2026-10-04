"""Temporary JSON input/output trace for inspecting the agent pipeline."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

TRACE_PATH = Path(__file__).parents[1] / "agent_io_trace.txt"
_TRACE_LOCK = Lock()


def record_trace(agent: str, direction: str, payload: object, **metadata: object) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "direction": direction,
        **metadata,
        "payload": payload,
    }
    block = json.dumps(entry, indent=2, default=str)
    with _TRACE_LOCK:
        with TRACE_PATH.open("a", encoding="utf-8") as trace_file:
            trace_file.write(block + "\n" + ("=" * 100) + "\n")
