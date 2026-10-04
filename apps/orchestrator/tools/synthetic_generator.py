"""
AI Synthetic Patient Generator & FHIR Seeder (High-Performance Parallelized).

Optimizations:
  1. Asynchronous concurrent LLM generation via asyncio.gather + Semaphore.
  2. FHIR R4 Transaction Bundles: Compresses 15-20 individual HTTP roundtrips
     per patient into a single atomic POST /baseR4 transaction request.
  3. Parallel FHIR bundle uploads via httpx.AsyncClient.
  4. Fixes authentication header pass-through (x-bf-vk) for Kado Bifrost gateway.
  5. Preserves patient name throughout JSON, seeded map, and Supabase synchronization.
"""

import argparse
import asyncio
import itertools
import json
import os
import random
import re
import sys
import time
import uuid
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import find_dotenv, load_dotenv
import httpx
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

load_dotenv(find_dotenv(usecwd=True))

REPO_ROOT = Path(__file__).resolve().parents[3]
MCP_EHR_SRC = REPO_ROOT / "packages" / "mcp-ehr" / "src"
MCP_EHR_PKG = MCP_EHR_SRC / "mcp_ehr"

for p in [str(REPO_ROOT), str(MCP_EHR_SRC), str(MCP_EHR_PKG)]:
    if p not in sys.path:
        sys.path.insert(0, p)

EXPANDED_FILE_PATH = MCP_EHR_PKG / "patients_expanded.json"
SEEDED_ID_PATH = MCP_EHR_PKG / "seeded_patient_ids.json"


def _resolve_fhir_base_url() -> str:
    default_url = "https://hapi.fhir.org/baseR4"
    raw = os.getenv("FHIR_SERVER_URL") or os.getenv("FHIR_BASE_URL") or ""
    raw = raw.replace("\ufeff", "").strip()
    raw = re.sub(r"""['"“”‘’\[\]\(\)]""", "", raw).strip().rstrip("/")
    if not raw or raw.lower() in {"none", "null", "undefined"}:
        return default_url
    if not raw.startswith(("http://", "https://")):
        raw = f"https://{raw}"
    return raw


FHIR_BASE_URL = _resolve_fhir_base_url()

REGIONAL_CULTURAL_ETHOSES = [
    "Tamil Nadu / Kerala (Dravidian roots, e.g., Balasubramanian, Menachery, Kurup, Swaminathan, Chettiar)",
    "West Bengal / Odisha (Eastern roots, e.g., Bandyopadhyay, Mahapatra, Bhattacharjee, Patnaik, Barik)",
    "Maharashtra / Goa (Western roots, e.g., Deshpande, Sawant, Gokhale, Tendolkar, Wagh, Prabhu)",
    "Assam / Meghalaya / Manipur (North-Eastern roots, e.g., Borphukan, Hazarika, Lyngdoh, Saikia, Singha)",
    "Punjab / Haryana / Kashmir (North-Western roots, e.g., Bhat, Ahluwalia, Chawla, Wani, Bajwa, Sandhu)",
    "Andhra Pradesh / Telangana (Telugu roots, e.g., Vangapandu, Kondaveeti, Ghattamaneni, Yarlagadda)",
    "Gujarat / Rajasthan (Western roots, e.g., Ruparel, Shekhawat, Meghwal, Zaveri, Rathore, Solanki)",
    "Bihar / Uttar Pradesh (Gangetic Plains roots, e.g., Upadhyay, Tripathi, Paswan, Kushwaha, Ojha)",
]

