"""
FHIR/EHR MCP server, built with fastmcp.

Exposes tools backed by live fetches against the public HAPI FHIR R4 
test server, Supabase, and synthetic fixtures (patients_expanded.json).
Adheres strictly to the updated PatientData schema contract used across the orchestrator.

Run this server:
    python server.py
    # or
    fastmcp run server.py
"""

import copy
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import find_dotenv, load_dotenv
from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Dynamic Path Resolution & Environment Loading
# ---------------------------------------------------------------------------
_pkg_dir = Path(__file__).resolve().parent

# Traverse upward to reliably resolve repository root
_repo_root = _pkg_dir
for parent in [_pkg_dir] + list(_pkg_dir.parents):
    if (parent / ".env").exists() or (parent / "packages").exists() or (parent / ".git").exists():
        _repo_root = parent
        break

load_dotenv(find_dotenv(usecwd=True))
load_dotenv(_repo_root / ".env")

if str(_pkg_dir) not in sys.path:
    sys.path.insert(0, str(_pkg_dir))

try:
    from fhir_client import (
        find_nearest_patients as _find_nearest_patients,
        get_patient as _get_patient,
        list_patients_for_ui as _list_patients_for_ui,
    )
except ImportError:
    from .fhir_client import (
        find_nearest_patients as _find_nearest_patients,
        get_patient as _get_patient,
        list_patients_for_ui as _list_patients_for_ui,
    )

mcp = FastMCP(
    name="ehr-server",
    description="FHIR R4 EHR retrieval server for clinical trial adjudication pipeline.",
)


