import copy

from mcp_audit import GENESIS_HASH, canonical_json, compute_hash, seal_record, verify_chain


def build_chain(n=4):
    records = []
    prev = None
    for i in range(n):
        rec = seal_record(
            {
                "report_id": f"r{i}",
                "saved_at": f"2026-01-0{i + 1}T00:00:00+00:00",
                "final_decision": "ACCEPTED" if i % 2 == 0 else "REJECTED",
                "clinician_justification": f"rationale {i}",
                "safety_result": {"safety_status": "SAFE", "confidence": 0.9},
            },
            prev,
        )
        records.append(rec)
        prev = rec["hash"]
    return records


def test_canonical_json_ignores_key_order_and_whitespace():
    assert canonical_json({"b": 1, "a": [1, 2]}) == canonical_json({"a": [1, 2], "b": 1})
    assert canonical_json({"a": 1}) == '{"a":1}'


def test_first_record_uses_genesis_and_hash_formula():
    rec = seal_record({"x": 1})
    assert rec["prev_hash"] == GENESIS_HASH
    assert rec["hash"] == compute_hash(GENESIS_HASH, {"x": 1})
    assert len(rec["hash"]) == 64


def test_seal_ignores_existing_hash_fields():
    first = seal_record({"x": 1})
    again = seal_record(first, first["prev_hash"])
    assert again == first


def test_valid_chain_passes():
    result = verify_chain(build_chain())
    assert result.ok
    assert result.length == 4
    assert result.broken_index is None
    assert result.head_hash is not None


def test_empty_chain_is_valid():
    assert verify_chain([]).ok


def test_editing_any_field_of_an_earlier_record_fails_at_that_record():
    for field, new_value in [
        ("final_decision", "MODIFIED"),
        ("clinician_justification", "changed"),
        ("saved_at", "2030-01-01T00:00:00+00:00"),
    ]:
        records = build_chain()
        records[1][field] = new_value
        result = verify_chain(records)
        assert not result.ok
        assert result.broken_index == 1, field


def test_editing_a_nested_field_fails():
    records = build_chain()
    records[0]["safety_result"]["confidence"] = 0.1
    result = verify_chain(records)
    assert not result.ok
    assert result.broken_index == 0


def test_adding_a_field_fails():
    records = build_chain()
    records[2]["extra"] = "x"
    assert verify_chain(records).broken_index == 2


def test_order_matters():
    records = build_chain()
    swapped = copy.deepcopy(records)
    swapped[1], swapped[2] = swapped[2], swapped[1]
    result = verify_chain(swapped)
    assert not result.ok
    assert result.broken_index == 1


def test_removing_a_middle_record_fails():
    records = build_chain()
    del records[1]
    result = verify_chain(records)
    assert not result.ok
    assert result.broken_index == 1


def test_recomputed_hash_with_stale_link_still_fails():
    # An attacker edits record 1 and recomputes its own hash, but record 2 still points at the old one.
    records = build_chain()
    edited = {k: v for k, v in records[1].items() if k not in ("hash", "prev_hash")}
    edited["final_decision"] = "MODIFIED"
    records[1] = seal_record(edited, records[0]["hash"])
    result = verify_chain(records)
    assert not result.ok
    assert result.broken_index == 2


def test_truncating_the_tail_is_not_detected():
    # Documented limitation: nothing outside the chain remembers the head hash.
    assert verify_chain(build_chain()[:-1]).ok


def test_legacy_unsealed_prefix_is_skipped():
    legacy = [{"report_id": "old1"}, {"report_id": "old2"}]
    result = verify_chain(legacy + build_chain(2))
    assert result.ok
    assert result.unchained == 2


def test_unsealed_record_after_chain_start_fails():
    records = build_chain(3)
    records.append({"report_id": "sneaky"})
    result = verify_chain(records)
    assert not result.ok
    assert result.broken_index == 3