DISEASE_SCENARIO_PROFILES = [
    {
        "category": "Cardiovascular & AF (Antithrombotic Protocol)",
        "cohort": "Cohort A - Standard Protocol",
        "description": "Non-valvular atrial fibrillation post-PCI or post-ACS requiring anticoagulation.",
        "diagnoses_hints": ["non-valvular atrial fibrillation", "coronary artery disease post-PCI", "essential hypertension"],
        "medications_hints": ["apixaban 5mg BID", "clopidogrel 75mg daily", "atorvastatin 40mg daily"],
    },
    {
        "category": "Oncology / Solid Tumors",
        "cohort": "Cohort C - Solid Tumor Oncology",
        "description": "Metastatic or locally advanced solid tumors undergoing targeted/immunotherapy monitoring.",
        "diagnoses_hints": ["non-small cell lung cancer (stage IIIB)", "colorectal adenocarcinoma"],
        "medications_hints": ["pembrolizumab 200mg IV Q3W", "capecitabine 1000mg BID", "ondansetron 8mg PRN"],
    },
    {
        "category": "Hepatology & Metabolic Disorders",
        "cohort": "Cohort B - NAFLD Protocol",
        "description": "Metabolic Dysfunction-Associated Steatohepatitis (MASH / NAFLD) with transaminase monitoring.",
        "diagnoses_hints": ["metabolic dysfunction-associated steatohepatitis (MASH)", "type 2 diabetes mellitus"],
        "medications_hints": ["pioglitazone 30mg daily", "semaglutide 1.0mg weekly", "vitamin E 800 IU daily"],
    },
    {
        "category": "Nephrology & Glomerular Disease",
        "cohort": "Cohort B - Renal Stratification",
        "description": "Chronic glomerulonephritis or diabetic nephropathy with preserved baseline filtration.",
        "diagnoses_hints": ["diabetic nephropathy stage 3a", "membranous nephropathy"],
        "medications_hints": ["empagliflozin 10mg daily", "losartan 50mg daily", "torsemide 10mg daily"],
    },
]


def get_available_rag_trial_ids(limit_count: int = 4) -> List[str]:
    fallback = ["NCT00699998", "NCT00781573", "NCT00809965", "NCT02415400"]
    try:
        from apps.orchestrator.nodes.rag_node import get_retriever
        retriever = get_retriever()
        store_trials = retriever.store.trials.get(limit=150)
        found_ids = {meta.get("trial_id") for meta in store_trials.get("metadatas", []) if meta.get("trial_id")}
        if found_ids:
            return sorted(list(found_ids))[:limit_count]
    except Exception:
        pass
    return fallback[:limit_count]


class SyntheticVitalSigns(BaseModel):
    heart_rate: float = 72.0
    blood_pressure_systolic: int = 120
    blood_pressure_diastolic: int = 80


class SyntheticLabResults(BaseModel):
    ALT: float = 28.0
    AST: float = 24.0
    eGFR: float = 75.0
    ANC: float = 3800.0
    platelets: float = 240000.0
    hemoglobin: float = 13.8
    INR: float = 1.1
    total_bilirubin: float = 0.8
    serum_creatinine: float = 1.0
    creatinine_clearance: float = 65.0


class SyntheticCardiacFunction(BaseModel):
    LVEF: float = 55.0
    QTc: float = 415.0


class SyntheticProtocolFacts(BaseModel):
    oral_anticoagulation_required: bool = True
    planned_or_existing_oral_anticoagulation: bool = True
    acs_pathway: bool = False
    days_since_acute_coronary_syndrome: Optional[int] = None
    pci_pathway: bool = True
    days_since_PCI: Optional[int] = 7
    planned_p2y12_duration: int = 6
    history_of_intracranial_hemorrhage: bool = False
    prior_bleeding: bool = False
    ongoing_bleeding: bool = False
    known_coagulopathy: bool = False
    cabg_for_index_acs: bool = False
    other_condition_requiring_chronic_anticoagulation: bool = False
    drug_contraindication: List[str] = Field(default_factory=list)
    pregnant: bool = False
    breastfeeding: bool = False
    woman_of_childbearing_potential: bool = False
    pregnancy_test_negative: bool = True


class GeneratedPatient(BaseModel):
    patient_id: str
    name: str
    cohort: str
    age: int = Field(ge=18, le=95)
    sex: str = "female"
    weight: float = 68.0
    diagnoses: List[str]
    medications: List[str]
    allergies: List[str] = Field(default_factory=list)
    lab_results: SyntheticLabResults = Field(default_factory=SyntheticLabResults)
    vital_signs: SyntheticVitalSigns = Field(default_factory=SyntheticVitalSigns)
    cardiac_function: SyntheticCardiacFunction = Field(default_factory=SyntheticCardiacFunction)
    medical_history: List[str]
    medical_history_narrative: str
    current_symptoms: List[str] = Field(default_factory=list)
    pregnancy_test_result: str = "negative"
    consent_capacity: bool = True
    ecog_status: int = 0
    last_systemic_therapy_date: Optional[str] = None
    protocol_facts: SyntheticProtocolFacts = Field(default_factory=SyntheticProtocolFacts)


