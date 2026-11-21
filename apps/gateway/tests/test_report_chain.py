import pytest
from mcp_audit import verify_chain

from services import supabase_reports


@pytest.fixture
def local_store(tmp_path, monkeypatch):
    monkeypatch.setattr(supabase_reports, "LOCAL_STORE_PATH", tmp_path / "reports.json")
    monkeypatch.setattr(supabase_reports, "_IN_MEMORY_REPORTS", {})
    monkeypatch.setattr(supabase_reports, "_config", lambda: (None, None))
    return tmp_path / "reports.json"


def report(decision):
    return {"final_decision": decision, "clinician_justification": f"because {decision}"}


def test_reports_are_chained_per_patient(local_store):
    first = supabase_reports.append_final_report("P001", report("ACCEPTED"))
    second = supabase_reports.append_final_report("P001", report("REJECTED"))
    other = supabase_reports.append_final_report("P002", report("ACCEPTED"))

    assert second["prev_hash"] == first["hash"]
    assert other["prev_hash"] == first["prev_hash"]  # genesis: separate chain per patient
    assert supabase_reports.verify_patient_chain("P001")["ok"]
    assert supabase_reports.verify_patient_chain("P001")["length"] == 2


def test_tampering_with_the_local_store_is_detected(local_store):
    supabase_reports.append_final_report("P001", report("ACCEPTED"))
    supabase_reports.append_final_report("P001", report("REJECTED"))

    supabase_reports._IN_MEMORY_REPORTS["P001"][0]["final_decision"] = "REJECTED"

    result = supabase_reports.verify_patient_chain("P001")
    assert not result["ok"]
    assert result["broken_index"] == 0


def test_chain_survives_a_reload_from_disk(local_store, monkeypatch):
    supabase_reports.append_final_report("P001", report("ACCEPTED"))
    monkeypatch.setattr(supabase_reports, "_IN_MEMORY_REPORTS", {})
    supabase_reports.append_final_report("P001", report("REJECTED"))

    assert verify_chain(supabase_reports.get_final_reports("P001")).ok


def test_legacy_reports_without_hashes_do_not_break_new_chain(local_store):
    supabase_reports._save_local_report("P001", {"report_id": "legacy", "final_decision": "ACCEPTED"})
    new = supabase_reports.append_final_report("P001", report("REJECTED"))

    assert new["prev_hash"] == "0" * 64
    result = supabase_reports.verify_patient_chain("P001")
    assert result["ok"]
    assert result["unchained"] == 1