def _conform_patient_schema(raw_record: Dict[str, Any], root_envelope: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Ensures fetched clinical record conforms strictly to the updated PatientData contract."""
    record = copy.deepcopy(raw_record)
    envelope = root_envelope or {}

    # Hydrate top-level metadata from root envelope if missing inside patient dict
    if not record.get("trial_id"):
        record["trial_id"] = (
            envelope.get("assigned_demo_trial_id") 
            or envelope.get("trial_id") 
            or record.get("assigned_demo_trial_id")
        )
    if not record.get("cohort"):
        record["cohort"] = envelope.get("cohort")
    if not record.get("name") and envelope.get("name"):
        record["name"] = envelope.get("name")
    if not record.get("fhir_id") and envelope.get("fhir_id"):
        record["fhir_id"] = str(envelope.get("fhir_id"))

    # Ensure nested sub-dictionaries exist
    record.setdefault("lab_results", {})
    record.setdefault("vital_signs", {})
    record.setdefault("cardiac_function", {})
    record.setdefault("protocol_facts", {})

    # Ensure list attributes exist
    record.setdefault("diagnoses", [])
    record.setdefault("medications", [])
    record.setdefault("allergies", [])
    record.setdefault("medical_history", [])
    record.setdefault("current_symptoms", [])

    # Ensure optional clinical flags exist per PatientData schema
    record.setdefault("dob", record.get("birth_date"))
    record.setdefault("cohort", "Cohort A - Standard Protocol")
    record.setdefault("internal_id", record.get("patient_id"))
    record.setdefault("fhir_id", None)
    record.setdefault("name", f"Patient {record.get('patient_id', 'Unknown')}")
    record.setdefault("weight", None)
    record.setdefault("medical_history_narrative", None)
    record.setdefault("pregnancy_test_result", "negative")
    record.setdefault("consent_capacity", True)
    record.setdefault("ecog_status", None)
    record.setdefault("last_systemic_therapy_date", None)

    # Standardize sex representation (lowercase "female" / "male" conforming to trial rules)
    raw_sex = str(record.get("sex") or "").strip().lower()
    if raw_sex in ["female", "f"]:
        record["sex"] = "female"
    elif raw_sex in ["male", "m"]:
        record["sex"] = "male"
    else:
        record["sex"] = "unknown"

    # Standardize protocol_facts defaults
    pf = record["protocol_facts"]
    pf.setdefault("oral_anticoagulation_required", None)
    pf.setdefault("acs_pathway", None)
    pf.setdefault("days_since_acute_coronary_syndrome", None)
    pf.setdefault("pci_pathway", None)
    pf.setdefault("days_since_PCI", None)
    pf.setdefault("planned_p2y12_duration", None)
    pf.setdefault("history_of_intracranial_hemorrhage", False)
    pf.setdefault("ongoing_bleeding", False)
    pf.setdefault("known_coagulopathy", False)
    pf.setdefault("cabg_for_index_acs", False)
    pf.setdefault("other_condition_requiring_chronic_anticoagulation", False)
    pf.setdefault("drug_contraindication", [])
    pf.setdefault("pregnant", False)
    pf.setdefault("breastfeeding", False)
    pf.setdefault("woman_of_childbearing_potential", False)
    pf.setdefault("pregnancy_test_negative", True)

    return record


@mcp.tool()
def get_patient(patient_identifier: str) -> Dict[str, Any]:
    """
    Fetch a patient's clinical record by numeric FHIR ID (e.g., '138563043'),
    internal alias (e.g., 'P001', 'PT-4471-0293'), or full name.

    Queries FHIR R4 test servers with fallback to Supabase or local fixtures.
    Returns structured data matching the PatientData schema.
    """
    clean_id = patient_identifier.strip()
    if not clean_id:
        raise ValueError("Patient identifier must not be empty.")

    try:
        # If user passed a full name instead of an identifier, resolve to ID first
        if not clean_id.upper().startswith(("P0", "PT-")) and not clean_id.isdigit():
            candidates = _list_patients_for_ui(query=clean_id)
            if candidates:
                clean_id = str(
                    candidates[0].get("patient_id")
                    or candidates[0].get("internal_id")
                    or candidates[0].get("fhir_id")
                )

        record = _get_patient(clean_id)
        if not record:
            raise ValueError(f"Patient record '{patient_identifier}' not found.")

        # Unpack patient sub-dictionary if wrapped in root envelope, but preserve outer metadata
        if "patient" in record and isinstance(record["patient"], dict):
            return _conform_patient_schema(record["patient"], root_envelope=record)
        return _conform_patient_schema(record)

    except Exception as e:
        raise ValueError(f"Failed to fetch patient record for '{patient_identifier}': {str(e)}") from e


@mcp.tool()
def search_patients(query: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search and auto-complete patient records by exact ID, partial name, cohort, or diagnosis.
    
    Returns a lightweight summary list containing:
    - patient_id / internal_id
    - fhir_id
    - name
    - dob
    - cohort
    - display_label
    - age, sex, and primary diagnoses
    """
    try:
        results = _list_patients_for_ui(query=query.strip() if query else None)
        return results[:limit]
    except Exception as e:
        raise RuntimeError(f"Patient search failed for query '{query}': {str(e)}") from e


@mcp.tool()
def find_nearest_patients(patient_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Finds clinically similar cohort candidates based on lab profile, age, and diagnoses.
    """
    clean_id = patient_id.strip()
    if not clean_id:
        raise ValueError("Patient ID must not be empty.")
    try:
        return _find_nearest_patients(clean_id, limit=limit)
    except Exception as e:
        raise RuntimeError(f"Similarity search failed for patient '{clean_id}': {str(e)}") from e


@mcp.resource("ehr://patients/summary")
def get_cohort_summary() -> str:
    """Provides a summarized markdown directory of all available trial test patients."""
    try:
        patients = _list_patients_for_ui()
        lines = ["# EHR Available Patient Cohort", ""]
        for p in patients:
            pid = p.get("patient_id") or p.get("internal_id")
            name = p.get("name", "Unknown")
            fhir_id = p.get("fhir_id", "N/A")
            age = p.get("age", "N/A")
            sex = p.get("sex", "N/A")
            cohort = p.get("cohort") or "Unassigned Cohort"
            diags = ", ".join(p.get("diagnoses", [])) or "None listed"

            lines.append(
                f"- **{name}** (`{pid}` / FHIR `#{fhir_id}`) "
                f"— {sex}, Age: {age} | Cohort: {cohort} | Diags: {diags}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Unable to generate cohort summary: {str(e)}"


if __name__ == "__main__":
    mcp.run()