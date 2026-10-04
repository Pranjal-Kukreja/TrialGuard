import os
import re
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()


class DosageModification(BaseModel):
    dosage_name: str = Field(description="Name of the drug or biological parameter (e.g., 'Apixaban', 'Pembrolizumab')")
    proposed_dosage: float = Field(description="The extracted exact numerical value")
    dosage_unit: str = Field(default="mg", description="The unit of measurement (e.g., 'mg', 'g')")
    frequency: str = Field(default="twice daily", description="Dosing frequency (e.g., 'twice daily', 'once daily', 'every 3 weeks')")
    route: str = Field(default="oral", description="Route of administration (e.g., 'oral', 'IV')")
    timing_schedule: str = Field(default="Every 12 hours (08:00, 20:00)", description="Timing schedule string")
    target_field: str = Field(default="MedicationRequest.dosageInstruction[0]", description="FHIR resource field path")


class ExtractedOverride(BaseModel):
    is_valid: bool = Field(description="True ONLY if exact numerical dosages can be determined.")
    is_appropriate: bool = Field(default=True, description="True if the note is a valid clinical prescription intent; False if vague or conversational.")
    warning: Optional[str] = Field(default=None, description="Clinical warning if the note is inappropriate, vague, or missing critical data.")
    standardized_drug: Optional[str] = Field(default=None, description="Standardized formulary drug name.")
    original_spelling: Optional[str] = Field(default=None, description="Original spelling in note.")
    spelling_corrected: bool = Field(default=False, description="True if spelling was corrected.")
    standardized_action: Optional[str] = Field(default=None, description="Full standardized clinical action string.")
    target_fhir_field: str = Field(default="MedicationRequest.dosageInstruction[0]", description="Target FHIR field to update.")
    reasoning: str = Field(description="Explanation of clinical intent verification or what is missing.")
    modifications: List[DosageModification] = Field(default_factory=list, description="List of specific parameter modifications extracted.")


FORMULARY_SYNONYMS = {
    "apixaban": {
        "canonical": "Apixaban",
        "default_dose": 5.0,
        "default_unit": "mg",
        "default_freq": "twice daily",
        "default_route": "oral",
        "default_timing": "Every 12 hours (08:00, 20:00)",
        "synonyms": ["apixaban", "apixiban", "apixibam", "apixabam", "eliquis", "eliquiss"],
    },
    "pembrolizumab": {
        "canonical": "Pembrolizumab",
        "default_dose": 200.0,
        "default_unit": "mg",
        "default_freq": "every 3 weeks",
        "default_route": "IV",
        "default_timing": "Day 1 of 21-day cycle (09:00)",
        "synonyms": ["pembrolizumab", "pemprolizumab", "pembro", "keytruda", "keytrudaa"],
    },
    "empagliflozin": {
        "canonical": "Empagliflozin",
        "default_dose": 10.0,
        "default_unit": "mg",
        "default_freq": "once daily",
        "default_route": "oral",
        "default_timing": "Every 24 hours (08:00)",
        "synonyms": ["empagliflozin", "empaglifozin", "jardiance"],
    },
    "pioglitazone": {
        "canonical": "Pioglitazone",
        "default_dose": 30.0,
        "default_unit": "mg",
        "default_freq": "once daily",
        "default_route": "oral",
        "default_timing": "Every 24 hours (08:00)",
        "synonyms": ["pioglitazone", "actos"],
    },
}