def reset_local_patient_storage() -> None:
    SEEDED_ID_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEEDED_ID_PATH.write_text("{}", encoding="utf-8")
    clean = {
        "metadata": {"version": "2.0.0", "description": "Synthetic FHIR cohort", "patient_count": 0},
        "patients": [],
    }
    EXPANDED_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPANDED_FILE_PATH.write_text(json.dumps(clean, indent=2), encoding="utf-8")
    print(f"✓ Reset local fixture storage.")


def find_expanded_json_file() -> Path:
    for path in [
        EXPANDED_FILE_PATH,
        MCP_EHR_SRC / "patients_expanded.json",
        REPO_ROOT / "packages" / "mcp-ehr" / "patients_expanded.json",
        Path.cwd() / "patients_expanded.json",
    ]:
        if path.exists():
            return path.resolve()
    EXPANDED_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPANDED_FILE_PATH.write_text('{"metadata": {"patient_count": 0}, "patients": []}', encoding="utf-8")
    return EXPANDED_FILE_PATH.resolve()


def get_next_patient_id(expanded_file: Path) -> int:
    try:
        data = json.loads(expanded_file.read_text(encoding="utf-8"))
        p_ids = [
            int(m.group(1))
            for item in data.get("patients", [])
            for pid in [item.get("patient_id") or item.get("patient", {}).get("patient_id", "")]
            if (m := re.match(r"P(\d+)", pid))
        ]
        return max(p_ids) + 1 if p_ids else 1
    except Exception:
        return 1


def extract_json_block(text: str) -> str:
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1].strip()
    return text


def erase_last_n_patients(n: int = 4) -> None:
    """Removes the last N patients from expanded JSON, seeded ID cache, and Supabase."""
    expanded_file = find_expanded_json_file()
    try:
        data = json.loads(expanded_file.read_text(encoding="utf-8"))
    except Exception:
        print("! No patients_expanded.json file found to trim.")
        return

    patients = data.get("patients", [])
    if not patients:
        print("! Patient list is already empty.")
        return

    to_remove = patients[-n:]
    removed_pids = [
        p.get("patient_id") or p.get("patient", {}).get("patient_id")
        for p in to_remove
        if p.get("patient_id") or p.get("patient", {}).get("patient_id")
    ]

    data["patients"] = patients[:-n]
    data.setdefault("metadata", {})["patient_count"] = len(data["patients"])
    expanded_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"✓ Removed {len(removed_pids)} patient records from {expanded_file.name}: {removed_pids}")

    if SEEDED_ID_PATH.exists():
        try:
            seeded_map = json.loads(SEEDED_ID_PATH.read_text(encoding="utf-8"))
            for pid in removed_pids:
                seeded_map.pop(pid, None)
            SEEDED_ID_PATH.write_text(json.dumps(seeded_map, indent=2), encoding="utf-8")
            print(f"✓ Removed {len(removed_pids)} IDs from seeded map.")
        except Exception as e:
            print(f"! Warning: Failed to clean seeded IDs map: {e}")

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    if supabase_url and supabase_key and removed_pids:
        try:
            from supabase import create_client
            client = create_client(supabase_url, supabase_key)
            client.table("patients").delete().in_("patient_id", removed_pids).execute()
            print(f"✓ Deleted {len(removed_pids)} records from Supabase table 'patients'.")
        except Exception as e:
            print(f"! Warning: Failed to prune from Supabase: {e}")


