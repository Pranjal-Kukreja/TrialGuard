import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Monorepo path resolution
ROOT_DIR = Path(__file__).resolve().parent
REPO_ROOT = ROOT_DIR if (ROOT_DIR / "apps").exists() else ROOT_DIR.parents[1]

PATHS = [
    REPO_ROOT,
    REPO_ROOT / "apps" / "orchestrator",
    REPO_ROOT / "apps" / "agent_master",
    REPO_ROOT / "packages" / "mcp-ehr" / "src" / "mcp_ehr",
    REPO_ROOT / "packages" / "mcp-ehr" / "src",
    REPO_ROOT / "packages" / "shared-schemas",
]

for p in PATHS:
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

try:
    from apps.orchestrator.gateway import prepare_trial_state_from_ui
    from apps.orchestrator.graph import app_graph
except ImportError:
    from gateway import prepare_trial_state_from_ui
    from graph import app_graph

JSON_PATH = REPO_ROOT / "packages" / "mcp-ehr" / "src" / "mcp_ehr" / "seeded_patient_ids.json"
DEFAULT_TRIAL = "NCT02415400"


def main():
    if not JSON_PATH.exists():
        print(f"Error: Could not find {JSON_PATH}")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        patients = json.load(f)

    print(f"\n==========================================================================")
    print(f"  TRIALGUARD BATCH ADJUDICATION AUDIT: {len(patients)} PROFILES ({DEFAULT_TRIAL})")
    print(f"==========================================================================\n")
    print(f"{'PID':<6} | {'Name':<22} | {'Verdict':<10} | {'Conf':<6} | {'HITL':<6} | {'Violations':<10}")
    print("-" * 72)

    for pid, profile in patients.items():
        name = profile.get("name", "Unknown") if isinstance(profile, dict) else "Unknown"

        try:
            initial_state = prepare_trial_state_from_ui(
                trial_id=DEFAULT_TRIAL,
                raw_patient_id=pid,
                proposed_action="Standard Protocol Review",
            )

            result = app_graph.invoke(
                initial_state,
                config={"configurable": {"thread_id": f"batch-{pid}"}},
            )

            verdict = (
                result.get("final_decision")
                or result.get("decision")
                or result.get("eligibility")
                or "UNKNOWN"
            )
            confidence = result.get("confidence")
            conf_str = f"{float(confidence):.2f}" if confidence is not None else "N/A"
            hitl = bool(result.get("requires_hitl") or result.get("needs_human_review"))
            violations = len(result.get("violations", []))

            print(f"{pid:<6} | {name:<22} | {verdict:<10} | {conf_str:<6} | {str(hitl):<6} | {violations:<10}")
        except Exception as exc:
            print(f"{pid:<6} | {name:<22} | ERROR      | N/A    | False  | {str(exc)[:20]}")


if __name__ == "__main__":
    main()