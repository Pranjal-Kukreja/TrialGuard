"""Financial risk & coverage specialist used behind the A2A adapter."""

from __future__ import annotations

import json
from typing import Any

from .llm_client import call_llm, parse_json_response


DRUG_FINANCIAL_PROFILES = {
    "apixaban": {
        "drug_name": "Apixaban",
        "standard_dose": "5 mg oral BID",
        "allowed_doses": ["2.5 mg", "2.5mg", "5 mg", "5mg"],
        "unapproved_exposure": 3200,
        "trial_id": "NCT02415400",
        "coverage_plan": "Medicare Part B + Clinical Trial Sponsor Agreement (NCT02415400 / NCT00781573)",
        "terms": "Sponsor provides 100% coverage ONLY for protocol-specified oral anticoagulation (Apixaban 5 mg BID or 2.5 mg BID renal adjustment). Non-protocol excessive dosages are strictly excluded from research grant billing.",
    },
    "empagliflozin": {
        "drug_name": "Empagliflozin",
        "standard_dose": "10 mg oral daily",
        "allowed_doses": ["10 mg", "10mg", "25 mg", "25mg"],
        "unapproved_exposure": 1250,
        "trial_id": "NCT00699998",
        "coverage_plan": "Clinical Research Agreement - Renal SGLT2i Stratification (NCT00699998)",
        "terms": "Sponsor covers investigational SGLT2i therapy at 10 mg or 25 mg daily per protocol. Unauthorized dose escalations or unapproved combinations require secondary prior authorization.",
    },
    "pioglitazone": {
        "drug_name": "Pioglitazone",
        "standard_dose": "30 mg oral daily",
        "allowed_doses": ["15 mg", "15mg", "30 mg", "30mg", "45 mg", "45mg"],
        "unapproved_exposure": 450,
        "trial_id": "NCT00809965",
        "coverage_plan": "Investigational Metabolic CTA (NCT00809965 - NAFLD/MASH)",
        "terms": "Sponsor covers research grant formulary for oral TZD therapy (15-30 mg daily). Non-protocol dosing incurs secondary patient out-of-pocket exposure.",
    },
    "pembrolizumab": {
        "drug_name": "Pembrolizumab",
        "standard_dose": "200 mg IV Q3W",
        "allowed_doses": ["200 mg", "200mg", "400 mg Q6W"],
        "unapproved_exposure": 23000,
        "trial_id": "NCT02415400",
        "coverage_plan": "Specialty Biologics Clinical Trial Grant (Oncology Cohort C)",
        "terms": "Sponsor covers monoclonal antibody immunotherapy strictly per 200 mg Q3W schedule. Off-label frequencies or unapproved escalations require specialty prior authorization with significant non-covered liability.",
    },
}


def _detect_drug_key(text: str) -> str:
    lower = text.lower()
    for key in DRUG_FINANCIAL_PROFILES:
        if key in lower:
            return key
    return "apixaban"