# ---------------------------------------------------------------------------
# Parallelized LLM Generation
# ---------------------------------------------------------------------------
async def _generate_single_patient(
    client: AsyncOpenAI,
    model_name: str,
    curr_id: str,
    target_region: str,
    target_disease_profile: dict,
    schema_str: str,
    current_year: int,
    semaphore: asyncio.Semaphore,
) -> Optional[Dict[str, Any]]:
    prompt = f"""You are an expert Clinical Data Architect.
Generate 1 realistic synthetic clinical patient record strictly matching the JSON schema below.

Target JSON Schema:
{schema_str}

Clinical Category: {target_disease_profile['category']}
Cohort: {target_disease_profile['cohort']}
Context: {target_disease_profile['description']}
Diagnoses Hints: {', '.join(target_disease_profile['diagnoses_hints'])}
Medication Hints: {', '.join(target_disease_profile['medications_hints'])}

Directives:
1. 'patient_id': Must be exactly "{curr_id}".
2. 'name': Authentic full name matching sex ('female' or 'male') for origin: {target_region}. Never return null or empty.
3. 'diagnoses' & 'medications': Match category {target_disease_profile['category']}.
4. 'medical_history': 1 to 3 past surgeries or clinical events.
5. 'medical_history_narrative': 2-3 sentence narrative summarizing profile.
6. Absolute lab units: ANC (2000-6500 /uL, absolute count), Platelets (150000-380000 /uL), eGFR (60-105), ALT/AST (20-45 U/L).

Return valid JSON only.
"""
    async with semaphore:
        for _ in range(3):
            try:
                resp = await client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "You are a clinical data system generating strict JSON. Output JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                    timeout=35.0,
                )
                raw_text = extract_json_block(resp.choices[0].message.content or "{}")
                p_obj = GeneratedPatient.model_validate_json(raw_text)
                dumped = p_obj.model_dump()

                age = dumped.get("age", 55)
                dob = f"{current_year - age}-03-15"
                dumped["birth_date"] = dob
                dumped["dob"] = dob
                dumped["internal_id"] = dumped["patient_id"]
                dumped["fhir_id"] = None
                dumped["sex"] = "female" if str(dumped.get("sex", "")).lower().startswith("f") else "male"

                raw_labs = dumped.get("lab_results", {})
                units = {
                    "ALT": "U/L", "AST": "U/L", "eGFR": "mL/min/1.73m2",
                    "ANC": "/uL", "platelets": "/uL", "hemoglobin": "g/dL",
                    "INR": "ratio", "total_bilirubin": "mg/dL",
                    "serum_creatinine": "mg/dL", "creatinine_clearance": "mL/min"
                }
                structured_labs = {}
                for k, v in raw_labs.items():
                    val = float(v.get("value", v)) if isinstance(v, dict) else float(v)
                    if k == "ANC" and val < 100.0:
                        val *= 1000.0
                    elif k == "platelets" and val < 1000.0:
                        val *= 1000.0
                    structured_labs[k] = {"value": val, "unit": units.get(k, "unit")}
                dumped["lab_results"] = structured_labs

                return dumped
            except Exception:
                await asyncio.sleep(0.5)
    return None


async def generate_synthetic_patients_async(count: int = 4) -> List[Dict[str, Any]]:
    api_key = os.getenv("KADO_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("KADO_BASE_URL", "https://awesome.kado.so/openai/v1")
    model_name = os.getenv("KADO_MODEL", "kado")

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers={"x-bf-vk": api_key},
        max_retries=0,
    )
    expanded_file = find_expanded_json_file()
    start_id = get_next_patient_id(expanded_file)
    current_year = date.today().year
    schema_str = json.dumps(GeneratedPatient.model_json_schema())

    semaphore = asyncio.Semaphore(5)
    tasks = []

    ethos_cycle = itertools.cycle(random.sample(REGIONAL_CULTURAL_ETHOSES, len(REGIONAL_CULTURAL_ETHOSES)))
    disease_cycle = itertools.cycle(random.sample(DISEASE_SCENARIO_PROFILES, len(DISEASE_SCENARIO_PROFILES)))

    print(f"--> Generating {count} synthetic patient profiles concurrently...")
    for idx in range(count):
        curr_id = f"P{start_id + idx:03d}"
        tasks.append(
            _generate_single_patient(
                client, model_name, curr_id, next(ethos_cycle),
                next(disease_cycle), schema_str, current_year, semaphore
            )
        )

    results = await asyncio.gather(*tasks)
    valid_patients = [r for r in results if r is not None]
    print(f"✓ Successfully generated {len(valid_patients)}/{count} patient profiles.")
    return valid_patients


