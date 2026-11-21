import json
import sys
from pathlib import Path

# Add package paths to sys.path so imports resolve cleanly from root
ROOT_DIR = Path(__file__).resolve().parent
for p in [
    ROOT_DIR,
    ROOT_DIR / "apps" / "orchestrator",
    ROOT_DIR / "packages" / "mcp-ehr" / "src" / "mcp_ehr",
    ROOT_DIR / "packages" / "shared-schemas",
]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

try:
    from gateway import prepare_trial_state_from_ui
    from graph import app_graph
except ImportError:
    from apps.orchestrator.gateway import prepare_trial_state_from_ui
    from apps.orchestrator.graph import app_graph

JSON_PATH = ROOT_DIR / "packages" / "mcp-ehr" / "src" / "mcp_ehr" / "seeded_patient_ids.json"
DEFAULT_TRIAL = "NCT02415400"


def load_seeded_patients():
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"Cannot find seeded patient file at {JSON_PATH}")
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    patients = load_seeded_patients()
    print(f"\nEvaluating {len(patients)} seeded patients against {DEFAULT_TRIAL}...\n")
    print(f"{'PID':<6} | {'Patient Name':<22} | {'Verdict':<10} | {'Confidence':<10} | {'HITL?':<8} | {'Violations'}")
    print("-" * 75)

    for pid, profile in patients.items():
        name = profile.get("name", "Unknown") if isinstance(profile, dict) else "Unknown"

        # 1. Ingest patient data and initialize TrialState
        initial_state = prepare_trial_state_from_ui(
            trial_id=DEFAULT_TRIAL,
            raw_patient_id=pid,
            proposed_action="Standard Protocol Review",
        )

        # 2. Invoke the compiled LangGraph workflow
        result = app_graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": f"audit-{pid}"}},
        )

        # 3. Extract the verdict, confidence, and HITL status
        verdict = (
            result.get("final_decision")
            or result.get("decision")
            or result.get("eligibility")
            or "UNKNOWN"
        )
        confidence = result.get("confidence")
        conf_str = f"{float(confidence):.2f}" if confidence is not None else "N/A"

        requires_hitl = bool(result.get("requires_hitl") or result.get("needs_human_review"))
        hitl_display = "⚠️ YES" if requires_hitl else "NO"

        violations_list = result.get("violations") or []
        violation_count = len(violations_list)

        print(f"{pid:<6} | {name:<22} | {verdict:<10} | {conf_str:<10} | {hitl_display:<8} | {violation_count}")


if __name__ == "__main__":
    main()