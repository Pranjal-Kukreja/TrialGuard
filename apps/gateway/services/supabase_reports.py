"""Server-side persistence for finalized adjudication reports."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import httpx

logger = logging.getLogger(__name__)

# Resilient local persistent storage fallback
GATEWAY_DIR = Path(__file__).resolve().parents[1]
LOCAL_STORE_PATH = GATEWAY_DIR / "data" / "adjudication_reports.json"
LOCAL_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
_IN_MEMORY_REPORTS: dict[str, list[dict]] = {}


class ReportPersistenceError(RuntimeError):
    pass


def _load_env_if_missing() -> None:
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        repo_env = GATEWAY_DIR.parent.parent / ".env"
        if repo_env.is_file():
            for line in repo_env.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("'\"")
                    if k in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY") and not os.getenv(k):
                        os.environ[k] = v


def _config() -> tuple[str | None, str | None]:
    _load_env_if_missing()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    return (url.rstrip("/") if url else None, key)


def _headers(key: str, prefer: str = "return=representation") -> dict[str, str]:
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": prefer,
    }


def _load_local_reports() -> dict[str, list[dict]]:
    global _IN_MEMORY_REPORTS
    if not _IN_MEMORY_REPORTS and LOCAL_STORE_PATH.is_file():
        try:
            _IN_MEMORY_REPORTS = json.loads(LOCAL_STORE_PATH.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("Failed to load local reports store: %s", exc)
            _IN_MEMORY_REPORTS = {}
    return _IN_MEMORY_REPORTS


def _save_local_report(patient_id: str, report: dict) -> None:
    store = _load_local_reports()
    clean_id = patient_id.strip()
    if clean_id not in store:
        store[clean_id] = []
    store[clean_id].append(report)
    try:
        LOCAL_STORE_PATH.write_text(json.dumps(store, indent=2), encoding="utf-8")
    except Exception as exc:
        logger.warning("Failed to write to local reports store: %s", exc)


def append_final_report(patient_id: str, report: dict) -> dict:
    finalized_report = {
        "report_id": str(uuid4()),
        "saved_at": datetime.now(timezone.utc).isoformat(),
        **report,
    }

    # 1. Always save locally first so the report is NEVER lost
    _save_local_report(patient_id, finalized_report)

    # 2. Attempt remote Supabase synchronization
    url, key = _config()
    if not url or not key:
        logger.info("Saved report for %s locally (Supabase credentials not configured)", patient_id)
        return finalized_report

    headers = _headers(key)
    base = f"{url}/rest/v1/patients"

    try:
        with httpx.Client(timeout=10) as client:
            # Primary strategy: Store in clinical_data JSONB (guaranteed to exist across tables)
            resp = client.get(
                base,
                params={"patient_id": f"eq.{patient_id}", "select": "patient_id,clinical_data"},
                headers=headers,
            )
            if resp.status_code == 200:
                rows = resp.json()
                if rows:
                    cdata = rows[0].get("clinical_data") or {}
                    existing = cdata.get("adjudication_reports") or []
                    if not isinstance(existing, list):
                        existing = []
                    cdata["adjudication_reports"] = [*existing, finalized_report]
                    patch_resp = client.patch(
                        base,
                        params={"patient_id": f"eq.{patient_id}"},
                        headers=headers,
                        json={"clinical_data": cdata},
                    )
                    if patch_resp.status_code in (200, 204):
                        logger.info("Report for %s synced to Supabase clinical_data", patient_id)
                        return finalized_report

            # Secondary strategy: Direct adjudication_reports column if migrated
            direct_resp = client.get(
                base,
                params={"patient_id": f"eq.{patient_id}", "select": "patient_id,adjudication_reports"},
                headers=headers,
            )
            if direct_resp.status_code == 200:
                rows = direct_resp.json()
                if rows:
                    existing = rows[0].get("adjudication_reports") or []
                    if not isinstance(existing, list):
                        existing = []
                    client.patch(
                        base,
                        params={"patient_id": f"eq.{patient_id}"},
                        headers=headers,
                        json={"adjudication_reports": [*existing, finalized_report]},
                    )
    except Exception as exc:
        logger.warning("Remote Supabase report sync encountered error (local copy preserved): %s", exc)

    return finalized_report


def get_final_reports(patient_id: str) -> list[dict]:
    # 1. Fetch from local store
    local_store = _load_local_reports()
    local_reports = local_store.get(patient_id.strip(), [])

    # 2. Attempt fetch from Supabase
    url, key = _config()
    remote_reports: list[dict] = []
    if url and key:
        headers = _headers(key, prefer="return=minimal")
        base = f"{url}/rest/v1/patients"
        try:
            with httpx.Client(timeout=8) as client:
                # Check clinical_data first
                resp = client.get(
                    base,
                    params={"patient_id": f"eq.{patient_id}", "select": "patient_id,clinical_data"},
                    headers=headers,
                )
                if resp.status_code == 200:
                    rows = resp.json()
                    if rows:
                        cdata = rows[0].get("clinical_data") or {}
                        remote_reports = cdata.get("adjudication_reports") or []
                elif resp.status_code != 200:
                    # Fallback to direct column
                    resp_direct = client.get(
                        base,
                        params={"patient_id": f"eq.{patient_id}", "select": "patient_id,adjudication_reports"},
                        headers=headers,
                    )
                    if resp_direct.status_code == 200:
                        rows = resp_direct.json()
                        if rows:
                            remote_reports = rows[0].get("adjudication_reports") or []
        except Exception as exc:
            logger.warning("Failed querying Supabase for reports: %s", exc)

    # 3. Merge and deduplicate by report_id
    seen_ids = set()
    combined: list[dict] = []
    for r in (*remote_reports, *local_reports):
        rid = r.get("report_id") or r.get("saved_at")
        if rid and rid not in seen_ids:
            seen_ids.add(rid)
            combined.append(r)
        elif not rid:
            combined.append(r)

    return combined