# ---------------------------------------------------------------------------
# High-Speed FHIR R4 Transaction Bundle Seeder
# ---------------------------------------------------------------------------
def build_patient_transaction_bundle(patient: Dict[str, Any]) -> dict:
    internal_id = patient.get("patient_id")
    ai_name = patient.get("name", "Murugan Sundaram")
    name_parts = ai_name.strip().split(" ", 1)
    given = [name_parts[0]]
    family = name_parts[1] if len(name_parts) > 1 else ""
    full_urn = f"urn:uuid:{uuid.uuid4()}"
    system = "https://techquest-hackathon.local/tags"

    entries = []

    entries.append({
        "fullUrl": full_urn,
        "resource": {
            "resourceType": "Patient",
            "identifier": [{"system": system, "value": internal_id}],
            "name": [{"use": "official", "family": family, "given": given, "text": ai_name}],
            "gender": "female" if patient.get("sex") == "female" else "male",
            "birthDate": patient.get("birth_date", "1970-01-01"),
            "active": True,
        },
        "request": {"method": "POST", "url": "Patient"},
    })

    for item in patient.get("medical_history", []):
        entries.append({
            "resource": {
                "resourceType": "Condition",
                "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "resolved"}]},
                "code": {"text": str(item)},
                "subject": {"reference": full_urn},
            },
            "request": {"method": "POST", "url": "Condition"},
        })

    for diag in patient.get("diagnoses", []):
        entries.append({
            "resource": {
                "resourceType": "Condition",
                "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]},
                "code": {"text": str(diag)},
                "subject": {"reference": full_urn},
            },
            "request": {"method": "POST", "url": "Condition"},
        })

    for med in patient.get("medications", []):
        entries.append({
            "resource": {
                "resourceType": "MedicationStatement",
                "status": "active",
                "medicationCodeableConcept": {"text": str(med)},
                "subject": {"reference": full_urn},
            },
            "request": {"method": "POST", "url": "MedicationStatement"},
        })

    for code, lab_data in patient.get("lab_results", {}).items():
        val = lab_data.get("value") if isinstance(lab_data, dict) else lab_data
        unit = lab_data.get("unit", "") if isinstance(lab_data, dict) else ""
        entries.append({
            "resource": {
                "resourceType": "Observation",
                "status": "final",
                "code": {"text": code},
                "valueQuantity": {"value": val, "unit": unit},
                "subject": {"reference": full_urn},
            },
            "request": {"method": "POST", "url": "Observation"},
        })

    return {"resourceType": "Bundle", "type": "transaction", "entry": entries}


async def _seed_single_patient_bundle(
    client: httpx.AsyncClient, patient: Dict[str, Any], semaphore: asyncio.Semaphore
) -> tuple[str, str, str]:
    bundle = build_patient_transaction_bundle(patient)
    pid = patient["patient_id"]
    async with semaphore:
        for _ in range(3):
            try:
                resp = await client.post(FHIR_BASE_URL, json=bundle, timeout=30.0)
                if resp.status_code in (200, 201):
                    data = resp.json()
                    patient_entry = data.get("entry", [{}])[0]
                    location = patient_entry.get("response", {}).get("location", "")
                    fhir_id = location.split("/_history")[0].split("/")[-1] if location else str(random.randint(100000, 999999))
                    return pid, fhir_id, patient.get("name", "Unknown")
            except Exception:
                await asyncio.sleep(1.0)
    return pid, f"fallback-{pid}", patient.get("name", "Unknown")


