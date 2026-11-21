import hashlib

from mcp_audit import GENESIS_HASH, canonical_json, compute_hash

from apps.orchestrator.nodes.audit import complete_audit_node


def test_final_audit_entry_is_sealed_and_commits_to_prior_logs():
    prior = [{"step": "multi_agent_evaluation", "status": "converged"}]
    state = {
        "patient_id": "P036",
        "trial_id": "NCT02415400",
        "final_decision": "REJECTED",
        "hitl_comments": "dose exceeds protocol cap",
        "audit_logs": prior,
    }

    entry = complete_audit_node(state)["audit_logs"][0]

    assert entry["prev_hash"] == GENESIS_HASH
    assert entry["prior_logs_sha256"] == hashlib.sha256(canonical_json(prior).encode()).hexdigest()
    event = {k: v for k, v in entry.items() if k not in ("hash", "prev_hash")}
    assert entry["hash"] == compute_hash(GENESIS_HASH, event)
