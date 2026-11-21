"""
Append-only SHA-256 hash chain for audit records.

Each record is the event payload plus two fields:
  - prev_hash: the hash of the previous record (GENESIS_HASH for the first one)
  - hash:      sha256(prev_hash + canonical_json(event))

where `event` is the record without its `hash` and `prev_hash` fields. Changing
any field of an earlier record, or reordering records, breaks verification at
the first affected link.

What this does not do: it cannot detect records deleted from the *end* of a
chain, because nothing outside the chain remembers the latest hash. Anchoring
the head hash somewhere else would close that gap.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

HASH_FIELD = "hash"
PREV_HASH_FIELD = "prev_hash"

# Fixed value used as prev_hash for the first record of every chain.
GENESIS_HASH = "0" * 64


def canonical_json(obj: Any) -> str:
    """Deterministic JSON: sorted keys, no whitespace, UTF-8 characters kept."""
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _event_of(record: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k not in (HASH_FIELD, PREV_HASH_FIELD)}


def compute_hash(prev_hash: str, event: Mapping[str, Any]) -> str:
    payload = prev_hash + canonical_json(event)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def seal_record(event: Mapping[str, Any], prev_hash: str | None = None) -> dict[str, Any]:
    """Return `event` plus `prev_hash` and `hash`. Pass None for the first record."""
    prev = GENESIS_HASH if prev_hash is None else prev_hash
    clean = _event_of(event)
    return {**clean, PREV_HASH_FIELD: prev, HASH_FIELD: compute_hash(prev, clean)}


@dataclass(frozen=True)
class ChainVerification:
    ok: bool
    length: int
    # Index of the first record that fails verification, or None if the chain is valid.
    broken_index: int | None = None
    reason: str = ""
    # Leading records written before sealing existed (no hash). They are skipped.
    unchained: int = 0
    head_hash: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "length": self.length,
            "broken_index": self.broken_index,
            "reason": self.reason,
            "unchained": self.unchained,
            "head_hash": self.head_hash,
        }


def verify_chain(records: Sequence[Mapping[str, Any]]) -> ChainVerification:
    """
    Recompute the chain and report the first broken link.

    Records with no `hash` at the start of the sequence are legacy records from
    before sealing was introduced; they are counted in `unchained` and skipped.
    Any unsealed record after the chain has started is a failure.
    """
    start = 0
    while start < len(records) and HASH_FIELD not in records[start]:
        start += 1

    expected_prev = GENESIS_HASH
    for idx in range(start, len(records)):
        rec = records[idx]
        if HASH_FIELD not in rec or PREV_HASH_FIELD not in rec:
            return ChainVerification(False, len(records), idx, "record is missing hash/prev_hash", start)
        if rec[PREV_HASH_FIELD] != expected_prev:
            return ChainVerification(
                False, len(records), idx, "prev_hash does not match the previous record", start
            )
        recomputed = compute_hash(rec[PREV_HASH_FIELD], _event_of(rec))
        if recomputed != rec[HASH_FIELD]:
            return ChainVerification(False, len(records), idx, "record contents do not match its hash", start)
        expected_prev = rec[HASH_FIELD]

    head = expected_prev if start < len(records) else None
    return ChainVerification(True, len(records), None, "", start, head)