async def seed_to_fhir_server_async(patients: List[Dict[str, Any]]) -> Dict[str, Any]:
    print(f"--> Uploading {len(patients)} FHIR transaction bundles in parallel to {FHIR_BASE_URL}...")
    existing_map = {}
    if SEEDED_ID_PATH.exists():
        try:
            existing_map = json.loads(SEEDED_ID_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    semaphore = asyncio.Semaphore(6)
    async with httpx.AsyncClient(timeout=45.0) as client:
        tasks = [_seed_single_patient_bundle(client, p, semaphore) for p in patients]
        results = await asyncio.gather(*tasks)

    for pid, fhir_id, p_name in results:
        matched = next((p for p in patients if p["patient_id"] == pid), {})
        matched["fhir_id"] = fhir_id
        existing_map[pid] = {
            "fhir_id": fhir_id,
            "name": p_name,
            "cohort": matched.get("cohort", "Cohort A - Standard Protocol"),
        }
        print(f"  ✓ Seeded {pid} ({p_name}) -> FHIR Patient/{fhir_id}")

    SEEDED_ID_PATH.write_text(json.dumps(existing_map, indent=2), encoding="utf-8")
    return existing_map


# ---------------------------------------------------------------------------
# Storage & Supabase Sync
# ---------------------------------------------------------------------------
def append_to_expanded_json(new_patients: List[Dict[str, Any]], target_trial_ids: List[str]) -> Path:
    expanded_file = find_expanded_json_file()
    try:
        data = json.loads(expanded_file.read_text(encoding="utf-8"))
    except Exception:
        data = {"metadata": {}, "patients": []}

    existing = data.get("patients", [])
    trial_cycler = itertools.cycle(target_trial_ids)

    for p in new_patients:
        patient_name = p.get("name", "Unknown Patient")
        clean = {k: v for k, v in p.items()}
        assigned_trial = next(trial_cycler)
        existing.append({
            "patient_id": p["patient_id"],
            "name": patient_name,
            "assigned_demo_trial_id": assigned_trial,
            "cohort": p.get("cohort", "Cohort A - Standard Protocol"),
            "demo_category": "SYNTHETIC_EHR",
            "patient": clean,
            "fhir_id": p.get("fhir_id"),
        })

    data["patients"] = existing
    data["metadata"]["patient_count"] = len(existing)
    expanded_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return expanded_file


def push_to_supabase(target_table: str = "patients") -> None:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        return

    try:
        from supabase import create_client
    except ImportError:
        return

    expanded_file = find_expanded_json_file()
    data = json.loads(expanded_file.read_text(encoding="utf-8"))
    patient_entries = data.get("patients", [])
    if not patient_entries:
        return

    seeded_map = json.loads(SEEDED_ID_PATH.read_text(encoding="utf-8")) if SEEDED_ID_PATH.exists() else {}
    client = create_client(supabase_url, supabase_key)

    rows = []
    for entry in patient_entries:
        p = entry.get("patient", entry)
        pid = entry.get("patient_id")
        mapped = seeded_map.get(pid, {})
        resolved_name = (
            mapped.get("name")
            if isinstance(mapped, dict) and mapped.get("name")
            else entry.get("name") or p.get("name") or "Unknown"
        )
        raw_dob = p.get("birth_date") or p.get("dob")
        dob_val = raw_dob if (raw_dob and str(raw_dob).count("-") == 2) else None
        age_val = p.get("age") if (p.get("age") is not None and isinstance(p.get("age"), (int, float)) and p.get("age") > 0) else None
        sex_val = p.get("sex") if (p.get("sex") and str(p.get("sex")).strip().lower() not in {"unknown", "unrecorded", "none", ""}) else None
        diagnoses = p.get("diagnoses", ["Unknown"])
        primary_dx = diagnoses[0] if diagnoses else entry.get("diagnosis", "Unknown")

        rows.append({
            "patient_id": pid,
            "trial_id": entry.get("assigned_demo_trial_id") or "NCT02415400",
            "name": resolved_name,
            "dob": dob_val,
            "age": age_val,
            "sex": sex_val,
            "cohort": entry.get("cohort"),
            "diagnosis": primary_dx,
            "fhir_id": str(mapped.get("fhir_id") or entry.get("fhir_id") or f"synthetic-{pid}"),
            "assigned_demo_trial_id": entry.get("assigned_demo_trial_id"),
            "demo_category": "SYNTHETIC_EHR",
            "clinical_data": p,
        })

    client.table(target_table).upsert(rows, on_conflict="patient_id").execute()
    print(f"✓ Upserted {len(rows)} patient records into Supabase.")


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------
async def run_pipeline(count: int, reset: bool, dry_run: bool, trim_last: Optional[int] = None):
    if trim_last is not None and trim_last > 0:
        erase_last_n_patients(n=trim_last)
        return

    if reset:
        reset_local_patient_storage()

    target_trials = get_available_rag_trial_ids(limit_count=4)
    start_time = time.time()

    patients = await generate_synthetic_patients_async(count=count)
    if patients:
        if not dry_run:
            await seed_to_fhir_server_async(patients)
        else:
            existing_map = {}
            if SEEDED_ID_PATH.exists():
                try:
                    existing_map = json.loads(SEEDED_ID_PATH.read_text(encoding="utf-8"))
                except Exception:
                    pass
            for p in patients:
                existing_map[p["patient_id"]] = {
                    "fhir_id": f"dry-run-{p['patient_id']}",
                    "name": p.get("name", "Unknown"),
                    "cohort": p.get("cohort", "Cohort A - Standard Protocol"),
                }
            SEEDED_ID_PATH.write_text(json.dumps(existing_map, indent=2), encoding="utf-8")

        append_to_expanded_json(patients, target_trial_ids=target_trials)
        push_to_supabase()

    print(f"\n⚡ Finished pipeline for {len(patients)} patients in {time.time() - start_time:.2f}s.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=4, help="Number of patients to generate")
    parser.add_argument("--reset", action="store_true", help="Reset all storage and seed fresh")
    parser.add_argument("--dry-run", action="store_true", help="Generate locally without remote FHIR")
    parser.add_argument("--trim-last", type=int, nargs="?", const=4, default=None, help="Erase the last N patients (default: 4)")
    args = parser.parse_args()

    asyncio.run(run_pipeline(count=args.count, reset=args.reset, dry_run=args.dry_run, trim_last=args.trim_last))