def _fallback_extract(comment: str) -> dict:
    text = (comment or "").strip()
    lower = text.lower()

    if not text or len(text) < 4:
        return {
            "is_valid": False,
            "is_appropriate": False,
            "warning": "Clinical note is empty or incomplete. An explicit therapeutic intervention order is required.",
            "reasoning": "Insufficient clinical detail provided in clinician note.",
            "modifications": [],
        }

    conversational = ["hello", "hi there", "weather", "lunch", "sunny", "good day", "test", "asdf"]
    if any(c in lower for c in conversational):
        return {
            "is_valid": False,
            "is_appropriate": False,
            "warning": "Clinical Warning: Inappropriate clinical note. The submitted narrative contains non-clinical or conversational text. Please specify a medication and target dosage.",
            "reasoning": "Non-clinical narrative detected.",
            "modifications": [],
        }

    matched_entry = None
    matched_orig = None
    for entry in FORMULARY_SYNONYMS.values():
        for syn in entry["synonyms"]:
            if syn in lower:
                matched_entry = entry
                matched_orig = syn
                break
        if matched_entry:
            break

    dose_match = re.search(r"(\d+(?:\.\d+)?)\s*(mg|mcg|g)\b", lower)
    if not dose_match and re.search(r"\b(lower|increase|reduce|adjust)\b", lower):
        drug_name = matched_entry["canonical"] if matched_entry else "the medication"
        return {
            "is_valid": False,
            "is_appropriate": False,
            "warning": f"Clinical Warning: Ambiguous titration directive for {drug_name}. A specific quantitative numerical dosage is required.",
            "reasoning": "Directive lacks a target numerical dosage value.",
            "modifications": [],
        }

    if not matched_entry and not dose_match:
        return {
            "is_valid": False,
            "is_appropriate": False,
            "warning": "Clinical Warning: Unrecognized prescription directive. Please specify both an identifiable medication and numerical dosage.",
            "reasoning": "Neither a trial drug nor quantitative dosage could be identified.",
            "modifications": [],
        }

    entry = matched_entry or FORMULARY_SYNONYMS["apixaban"]
    canonical = entry["canonical"]
    spelling_corrected = bool(matched_orig and matched_orig.lower() != canonical.lower())

    dose_val = float(dose_match.group(1)) if dose_match else entry["default_dose"]
    unit_val = dose_match.group(2).lower() if dose_match else entry["default_unit"]

    freq = entry["default_freq"]
    timing = entry["default_timing"]
    route = entry["default_route"]

    if any(k in lower for k in ["bid", "twice daily", "twice a day", "q12h"]):
        freq = "twice daily"
        timing = "Every 12 hours (08:00, 20:00)"
    elif any(k in lower for k in ["qd", "once daily", "daily", "q24h"]):
        freq = "once daily"
        timing = "Every 24 hours (08:00)"
    elif any(k in lower for k in ["q3w", "every 3 weeks"]):
        freq = "every 3 weeks"
        timing = "Day 1 of 21-day cycle (09:00)"
        route = "IV"

    if any(k in lower for k in ["iv", "intravenous"]):
        route = "IV"
    elif any(k in lower for k in ["oral", "po"]):
        route = "oral"

    standardized_action = f"{canonical} {dose_val:g} {unit_val} {route} {freq}"

    return {
        "is_valid": True,
        "is_appropriate": True,
        "warning": None,
        "standardized_drug": canonical,
        "original_spelling": matched_orig or canonical,
        "spelling_corrected": spelling_corrected,
        "standardized_action": standardized_action,
        "target_fhir_field": "MedicationRequest.dosageInstruction[0]",
        "reasoning": f"Clinical intent verified. Standardized to {standardized_action} ({timing}).",
        "modifications": [
            {
                "dosage_name": canonical,
                "proposed_dosage": dose_val,
                "dosage_unit": unit_val,
                "frequency": freq,
                "route": route,
                "timing_schedule": timing,
                "target_field": "MedicationRequest.dosageInstruction[0]",
            }
        ],
    }


_kado_key = os.getenv("KADO_API_KEY") or os.getenv("OPENAI_API_KEY")
_kado_base = os.getenv("KADO_BASE_URL", "https://awesome.kado.so/openai/v1")
_kado_model = os.getenv("KADO_MODEL", "kado")

_llm = None
if _kado_key:
    try:
        from langchain_openai import ChatOpenAI
        _llm = ChatOpenAI(
            model=_kado_model,
            api_key=_kado_key,
            base_url=_kado_base,
            temperature=0,
            default_headers={"x-bf-vk": _kado_key},
            timeout=10,
        )
    except Exception:
        _llm = None


class CommentRequest(BaseModel):
    comment: str


@router.post("/api/extract-comment")
async def extract_comment(request: CommentRequest):
    if _llm:
        try:
            structured = _llm.with_structured_output(ExtractedOverride)
            prompt = (
                "You are an expert Clinical Pharmacologist and EHR NLP Adjudicator. "
                "Analyze the clinician's prescription note:\n"
                f'"{request.comment}"\n\n'
                "Determine:\n"
                "1. Is it clinically appropriate with an identifiable drug and numerical dosage? "
                "(Allow spelling errors or brand names like apixiban, eliquis, pembro, keytruda).\n"
                "2. If inappropriate or vague without numbers, set is_appropriate=False, is_valid=False, and provide a clear clinical warning.\n"
                "3. If appropriate, extract standardized_drug, dosage, dosage_unit, route, frequency, timing_schedule, standardized_action, target_fhir_field, and modifications list."
            )
            result = structured.invoke(prompt)
            if result and hasattr(result, "model_dump"):
                dumped = result.model_dump()
                if dumped.get("is_valid") or dumped.get("is_appropriate") is False:
                    return dumped
        except Exception:
            pass

    return _fallback_extract(request.comment)