def evaluate(
    trial_id: str,
    patient_id: str | None,
    recent_action: dict,
    financial_context: dict | None = None,
    policies: list[dict] | None = None,
    report_history: list[dict] | None = None,
    modification: str = "",
) -> dict:
    action_text = json.dumps(recent_action) if isinstance(recent_action, dict) else str(recent_action)
    action_str = action_text.lower()
    dosage_str = str(recent_action.get("dosage", "")).lower() if isinstance(recent_action, dict) else action_str
    drug_str = str(recent_action.get("drug", "")).lower() if isinstance(recent_action, dict) else ""

    drug_key = _detect_drug_key(drug_str or action_str or trial_id)
    profile = DRUG_FINANCIAL_PROFILES.get(drug_key, DRUG_FINANCIAL_PROFILES["apixaban"])
    drug_display = profile["drug_name"]
    standard_dose_str = profile["standard_dose"]
    unapproved_exposure = profile["unapproved_exposure"]

    # Check for unapproved dose or unauthorized escalation
    is_unapproved_dose = any(
        term in dosage_str or term in action_str
        for term in ["40 mg", "40mg", "60 mg", "60mg", "overdose", "escalat", "unapproved", "8x"]
    )
    # Check if standard therapeutic dosage is confirmed
    is_standard_dose = any(ad in dosage_str or ad in action_str for ad in profile["allowed_doses"]) and not is_unapproved_dose

    ctx = financial_context or {
        "coverage_plan": profile["coverage_plan"],
        "investigational_drug_terms": profile["terms"],
        "protocol_allowance": "$50,000 research cap",
        "standard_protocol_dose": standard_dose_str,
    }
    pol = policies or [
        {
            "policy_id": f"SPONSOR-CTA-{drug_key.upper()}-01",
            "name": f"Clinical Trial Agreement — {drug_display} Protocol Compliance Clause",
            "text": f"Sponsor covers investigational {drug_display} only when administered per approved protocol ({standard_dose_str}). Non-protocol dosing violates trial terms; sponsor billing is denied and secondary prior authorization / non-covered liability applies.",
            "standard_dose": standard_dose_str,
        },
        {
            "policy_id": "CMS-NCD-310.1",
            "name": "Medicare Clinical Trial Policy — Investigational Item Coverage",
            "text": "Routine costs are covered only when investigational items conform to trial design. Off-protocol overdoses or unapproved escalations require prior authorization or are denied as non-covered investigational charges.",
        },
    ]

    prompt = f"""You are the TrialGuard AI Financial & Coverage Risk Agent.
Evaluate whether the prescribed trial intervention is covered under clinical research billing guidelines or requires prior authorization / triggers financial risk.

CRITICAL CLINICAL RESEARCH BILLING RULES FOR {drug_display.upper()}:
1. Standard protocol dosing for {trial_id} is {standard_dose_str}. When the prescribed action matches standard protocol dosing, it is 100% covered by the sponsor CTA at $0 patient liability:
   - coverage_status: "COVERED"
   - pre_auth_required: false
   - sponsor_billing_eligible: true
   - estimated_exposure: 0
   - tier: "Tier-1 Investigational Coverage"
2. Off-protocol dosages, unauthorized dose escalations, and protocol violations are EXCLUDED from sponsor clinical trial reimbursement:
   - coverage_status: "REQUIRES_PRE_AUTH"
   - pre_auth_required: true
   - sponsor_billing_eligible: false
   - estimated_exposure: {unapproved_exposure}
   - tier: "Non-Covered Protocol Deviation / Prior Auth Required"
   - explanation: Detail that the sponsor denies reimbursement for unapproved dosing and that prior authorization is required with ${unapproved_exposure:,.0f} exposure.

Return ONLY valid JSON with exactly:
{{"coverage_status": "COVERED", "pre_auth_required": false, "sponsor_billing_eligible": true, "estimated_exposure": 0, "tier": "Tier-1 Investigational Coverage", "explanation": "..."}}
Allowed values for coverage_status: "COVERED", "NOT_COVERED", "REQUIRES_PRE_AUTH".

TRIAL ID: {trial_id}
RECENT ACTION: {action_text}
MODIFICATION: {modification or '(none)'}
FINANCIAL CONTEXT: {json.dumps(ctx, indent=2)}
POLICIES: {json.dumps(pol, indent=2)}
REPORT HISTORY: {json.dumps(report_history or [], indent=2)}"""

    try:
        raw_result = parse_json_response(call_llm(prompt, max_tokens=500))
    except Exception:
        raw_result = {}

    # Deterministic enforcement of clinical research billing rules
    if is_unapproved_dose:
        status = "REQUIRES_PRE_AUTH"
        exposure = unapproved_exposure
        callout = f"Sponsor coverage denied: Prescribed dosing violates {trial_id} protocol. Prior auth required; estimated exposure: ${exposure:,.0f}."
        explanation = (
            raw_result.get("explanation")
            or f"The study sponsor covers 100% of medication costs ONLY for protocol-compliant dosing ({standard_dose_str}). "
            f"The prescribed regimen represents an unapproved protocol deviation, disqualifying it from sponsor billing "
            f"and triggering prior authorization requirements with ${exposure:,.0f} in non-covered pharmaceutical liability."
        )
        tier = "Non-Covered Protocol Deviation / Prior Auth Required"
        pre_auth = True
        sponsor_eligible = False
    elif is_standard_dose:
        status = "COVERED"
        exposure = 0
        callout = f"100% Protocol & Investigational Coverage under Sponsor Trial Agreement for {drug_display} (Zero Patient Liability)."
        explanation = (
            raw_result.get("explanation")
            or f"Intervention complies with protocol {trial_id} standard {drug_display} dosing ({standard_dose_str}). "
            f"100% covered under sponsor clinical research billing agreement at zero patient liability."
        )
        tier = "Tier-1 Investigational Coverage"
        pre_auth = False
        sponsor_eligible = True
    else:
        status = raw_result.get("coverage_status", "COVERED")
        if status not in {"COVERED", "NOT_COVERED", "REQUIRES_PRE_AUTH"}:
            status = "COVERED"
        exposure = raw_result.get("estimated_exposure", 0 if status == "COVERED" else unapproved_exposure)
        pre_auth = bool(raw_result.get("pre_auth_required", status == "REQUIRES_PRE_AUTH"))
        sponsor_eligible = bool(raw_result.get("sponsor_billing_eligible", status == "COVERED"))
        tier = str(raw_result.get("tier", "Tier-1 Investigational Coverage" if status == "COVERED" else "Secondary Payer Prior Authorization"))
        raw_explanation = raw_result.get("explanation")
        if status == "COVERED":
            exposure = 0
            callout = f"100% Protocol & Investigational Coverage under Sponsor Trial Agreement for {drug_display} (Zero Patient Liability)."
            explanation = raw_explanation or f"Intervention complies with protocol {trial_id} standard dosing for {drug_display}. 100% covered under sponsor clinical research billing agreement at zero patient liability."
        elif status == "REQUIRES_PRE_AUTH":
            callout = f"Prior authorization required for modified {drug_display} regimen. Estimated exposure: ${exposure:,.0f}."
            explanation = raw_explanation or f"Modified {drug_display} regimen requires prior authorization under secondary payer guidelines before sponsor reimbursement approval."
        else:
            callout = f"Uncovered clinical exposure: ${exposure:,.0f} out-of-pocket liability for {drug_display}."
            explanation = raw_explanation or f"Non-protocol {drug_display} intervention not eligible for sponsor clinical trial reimbursement."

    return {
        "patientId": patient_id,
        "coverage_status": status,
        "pre_auth_required": pre_auth,
        "sponsor_billing_eligible": sponsor_eligible,
        "tier": tier,
        "financialExposure": exposure,
        "callout": callout,
        "explanation": explanation,
        "confidence": 0.95,
    }
