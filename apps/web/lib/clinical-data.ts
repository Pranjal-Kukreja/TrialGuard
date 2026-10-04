export type Patient = {
  id: string
  name: string
  dob: string
  age: number
  sex: string
  cohort: string
  diagnosis: string
  creatinine: string
  trial_id?: string
  medications?: string[]
  clinical_data?: Record<string, any>
  report_history?: any[]
  action?: string
}

export const PATIENTS: Patient[] = [
  {
    "id": "P001",
    "name": "Swaminathan",
    "dob": "1964-03-15",
    "age": 62,
    "sex": "M",
    "cohort": "Cohort B - Renal Stratification - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "diabetic nephropathy stage 3a",
    "creatinine": "CrCl 55.0 mL/min",
    "trial_id": "NCT00699998",
    "medications": [
      "empagliflozin 10mg daily",
      "losartan 50mg daily",
      "torsemide 10mg daily"
    ],
    "clinical_data": {
      "age": 62,
      "dob": "1964-03-15",
      "sex": "male",
      "cohort": "Cohort B - Renal Stratification",
      "status": "JUSTIFIED",
      "weight": 68.0,
      "fhir_id": "138792165",
      "allergies": [],
      "diagnoses": [
        "diabetic nephropathy stage 3a",
        "membranous nephropathy"
      ],
      "birth_date": "1964-03-15",
      "patient_id": "P001",
      "ecog_status": 0,
      "internal_id": "P001",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 30.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 3800.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 58.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 240000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.8
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.8
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.2
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 55.0
        }
      },
      "medications": [
        "empagliflozin 10mg daily",
        "losartan 50mg daily",
        "torsemide 10mg daily"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "renal biopsy (2019)",
        "appendectomy (2005)"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "lower extremity edema",
        "fatigue"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "adjudication_reports": [
        {
          "saved_at": "2026-09-16T19:38:18.326618+00:00",
          "trial_id": "NCT00699998",
          "report_id": "2fe0cc66-15c7-447b-891a-0040d2243e07",
          "patient_id": "P001",
          "final_verdict": "JUSTIFIED",
          "final_decision": "ACCEPTED",
          "clinician_justification": "Approved per protocol guidelines."
        },
        {
          "summary": null,
          "saved_at": "2026-09-16T19:46:01.873497+00:00",
          "trial_id": "NCT00699998",
          "report_id": "b78ec40a-bf97-4015-9ed5-01674c8246f4",
          "patient_id": "P001",
          "protocol_id": "NCT00699998",
          "agent_metrics": {},
          "final_verdict": null,
          "safety_result": {},
          "final_decision": "accept",
          "report_history": [],
          "iteration_count": 0,
          "safety_evidence": [],
          "financial_result": {},
          "protocol_evidence": [],
          "decision_timestamp": "2026-09-17T01:10:00Z",
          "clinician_justification": "Clinician approved intervention.",
          "final_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "original_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "protocol_compliance_result": {}
        },
        {
          "summary": "The prescribed Empagliflozin 10 mg daily matches the protocol for Cohort B. The patient's eGFR of 58 mL/min/1.73m\u00b2 exceeds the safety threshold of \u226545, and no drug interactions or safety concerns were identified. Financial coverage is 100% under the sponsor trial agreement with zero patient liability. All checks confirm the action is appropriate and safe.",
          "saved_at": "2026-09-16T19:52:54.563445+00:00",
          "trial_id": "NCT00699998",
          "report_id": "8da254b0-2f29-4f4a-8876-346c5f730fb8",
          "patient_id": "P001",
          "protocol_id": "NCT00699998",
          "agent_metrics": {
            "Arbitration Reducer": {
              "confidence": 0.95,
              "latency_ms": 18022
            },
            "Financial Risk Agent": {
              "confidence": 0.95,
              "latency_ms": 5199
            },
            "Safety & Toxicity Agent": {
              "latency_ms": 7851
            },
            "Protocol Compliance Agent": {
              "latency_ms": 8567
            }
          },
          "final_verdict": "JUSTIFIED",
          "safety_result": {
            "safe": true,
            "concerns": [],
            "evidence": [
              "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.91,
            "patient_id": "P001",
            "explanation": "Patient's eGFR 58 mL/min/1.73m2 is above threshold for empagliflozin use (\u226545). No drug-drug interactions identified. Liver function normal. No safety concerns.",
            "safety_status": "SAFE",
            "needs_human_review": false
          },
          "final_decision": "reject",
          "report_history": [
            {
              "agent": "Protocol Compliance Agent",
              "status": "COMPLIANT",
              "verdict": "COMPLIANT",
              "iteration": 0,
              "confidence": 0.9,
              "violations": [],
              "explanation": "The recent action prescribes Empagliflozin 10 mg orally once daily, which exactly matches the dosing protocol for Cohort B. No patient information is provided to evaluate the renal stratification requirement, so the action itself is compliant."
            },
            {
              "agent": "Safety & Toxicity Agent",
              "status": "SAFE",
              "verdict": "SAFE",
              "concerns": [],
              "iteration": 0,
              "confidence": 0.91,
              "explanation": "Patient's eGFR 58 mL/min/1.73m2 is above threshold for empagliflozin use (\u226545). No drug-drug interactions identified. Liver function normal. No safety concerns."
            },
            {
              "agent": "Financial Risk Agent",
              "status": "COVERED",
              "verdict": "COVERED",
              "iteration": 0,
              "confidence": 0.95,
              "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per the Clinical Trial Agreement and sponsor policy, this is 100% covered under the CTA with $0 patient liability. No prior authorization is required."
            },
            {
              "agent": "Arbitration Reducer",
              "status": "JUSTIFIED",
              "summary": "The prescribed Empagliflozin 10 mg daily matches the protocol for Cohort B. The patient's eGFR of 58 mL/min/1.73m\u00b2 exceeds the safety threshold of \u226545, and no drug interactions or safety concerns were identified. Financial coverage is 100% under the sponsor trial agreement with zero patient liability. All checks confirm the action is appropriate and safe.",
              "verdict": "JUSTIFIED",
              "iteration": 0,
              "explanation": "The prescribed Empagliflozin 10 mg daily matches the protocol for Cohort B. The patient's eGFR of 58 mL/min/1.73m\u00b2 exceeds the safety threshold of \u226545, and no drug interactions or safety concerns were identified. Financial coverage is 100% under the sponsor trial agreement with zero patient liability. All checks confirm the action is appropriate and safe."
            }
          ],
          "iteration_count": 0,
          "safety_evidence": [
            "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
          ],
          "financial_result": {
            "tier": "Tier-1 Investigational Coverage",
            "callout": "100% Protocol & Investigational Coverage under Sponsor Trial Agreement for Empagliflozin (Zero Patient Liability).",
            "patientId": "P001",
            "confidence": 0.95,
            "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per the Clinical Trial Agreement and sponsor policy, this is 100% covered under the CTA with $0 patient liability. No prior authorization is required.",
            "coverage_status": "COVERED",
            "financialExposure": 0,
            "pre_auth_required": false,
            "sponsor_billing_eligible": true
          },
          "protocol_evidence": [
            {
              "text": "Cohort B Standard Protocol: Empagliflozin 10 mg orally once daily. Patients on renal stratification require eGFR >= 30 mL/min/1.73m2.",
              "score": 0.95,
              "source": "ClinicalTrials.gov",
              "section": "dosing_protocol",
              "chunk_id": "NCT00699998-dosing-001",
              "trial_id": "NCT00699998"
            },
            {
              "text": "Dialysis or severe end-stage renal failure excludes participation.",
              "score": 0.92,
              "source": "ClinicalTrials.gov",
              "section": "eligibility",
              "chunk_id": "NCT00699998-eligibility-003",
              "trial_id": "NCT00699998"
            }
          ],
          "decision_timestamp": "2026-09-16T19:52:54.559Z",
          "clinician_justification": "Order rejected due to protocol non-compliance (40 mg BID exceeds 5 mg BID standard) and acute hemorrhage contraindication.",
          "final_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "original_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "protocol_compliance_result": {
            "valid": true,
            "sources": [
              "NCT00699998-dosing-001"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.9,
            "violations": [],
            "explanation": "The recent action prescribes Empagliflozin 10 mg orally once daily, which exactly matches the dosing protocol for Cohort B. No patient information is provided to evaluate the renal stratification requirement, so the action itself is compliant.",
            "compliance_status": "COMPLIANT",
            "needs_human_review": false
          }
        },
        {
          "summary": "The prescribed Empagliflozin 10 mg daily matches the protocol for Cohort B. The patient's eGFR of 58 mL/min/1.73m\u00b2 exceeds the safety threshold of \u226545, and no drug interactions or safety concerns were identified. Financial coverage is 100% under the sponsor trial agreement with zero patient liability. All checks confirm the action is appropriate and safe.",
          "saved_at": "2026-09-16T19:53:38.064840+00:00",
          "trial_id": "NCT00699998",
          "report_id": "6f408e8b-6c31-41aa-9bc2-eccfa39ff395",
          "patient_id": "P001",
          "protocol_id": "NCT00699998",
          "agent_metrics": {
            "Arbitration Reducer": {
              "confidence": 0.95,
              "latency_ms": 18022
            },
            "Financial Risk Agent": {
              "confidence": 0.95,
              "latency_ms": 5199
            },
            "Safety & Toxicity Agent": {
              "latency_ms": 7851
            },
            "Protocol Compliance Agent": {
              "latency_ms": 8567
            }
          },
          "final_verdict": "JUSTIFIED",
          "safety_result": {
            "safe": true,
            "concerns": [],
            "evidence": [
              "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.91,
            "patient_id": "P001",
            "explanation": "Patient's eGFR 58 mL/min/1.73m2 is above threshold for empagliflozin use (\u226545). No drug-drug interactions identified. Liver function normal. No safety concerns.",
            "safety_status": "SAFE",
            "needs_human_review": false
          },
          "final_decision": "reject",
          "report_history": [
            {
              "agent": "Protocol Compliance Agent",
              "status": "COMPLIANT",
              "verdict": "COMPLIANT",
              "iteration": 0,
              "confidence": 0.9,
              "violations": [],
              "explanation": "The recent action prescribes Empagliflozin 10 mg orally once daily, which exactly matches the dosing protocol for Cohort B. No patient information is provided to evaluate the renal stratification requirement, so the action itself is compliant."
            },
            {
              "agent": "Safety & Toxicity Agent",
              "status": "SAFE",
              "verdict": "SAFE",
              "concerns": [],
              "iteration": 0,
              "confidence": 0.91,
              "explanation": "Patient's eGFR 58 mL/min/1.73m2 is above threshold for empagliflozin use (\u226545). No drug-drug interactions identified. Liver function normal. No safety concerns."
            },
            {
              "agent": "Financial Risk Agent",
              "status": "COVERED",
              "verdict": "COVERED",
              "iteration": 0,
              "confidence": 0.95,
              "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per the Clinical Trial Agreement and sponsor policy, this is 100% covered under the CTA with $0 patient liability. No prior authorization is required."
            },
            {
              "agent": "Arbitration Reducer",
              "status": "JUSTIFIED",
              "summary": "The prescribed Empagliflozin 10 mg daily matches the protocol for Cohort B. The patient's eGFR of 58 mL/min/1.73m\u00b2 exceeds the safety threshold of \u226545, and no drug interactions or safety concerns were identified. Financial coverage is 100% under the sponsor trial agreement with zero patient liability. All checks confirm the action is appropriate and safe.",
              "verdict": "JUSTIFIED",
              "iteration": 0,
              "explanation": "The prescribed Empagliflozin 10 mg daily matches the protocol for Cohort B. The patient's eGFR of 58 mL/min/1.73m\u00b2 exceeds the safety threshold of \u226545, and no drug interactions or safety concerns were identified. Financial coverage is 100% under the sponsor trial agreement with zero patient liability. All checks confirm the action is appropriate and safe."
            }
          ],
          "iteration_count": 0,
          "safety_evidence": [
            "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
          ],
          "financial_result": {
            "tier": "Tier-1 Investigational Coverage",
            "callout": "100% Protocol & Investigational Coverage under Sponsor Trial Agreement for Empagliflozin (Zero Patient Liability).",
            "patientId": "P001",
            "confidence": 0.95,
            "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per the Clinical Trial Agreement and sponsor policy, this is 100% covered under the CTA with $0 patient liability. No prior authorization is required.",
            "coverage_status": "COVERED",
            "financialExposure": 0,
            "pre_auth_required": false,
            "sponsor_billing_eligible": true
          },
          "protocol_evidence": [
            {
              "text": "Cohort B Standard Protocol: Empagliflozin 10 mg orally once daily. Patients on renal stratification require eGFR >= 30 mL/min/1.73m2.",
              "score": 0.95,
              "source": "ClinicalTrials.gov",
              "section": "dosing_protocol",
              "chunk_id": "NCT00699998-dosing-001",
              "trial_id": "NCT00699998"
            },
            {
              "text": "Dialysis or severe end-stage renal failure excludes participation.",
              "score": 0.92,
              "source": "ClinicalTrials.gov",
              "section": "eligibility",
              "chunk_id": "NCT00699998-eligibility-003",
              "trial_id": "NCT00699998"
            }
          ],
          "decision_timestamp": "2026-09-16T19:53:38.051Z",
          "clinician_justification": "Order rejected due to protocol non-compliance (40 mg BID exceeds 5 mg BID standard) and acute hemorrhage contraindication.",
          "final_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "original_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "protocol_compliance_result": {
            "valid": true,
            "sources": [
              "NCT00699998-dosing-001"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.9,
            "violations": [],
            "explanation": "The recent action prescribes Empagliflozin 10 mg orally once daily, which exactly matches the dosing protocol for Cohort B. No patient information is provided to evaluate the renal stratification requirement, so the action itself is compliant.",
            "compliance_status": "COMPLIANT",
            "needs_human_review": false
          }
        },
        {
          "summary": "The prescribed Empagliflozin 10 mg daily matches the protocol for Cohort B. The patient's eGFR of 58 mL/min/1.73m\u00b2 exceeds the safety threshold of \u226545, and no drug interactions or safety concerns were identified. Financial coverage is 100% under the sponsor trial agreement with zero patient liability. All checks confirm the action is appropriate and safe.",
          "saved_at": "2026-09-16T19:53:38.769371+00:00",
          "trial_id": "NCT00699998",
          "report_id": "010eaf3e-abad-40ec-a00b-7e31d48500ad",
          "patient_id": "P001",
          "protocol_id": "NCT00699998",
          "agent_metrics": {
            "Arbitration Reducer": {
              "confidence": 0.95,
              "latency_ms": 18022
            },
            "Financial Risk Agent": {
              "confidence": 0.95,
              "latency_ms": 5199
            },
            "Safety & Toxicity Agent": {
              "latency_ms": 7851
            },
            "Protocol Compliance Agent": {
              "latency_ms": 8567
            }
          },
          "final_verdict": "JUSTIFIED",
          "safety_result": {
            "safe": true,
            "concerns": [],
            "evidence": [
              "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.91,
            "patient_id": "P001",
            "explanation": "Patient's eGFR 58 mL/min/1.73m2 is above threshold for empagliflozin use (\u226545). No drug-drug interactions identified. Liver function normal. No safety concerns.",
            "safety_status": "SAFE",
            "needs_human_review": false
          },
          "final_decision": "reject",
          "report_history": [
            {
              "agent": "Protocol Compliance Agent",
              "status": "COMPLIANT",
              "verdict": "COMPLIANT",
              "iteration": 0,
              "confidence": 0.9,
              "violations": [],
              "explanation": "The recent action prescribes Empagliflozin 10 mg orally once daily, which exactly matches the dosing protocol for Cohort B. No patient information is provided to evaluate the renal stratification requirement, so the action itself is compliant."
            },
            {
              "agent": "Safety & Toxicity Agent",
              "status": "SAFE",
              "verdict": "SAFE",
              "concerns": [],
              "iteration": 0,
              "confidence": 0.91,
              "explanation": "Patient's eGFR 58 mL/min/1.73m2 is above threshold for empagliflozin use (\u226545). No drug-drug interactions identified. Liver function normal. No safety concerns."
            },
            {
              "agent": "Financial Risk Agent",
              "status": "COVERED",
              "verdict": "COVERED",
              "iteration": 0,
              "confidence": 0.95,
              "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per the Clinical Trial Agreement and sponsor policy, this is 100% covered under the CTA with $0 patient liability. No prior authorization is required."
            },
            {
              "agent": "Arbitration Reducer",
              "status": "JUSTIFIED",
              "summary": "The prescribed Empagliflozin 10 mg daily matches the protocol for Cohort B. The patient's eGFR of 58 mL/min/1.73m\u00b2 exceeds the safety threshold of \u226545, and no drug interactions or safety concerns were identified. Financial coverage is 100% under the sponsor trial agreement with zero patient liability. All checks confirm the action is appropriate and safe.",
              "verdict": "JUSTIFIED",
              "iteration": 0,
              "explanation": "The prescribed Empagliflozin 10 mg daily matches the protocol for Cohort B. The patient's eGFR of 58 mL/min/1.73m\u00b2 exceeds the safety threshold of \u226545, and no drug interactions or safety concerns were identified. Financial coverage is 100% under the sponsor trial agreement with zero patient liability. All checks confirm the action is appropriate and safe."
            }
          ],
          "iteration_count": 0,
          "safety_evidence": [
            "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
          ],
          "financial_result": {
            "tier": "Tier-1 Investigational Coverage",
            "callout": "100% Protocol & Investigational Coverage under Sponsor Trial Agreement for Empagliflozin (Zero Patient Liability).",
            "patientId": "P001",
            "confidence": 0.95,
            "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per the Clinical Trial Agreement and sponsor policy, this is 100% covered under the CTA with $0 patient liability. No prior authorization is required.",
            "coverage_status": "COVERED",
            "financialExposure": 0,
            "pre_auth_required": false,
            "sponsor_billing_eligible": true
          },
          "protocol_evidence": [
            {
              "text": "Cohort B Standard Protocol: Empagliflozin 10 mg orally once daily. Patients on renal stratification require eGFR >= 30 mL/min/1.73m2.",
              "score": 0.95,
              "source": "ClinicalTrials.gov",
              "section": "dosing_protocol",
              "chunk_id": "NCT00699998-dosing-001",
              "trial_id": "NCT00699998"
            },
            {
              "text": "Dialysis or severe end-stage renal failure excludes participation.",
              "score": 0.92,
              "source": "ClinicalTrials.gov",
              "section": "eligibility",
              "chunk_id": "NCT00699998-eligibility-003",
              "trial_id": "NCT00699998"
            }
          ],
          "decision_timestamp": "2026-09-16T19:53:38.767Z",
          "clinician_justification": "Order rejected due to protocol non-compliance (40 mg BID exceeds 5 mg BID standard) and acute hemorrhage contraindication.",
          "final_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "original_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "protocol_compliance_result": {
            "valid": true,
            "sources": [
              "NCT00699998-dosing-001"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.9,
            "violations": [],
            "explanation": "The recent action prescribes Empagliflozin 10 mg orally once daily, which exactly matches the dosing protocol for Cohort B. No patient information is provided to evaluate the renal stratification requirement, so the action itself is compliant.",
            "compliance_status": "COMPLIANT",
            "needs_human_review": false
          }
        },
        {
          "summary": "The prescribed Empagliflozin 10 mg daily matches the protocol for Cohort B. The patient's eGFR of 58 mL/min/1.73m\u00b2 exceeds the safety threshold of \u226545, and no drug interactions or safety concerns were identified. Financial coverage is 100% under the sponsor trial agreement with zero patient liability. All checks confirm the action is appropriate and safe.",
          "saved_at": "2026-09-16T19:53:44.449813+00:00",
          "trial_id": "NCT00699998",
          "report_id": "e487d2b4-0d84-4797-a57e-5f9ee1263129",
          "patient_id": "P001",
          "protocol_id": "NCT00699998",
          "agent_metrics": {
            "Arbitration Reducer": {
              "confidence": 0.95,
              "latency_ms": 18022
            },
            "Financial Risk Agent": {
              "confidence": 0.95,
              "latency_ms": 5199
            },
            "Safety & Toxicity Agent": {
              "latency_ms": 7851
            },
            "Protocol Compliance Agent": {
              "latency_ms": 8567
            }
          },
          "final_verdict": "JUSTIFIED",
          "safety_result": {
            "safe": true,
            "concerns": [],
            "evidence": [
              "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.91,
            "patient_id": "P001",
            "explanation": "Patient's eGFR 58 mL/min/1.73m2 is above threshold for empagliflozin use (\u226545). No drug-drug interactions identified. Liver function normal. No safety concerns.",
            "safety_status": "SAFE",
            "needs_human_review": false
          },
          "final_decision": "accept",
          "report_history": [
            {
              "agent": "Protocol Compliance Agent",
              "status": "COMPLIANT",
              "verdict": "COMPLIANT",
              "iteration": 0,
              "confidence": 0.9,
              "violations": [],
              "explanation": "The recent action prescribes Empagliflozin 10 mg orally once daily, which exactly matches the dosing protocol for Cohort B. No patient information is provided to evaluate the renal stratification requirement, so the action itself is compliant."
            },
            {
              "agent": "Safety & Toxicity Agent",
              "status": "SAFE",
              "verdict": "SAFE",
              "concerns": [],
              "iteration": 0,
              "confidence": 0.91,
              "explanation": "Patient's eGFR 58 mL/min/1.73m2 is above threshold for empagliflozin use (\u226545). No drug-drug interactions identified. Liver function normal. No safety concerns."
            },
            {
              "agent": "Financial Risk Agent",
              "status": "COVERED",
              "verdict": "COVERED",
              "iteration": 0,
              "confidence": 0.95,
              "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per the Clinical Trial Agreement and sponsor policy, this is 100% covered under the CTA with $0 patient liability. No prior authorization is required."
            },
            {
              "agent": "Arbitration Reducer",
              "status": "JUSTIFIED",
              "summary": "The prescribed Empagliflozin 10 mg daily matches the protocol for Cohort B. The patient's eGFR of 58 mL/min/1.73m\u00b2 exceeds the safety threshold of \u226545, and no drug interactions or safety concerns were identified. Financial coverage is 100% under the sponsor trial agreement with zero patient liability. All checks confirm the action is appropriate and safe.",
              "verdict": "JUSTIFIED",
              "iteration": 0,
              "explanation": "The prescribed Empagliflozin 10 mg daily matches the protocol for Cohort B. The patient's eGFR of 58 mL/min/1.73m\u00b2 exceeds the safety threshold of \u226545, and no drug interactions or safety concerns were identified. Financial coverage is 100% under the sponsor trial agreement with zero patient liability. All checks confirm the action is appropriate and safe."
            }
          ],
          "iteration_count": 0,
          "safety_evidence": [
            "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
          ],
          "financial_result": {
            "tier": "Tier-1 Investigational Coverage",
            "callout": "100% Protocol & Investigational Coverage under Sponsor Trial Agreement for Empagliflozin (Zero Patient Liability).",
            "patientId": "P001",
            "confidence": 0.95,
            "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per the Clinical Trial Agreement and sponsor policy, this is 100% covered under the CTA with $0 patient liability. No prior authorization is required.",
            "coverage_status": "COVERED",
            "financialExposure": 0,
            "pre_auth_required": false,
            "sponsor_billing_eligible": true
          },
          "protocol_evidence": [
            {
              "text": "Cohort B Standard Protocol: Empagliflozin 10 mg orally once daily. Patients on renal stratification require eGFR >= 30 mL/min/1.73m2.",
              "score": 0.95,
              "source": "ClinicalTrials.gov",
              "section": "dosing_protocol",
              "chunk_id": "NCT00699998-dosing-001",
              "trial_id": "NCT00699998"
            },
            {
              "text": "Dialysis or severe end-stage renal failure excludes participation.",
              "score": 0.92,
              "source": "ClinicalTrials.gov",
              "section": "eligibility",
              "chunk_id": "NCT00699998-eligibility-003",
              "trial_id": "NCT00699998"
            }
          ],
          "decision_timestamp": "2026-09-16T19:53:44.445Z",
          "clinician_justification": "Order accepted and electronically co-signed by attending investigator per 21 CFR Part 11.",
          "final_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "original_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "protocol_compliance_result": {
            "valid": true,
            "sources": [
              "NCT00699998-dosing-001"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.9,
            "violations": [],
            "explanation": "The recent action prescribes Empagliflozin 10 mg orally once daily, which exactly matches the dosing protocol for Cohort B. No patient information is provided to evaluate the renal stratification requirement, so the action itself is compliant.",
            "compliance_status": "COMPLIANT",
            "needs_human_review": false
          }
        }
      ],
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "62-year-old male with diabetic nephropathy stage 3a and membranous nephropathy. Baseline renal function preserved with eGFR 58 mL/min/1.73m2. History of renal biopsy in 2019 confirming membranous nephropathy, and remote appendectomy.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P002",
    "name": "Sneha Deshpande",
    "dob": "1961-03-15",
    "age": 65,
    "sex": "F",
    "cohort": "Cohort A - Standard Protocol - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "Non-valvular atrial fibrillation",
    "creatinine": "CrCl 68.0 mL/min",
    "trial_id": "NCT00781573",
    "medications": [
      "Apixaban 5mg BID",
      "Clopidogrel 75mg daily",
      "Atorvastatin 40mg daily"
    ],
    "clinical_data": {
      "age": 65,
      "dob": "1961-03-15",
      "sex": "female",
      "cohort": "Cohort A - Standard Protocol",
      "status": "JUSTIFIED",
      "weight": 68.0,
      "fhir_id": "138792182",
      "allergies": [
        "None known"
      ],
      "diagnoses": [
        "Non-valvular atrial fibrillation",
        "Coronary artery disease post-PCI",
        "Essential hypertension"
      ],
      "birth_date": "1961-03-15",
      "patient_id": "P002",
      "ecog_status": 0,
      "internal_id": "P002",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 32.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4200.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.2
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 72.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 210000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.5
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.7
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 0.9
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 68.0
        }
      },
      "medications": [
        "Apixaban 5mg BID",
        "Clopidogrel 75mg daily",
        "Atorvastatin 40mg daily"
      ],
      "vital_signs": {
        "heart_rate": 78.0,
        "blood_pressure_systolic": 128,
        "blood_pressure_diastolic": 82
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": true,
        "breastfeeding": false,
        "days_since_PCI": 180,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": true,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": true,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "PCI (percutaneous coronary intervention) 6 months ago",
        "Appendectomy 10 years ago"
      ],
      "cardiac_function": {
        "QTc": 420.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "Palpitations",
        "Fatigue"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "adjudication_reports": [
        {
          "summary": null,
          "saved_at": "2026-09-16T19:49:17.150784+00:00",
          "trial_id": "NCT00781573",
          "report_id": "337be0b7-f5ab-463a-ae7c-377d98ee5cb7",
          "patient_id": "P002",
          "protocol_id": "NCT00781573",
          "agent_metrics": {},
          "final_verdict": null,
          "safety_result": {},
          "final_decision": "reject",
          "report_history": [],
          "iteration_count": 0,
          "safety_evidence": [],
          "financial_result": {},
          "protocol_evidence": [],
          "decision_timestamp": "2026-09-17T01:15:00Z",
          "clinician_justification": "Order rejected due to protocol non-compliance.",
          "final_prescribed_action": "Apixaban 5 mg oral twice daily",
          "original_prescribed_action": "Apixaban 5 mg oral twice daily",
          "protocol_compliance_result": {}
        }
      ],
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "A 65-year-old female with non-valvular atrial fibrillation and coronary artery disease status post PCI 6 months ago. She has essential hypertension and is currently on apixaban, clopidogrel, and atorvastatin. She has no prior bleeding or intracranial hemorrhage.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P003",
    "name": "Gurpreet Kaur Sandhu",
    "dob": "1972-03-15",
    "age": 54,
    "sex": "F",
    "cohort": "Cohort B - NAFLD Protocol - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "metabolic dysfunction-associated steatohepatitis (MASH)",
    "creatinine": "CrCl 80.0 mL/min",
    "trial_id": "NCT00809965",
    "medications": [
      "pioglitazone 30mg daily",
      "semaglutide 1.0mg weekly",
      "vitamin E 800 IU daily",
      "metformin 500mg twice daily"
    ],
    "clinical_data": {
      "age": 54,
      "dob": "1972-03-15",
      "sex": "female",
      "cohort": "Cohort B - NAFLD Protocol",
      "status": "JUSTIFIED",
      "weight": 72.0,
      "fhir_id": "138792240",
      "allergies": [
        "sulfa drugs"
      ],
      "diagnoses": [
        "metabolic dysfunction-associated steatohepatitis (MASH)",
        "type 2 diabetes mellitus",
        "hypertension"
      ],
      "birth_date": "1972-03-15",
      "patient_id": "P003",
      "ecog_status": 0,
      "internal_id": "P003",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 42.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4500.0
        },
        "AST": {
          "unit": "U/L",
          "value": 38.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.0
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 85.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 220000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.5
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.6
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 0.9
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 80.0
        }
      },
      "medications": [
        "pioglitazone 30mg daily",
        "semaglutide 1.0mg weekly",
        "vitamin E 800 IU daily",
        "metformin 500mg twice daily"
      ],
      "vital_signs": {
        "heart_rate": 76.0,
        "blood_pressure_systolic": 128,
        "blood_pressure_diastolic": 82
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 0,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "laparoscopic cholecystectomy (2018)",
        "diagnosis of hypertension (2015)"
      ],
      "cardiac_function": {
        "QTc": 420.0,
        "LVEF": 60.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "mild fatigue",
        "intermittent right upper quadrant discomfort"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "54-year-old female with metabolic dysfunction-associated steatohepatitis (MASH) and type 2 diabetes mellitus. She has a history of hypertension and underwent laparoscopic cholecystectomy in 2018. She is currently managed on pioglitazone, semaglutide, vitamin E, and metformin with stable liver enzymes.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P004",
    "name": "Kavita Shekhawat",
    "dob": "1964-03-15",
    "age": 62,
    "sex": "F",
    "cohort": "Cohort C - Solid Tumor Oncology - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "non-small cell lung cancer (stage IIIB)",
    "creatinine": "CrCl 65.0 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "pembrolizumab 200mg IV Q3W",
      "capecitabine 1000mg BID",
      "ondansetron 8mg PRN"
    ],
    "clinical_data": {
      "age": 62,
      "dob": "1964-03-15",
      "sex": "female",
      "cohort": "Cohort C - Solid Tumor Oncology",
      "status": "JUSTIFIED",
      "weight": 68.0,
      "fhir_id": "138792211",
      "allergies": [],
      "diagnoses": [
        "non-small cell lung cancer (stage IIIB)",
        "colorectal adenocarcinoma"
      ],
      "birth_date": "1964-03-15",
      "patient_id": "P004",
      "ecog_status": 1,
      "internal_id": "P004",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 28.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 3800.0
        },
        "AST": {
          "unit": "U/L",
          "value": 24.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 75.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 240000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.8
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.8
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.0
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 65.0
        }
      },
      "medications": [
        "pembrolizumab 200mg IV Q3W",
        "capecitabine 1000mg BID",
        "ondansetron 8mg PRN"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 0,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "Video-assisted thoracoscopic surgery (VATS) biopsy of lung lesion",
        "Port-a-cath insertion for chemotherapy",
        "Colonoscopy with polypectomy"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "fatigue",
        "intermittent cough"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "Kavita Shekhawat is a 62-year-old female with stage IIIB non-small cell lung cancer and concurrent colorectal adenocarcinoma. She underwent VATS biopsy for diagnosis and has a port-a-cath for systemic therapy. She is currently receiving pembrolizumab and capecitabine with supportive care.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P005",
    "name": "Ravi Paswan",
    "dob": "1964-03-15",
    "age": 62,
    "sex": "M",
    "cohort": "Cohort B - Renal Stratification - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "diabetic nephropathy stage 3a",
    "creatinine": "CrCl 50.0 mL/min",
    "trial_id": "NCT00699998",
    "medications": [
      "empagliflozin 10mg daily",
      "losartan 50mg daily",
      "torsemide 10mg daily"
    ],
    "clinical_data": {
      "age": 62,
      "dob": "1964-03-15",
      "sex": "male",
      "cohort": "Cohort B - Renal Stratification",
      "status": "JUSTIFIED",
      "weight": 72.0,
      "fhir_id": "138792202",
      "allergies": [],
      "diagnoses": [
        "diabetic nephropathy stage 3a",
        "membranous nephropathy"
      ],
      "birth_date": "1964-03-15",
      "patient_id": "P005",
      "ecog_status": 0,
      "internal_id": "P005",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 32.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4500.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 65.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 240000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 12.5
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.7
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.2
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 50.0
        }
      },
      "medications": [
        "empagliflozin 10mg daily",
        "losartan 50mg daily",
        "torsemide 10mg daily"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 135,
        "blood_pressure_diastolic": 85
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 0,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "renal biopsy (2 years ago)",
        "appendectomy (30 years ago)",
        "hypertension (diagnosed 10 years ago)"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "lower extremity edema",
        "fatigue"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "Patient with long-standing type 2 diabetes and hypertension, diagnosed with diabetic nephropathy and membranous nephropathy. He underwent renal biopsy 2 years ago confirming membranous nephropathy. He is on SGLT2 inhibitor and ARB for renal protection.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P006",
    "name": "Yarlagadda Surya Narayana",
    "dob": "1958-03-15",
    "age": 68,
    "sex": "M",
    "cohort": "Cohort A - Standard Protocol - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "Non-valvular atrial fibrillation",
    "creatinine": "CrCl 65.0 mL/min",
    "trial_id": "NCT00781573",
    "medications": [
      "Apixaban 5mg BID",
      "Clopidogrel 75mg daily",
      "Atorvastatin 40mg daily"
    ],
    "clinical_data": {
      "age": 68,
      "dob": "1958-03-15",
      "sex": "male",
      "cohort": "Cohort A - Standard Protocol",
      "status": "JUSTIFIED",
      "weight": 80.0,
      "fhir_id": "138792391",
      "allergies": [
        "None known"
      ],
      "diagnoses": [
        "Non-valvular atrial fibrillation",
        "Coronary artery disease post-PCI",
        "Essential hypertension"
      ],
      "birth_date": "1958-03-15",
      "patient_id": "P006",
      "ecog_status": 0,
      "internal_id": "P006",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 28.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 3800.0
        },
        "AST": {
          "unit": "U/L",
          "value": 24.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 75.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 240000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.8
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.8
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.0
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 65.0
        }
      },
      "medications": [
        "Apixaban 5mg BID",
        "Clopidogrel 75mg daily",
        "Atorvastatin 40mg daily"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": true,
        "pci_pathway": true,
        "breastfeeding": false,
        "days_since_PCI": 60,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": true,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": 60,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": true,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "Percutaneous coronary intervention (PCI) with drug-eluting stent to left anterior descending artery 6 months ago",
        "Appendectomy 10 years ago"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "None"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "Patient is a 68-year-old male with non-valvular atrial fibrillation and coronary artery disease status post-PCI. He has essential hypertension and is on triple antithrombotic therapy with apixaban, clopidogrel, and atorvastatin. No history of bleeding or intracranial hemorrhage.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P007",
    "name": "Monalisha Hazarika",
    "dob": "1971-03-15",
    "age": 55,
    "sex": "F",
    "cohort": "Cohort B - NAFLD Protocol - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "Metabolic dysfunction-associated steatohepatitis (MASH)",
    "creatinine": "CrCl 65.0 mL/min",
    "trial_id": "NCT00809965",
    "medications": [
      "pioglitazone 30mg daily",
      "semaglutide 1.0mg weekly",
      "vitamin E 800 IU daily"
    ],
    "clinical_data": {
      "age": 55,
      "dob": "1971-03-15",
      "sex": "female",
      "cohort": "Cohort B - NAFLD Protocol",
      "status": "JUSTIFIED",
      "weight": 68.0,
      "fhir_id": "138792261",
      "allergies": [
        "none"
      ],
      "diagnoses": [
        "Metabolic dysfunction-associated steatohepatitis (MASH)",
        "Type 2 diabetes mellitus"
      ],
      "birth_date": "1971-03-15",
      "patient_id": "P007",
      "ecog_status": 0,
      "internal_id": "P007",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 38.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 3800.0
        },
        "AST": {
          "unit": "U/L",
          "value": 34.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 75.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 240000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.8
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.8
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.0
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 65.0
        }
      },
      "medications": [
        "pioglitazone 30mg daily",
        "semaglutide 1.0mg weekly",
        "vitamin E 800 IU daily"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "Cholecystectomy (12 years ago)",
        "Laparoscopic adjustable gastric banding (8 years ago)"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "Fatigue",
        "Right upper quadrant discomfort"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "55-year-old female with metabolic dysfunction-associated steatohepatitis and type 2 diabetes mellitus. She underwent cholecystectomy 12 years ago and laparoscopic adjustable gastric banding 8 years ago for obesity. Current symptoms include fatigue and mild right upper quadrant discomfort.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P008",
    "name": "Smita Bandyopadhyay",
    "dob": "1964-03-15",
    "age": 62,
    "sex": "F",
    "cohort": "Cohort C - Solid Tumor Oncology - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "Non-small cell lung cancer (stage IIIB)",
    "creatinine": "CrCl 68.0 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "Pembrolizumab 200mg IV Q3W",
      "Capecitabine 1000mg BID",
      "Ondansetron 8mg PRN"
    ],
    "clinical_data": {
      "age": 62,
      "dob": "1964-03-15",
      "sex": "female",
      "cohort": "Cohort C - Solid Tumor Oncology",
      "status": "JUSTIFIED",
      "weight": 68.0,
      "fhir_id": "138792279",
      "allergies": [],
      "diagnoses": [
        "Non-small cell lung cancer (stage IIIB)",
        "Colorectal adenocarcinoma"
      ],
      "birth_date": "1964-03-15",
      "patient_id": "P008",
      "ecog_status": 0,
      "internal_id": "P008",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 32.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4200.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 78.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 250000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 12.5
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.7
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 0.9
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 68.0
        }
      },
      "medications": [
        "Pembrolizumab 200mg IV Q3W",
        "Capecitabine 1000mg BID",
        "Ondansetron 8mg PRN"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 0,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "Laparoscopic right hemicolectomy for colorectal adenocarcinoma (2019)",
        "CT-guided lung biopsy (2021)"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "62-year-old female with stage IIIB non-small cell lung cancer and history of colorectal adenocarcinoma post right hemicolectomy. Currently on pembrolizumab and capecitabine with good tolerance. ECOG status 0, no significant comorbidities.",
      "last_systemic_therapy_date": "2023-10-15"
    }
  },
  {
    "id": "P009",
    "name": "P. N. Menachery",
    "dob": "1962-03-15",
    "age": 64,
    "sex": "M",
    "cohort": "Cohort B - Renal Stratification - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "diabetic nephropathy stage 3a",
    "creatinine": "CrCl 55.0 mL/min",
    "trial_id": "NCT00699998",
    "medications": [
      "empagliflozin 10mg daily",
      "losartan 50mg daily",
      "torsemide 10mg daily"
    ],
    "clinical_data": {
      "age": 64,
      "dob": "1962-03-15",
      "sex": "male",
      "cohort": "Cohort B - Renal Stratification",
      "status": "JUSTIFIED",
      "weight": 72.0,
      "fhir_id": "138792306",
      "allergies": [],
      "diagnoses": [
        "diabetic nephropathy stage 3a",
        "membranous nephropathy"
      ],
      "birth_date": "1962-03-15",
      "patient_id": "P009",
      "ecog_status": 0,
      "internal_id": "P009",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 32.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 3800.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 52.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 240000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 12.5
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.8
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.3
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 55.0
        }
      },
      "medications": [
        "empagliflozin 10mg daily",
        "losartan 50mg daily",
        "torsemide 10mg daily"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 130,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 0,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "renal biopsy",
        "appendectomy",
        "hypertension diagnosed 10 years ago"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "edema",
        "fatigue"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "adjudication_reports": [
        {
          "summary": "All three assessments (protocol compliance, safety, and financial coverage) are favorable with high confidence. The patient meets inclusion criteria, empagliflozin 10 mg is safe given eGFR 52 mL/min/1.73m\u00b2, and the intervention is fully covered under the trial agreement. No violations, safety concerns, or financial liability are present.",
          "saved_at": "2026-09-17T01:47:26.381056+00:00",
          "trial_id": "NCT00699998",
          "report_id": "5ce3da23-265e-4979-a702-5c6c245a1b62",
          "patient_id": "P009",
          "protocol_id": "NCT00699998",
          "agent_metrics": {
            "Arbitration Reducer": {
              "confidence": 0.95,
              "latency_ms": 1636
            },
            "Financial Risk Agent": {
              "confidence": 0.95,
              "latency_ms": 7389
            },
            "Safety & Toxicity Agent": {
              "latency_ms": 8002
            },
            "Protocol Compliance Agent": {
              "latency_ms": 7391
            }
          },
          "final_verdict": "JUSTIFIED",
          "safety_result": {
            "safe": true,
            "concerns": [],
            "evidence": [
              "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.91,
            "patient_id": "P009",
            "explanation": "Empagliflozin 10 mg once daily is appropriate for this patient. eGFR 52 mL/min/1.73m2 is above the threshold for dose adjustment (typically <45 for glycemic indication, but renal benefit indication allows use down to eGFR 30). No drug-drug interactions with losartan or torsemide beyond standard monitoring for volume depletion. Liver function and other labs are within normal limits. No safety concerns identified.",
            "safety_status": "SAFE",
            "needs_human_review": false
          },
          "final_decision": "accept",
          "report_history": [
            {
              "agent": "Protocol Compliance Agent",
              "status": "COMPLIANT",
              "verdict": "COMPLIANT",
              "iteration": 0,
              "confidence": 0.9,
              "violations": [],
              "explanation": "Intervention complies with protocol NCT00699998 standard trial inclusion criteria."
            },
            {
              "agent": "Safety & Toxicity Agent",
              "status": "SAFE",
              "verdict": "SAFE",
              "concerns": [],
              "iteration": 0,
              "confidence": 0.91,
              "explanation": "Empagliflozin 10 mg once daily is appropriate for this patient. eGFR 52 mL/min/1.73m2 is above the threshold for dose adjustment (typically <45 for glycemic indication, but renal benefit indication allows use down to eGFR 30). No drug-drug interactions with losartan or torsemide beyond standard monitoring for volume depletion. Liver function and other labs are within normal limits. No safety concerns identified."
            },
            {
              "agent": "Financial Risk Agent",
              "status": "COVERED",
              "verdict": "COVERED",
              "iteration": 0,
              "confidence": 0.95,
              "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per sponsor clinical trial agreement, this is 100% covered with $0 patient liability. No prior authorization required."
            },
            {
              "agent": "Arbitration Reducer",
              "status": "JUSTIFIED",
              "summary": "All three assessments (protocol compliance, safety, and financial coverage) are favorable with high confidence. The patient meets inclusion criteria, empagliflozin 10 mg is safe given eGFR 52 mL/min/1.73m\u00b2, and the intervention is fully covered under the trial agreement. No violations, safety concerns, or financial liability are present.",
              "verdict": "JUSTIFIED",
              "iteration": 0,
              "explanation": "All three assessments (protocol compliance, safety, and financial coverage) are favorable with high confidence. The patient meets inclusion criteria, empagliflozin 10 mg is safe given eGFR 52 mL/min/1.73m\u00b2, and the intervention is fully covered under the trial agreement. No violations, safety concerns, or financial liability are present."
            }
          ],
          "iteration_count": 0,
          "safety_evidence": [
            "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
          ],
          "financial_result": {
            "tier": "Tier-1 Investigational Coverage",
            "callout": "100% Protocol & Investigational Coverage under Sponsor Trial Agreement for Empagliflozin (Zero Patient Liability).",
            "patientId": "P009",
            "confidence": 0.95,
            "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per sponsor clinical trial agreement, this is 100% covered with $0 patient liability. No prior authorization required.",
            "coverage_status": "COVERED",
            "financialExposure": 0,
            "pre_auth_required": false,
            "sponsor_billing_eligible": true
          },
          "protocol_evidence": [
            {
              "text": "Cohort B Standard Protocol: Empagliflozin 10 mg orally once daily. Patients on renal stratification require eGFR >= 30 mL/min/1.73m2.",
              "score": 0.95,
              "source": "ClinicalTrials.gov",
              "section": "dosing_protocol",
              "chunk_id": "NCT00699998-dosing-001",
              "trial_id": "NCT00699998"
            },
            {
              "text": "Dialysis or severe end-stage renal failure excludes participation.",
              "score": 0.92,
              "source": "ClinicalTrials.gov",
              "section": "eligibility",
              "chunk_id": "NCT00699998-eligibility-003",
              "trial_id": "NCT00699998"
            }
          ],
          "decision_timestamp": "2026-09-17T01:47:26.316Z",
          "clinician_justification": "Order accepted and electronically co-signed by attending investigator per 21 CFR Part 11.",
          "final_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "original_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "protocol_compliance_result": {
            "valid": true,
            "sources": [
              "ClinicalTrials.gov Protocol NCT00699998"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.9,
            "violations": [],
            "explanation": "Intervention complies with protocol NCT00699998 standard trial inclusion criteria.",
            "compliance_status": "COMPLIANT",
            "needs_human_review": false
          }
        },
        {
          "summary": "All three assessments (protocol compliance, safety, and financial coverage) are favorable with high confidence. The patient meets inclusion criteria, empagliflozin 10 mg is safe given eGFR 52 mL/min/1.73m\u00b2, and the intervention is fully covered under the trial agreement. No violations, safety concerns, or financial liability are present.",
          "saved_at": "2026-09-17T01:47:40.170051+00:00",
          "trial_id": "NCT00699998",
          "report_id": "06c8d36b-8b46-47f0-84b9-8c2cf4e816e4",
          "patient_id": "P009",
          "protocol_id": "NCT00699998",
          "agent_metrics": {
            "Arbitration Reducer": {
              "confidence": 0.95,
              "latency_ms": 1636
            },
            "Financial Risk Agent": {
              "confidence": 0.95,
              "latency_ms": 7389
            },
            "Safety & Toxicity Agent": {
              "latency_ms": 8002
            },
            "Protocol Compliance Agent": {
              "latency_ms": 7391
            }
          },
          "final_verdict": "JUSTIFIED",
          "safety_result": {
            "safe": true,
            "concerns": [],
            "evidence": [
              "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.91,
            "patient_id": "P009",
            "explanation": "Empagliflozin 10 mg once daily is appropriate for this patient. eGFR 52 mL/min/1.73m2 is above the threshold for dose adjustment (typically <45 for glycemic indication, but renal benefit indication allows use down to eGFR 30). No drug-drug interactions with losartan or torsemide beyond standard monitoring for volume depletion. Liver function and other labs are within normal limits. No safety concerns identified.",
            "safety_status": "SAFE",
            "needs_human_review": false
          },
          "final_decision": "reject",
          "report_history": [
            {
              "agent": "Protocol Compliance Agent",
              "status": "COMPLIANT",
              "verdict": "COMPLIANT",
              "iteration": 0,
              "confidence": 0.9,
              "violations": [],
              "explanation": "Intervention complies with protocol NCT00699998 standard trial inclusion criteria."
            },
            {
              "agent": "Safety & Toxicity Agent",
              "status": "SAFE",
              "verdict": "SAFE",
              "concerns": [],
              "iteration": 0,
              "confidence": 0.91,
              "explanation": "Empagliflozin 10 mg once daily is appropriate for this patient. eGFR 52 mL/min/1.73m2 is above the threshold for dose adjustment (typically <45 for glycemic indication, but renal benefit indication allows use down to eGFR 30). No drug-drug interactions with losartan or torsemide beyond standard monitoring for volume depletion. Liver function and other labs are within normal limits. No safety concerns identified."
            },
            {
              "agent": "Financial Risk Agent",
              "status": "COVERED",
              "verdict": "COVERED",
              "iteration": 0,
              "confidence": 0.95,
              "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per sponsor clinical trial agreement, this is 100% covered with $0 patient liability. No prior authorization required."
            },
            {
              "agent": "Arbitration Reducer",
              "status": "JUSTIFIED",
              "summary": "All three assessments (protocol compliance, safety, and financial coverage) are favorable with high confidence. The patient meets inclusion criteria, empagliflozin 10 mg is safe given eGFR 52 mL/min/1.73m\u00b2, and the intervention is fully covered under the trial agreement. No violations, safety concerns, or financial liability are present.",
              "verdict": "JUSTIFIED",
              "iteration": 0,
              "explanation": "All three assessments (protocol compliance, safety, and financial coverage) are favorable with high confidence. The patient meets inclusion criteria, empagliflozin 10 mg is safe given eGFR 52 mL/min/1.73m\u00b2, and the intervention is fully covered under the trial agreement. No violations, safety concerns, or financial liability are present."
            }
          ],
          "iteration_count": 0,
          "safety_evidence": [
            "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
          ],
          "financial_result": {
            "tier": "Tier-1 Investigational Coverage",
            "callout": "100% Protocol & Investigational Coverage under Sponsor Trial Agreement for Empagliflozin (Zero Patient Liability).",
            "patientId": "P009",
            "confidence": 0.95,
            "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per sponsor clinical trial agreement, this is 100% covered with $0 patient liability. No prior authorization required.",
            "coverage_status": "COVERED",
            "financialExposure": 0,
            "pre_auth_required": false,
            "sponsor_billing_eligible": true
          },
          "protocol_evidence": [
            {
              "text": "Cohort B Standard Protocol: Empagliflozin 10 mg orally once daily. Patients on renal stratification require eGFR >= 30 mL/min/1.73m2.",
              "score": 0.95,
              "source": "ClinicalTrials.gov",
              "section": "dosing_protocol",
              "chunk_id": "NCT00699998-dosing-001",
              "trial_id": "NCT00699998"
            },
            {
              "text": "Dialysis or severe end-stage renal failure excludes participation.",
              "score": 0.92,
              "source": "ClinicalTrials.gov",
              "section": "eligibility",
              "chunk_id": "NCT00699998-eligibility-003",
              "trial_id": "NCT00699998"
            }
          ],
          "decision_timestamp": "2026-09-17T01:47:40.165Z",
          "clinician_justification": "Order rejected due to protocol non-compliance (40 mg BID exceeds 5 mg BID standard) and acute hemorrhage contraindication.",
          "final_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "original_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "protocol_compliance_result": {
            "valid": true,
            "sources": [
              "ClinicalTrials.gov Protocol NCT00699998"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.9,
            "violations": [],
            "explanation": "Intervention complies with protocol NCT00699998 standard trial inclusion criteria.",
            "compliance_status": "COMPLIANT",
            "needs_human_review": false
          }
        },
        {
          "summary": "All three assessments (protocol compliance, safety, and financial coverage) are favorable with high confidence. The patient meets inclusion criteria, empagliflozin 10 mg is safe given eGFR 52 mL/min/1.73m\u00b2, and the intervention is fully covered under the trial agreement. No violations, safety concerns, or financial liability are present.",
          "saved_at": "2026-09-17T01:47:47.836377+00:00",
          "trial_id": "NCT00699998",
          "report_id": "0d30e051-c502-4b04-8220-15cbcad6314d",
          "patient_id": "P009",
          "protocol_id": "NCT00699998",
          "agent_metrics": {
            "Arbitration Reducer": {
              "confidence": 0.95,
              "latency_ms": 1636
            },
            "Financial Risk Agent": {
              "confidence": 0.95,
              "latency_ms": 7389
            },
            "Safety & Toxicity Agent": {
              "latency_ms": 8002
            },
            "Protocol Compliance Agent": {
              "latency_ms": 7391
            }
          },
          "final_verdict": "JUSTIFIED",
          "safety_result": {
            "safe": true,
            "concerns": [],
            "evidence": [
              "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.91,
            "patient_id": "P009",
            "explanation": "Empagliflozin 10 mg once daily is appropriate for this patient. eGFR 52 mL/min/1.73m2 is above the threshold for dose adjustment (typically <45 for glycemic indication, but renal benefit indication allows use down to eGFR 30). No drug-drug interactions with losartan or torsemide beyond standard monitoring for volume depletion. Liver function and other labs are within normal limits. No safety concerns identified.",
            "safety_status": "SAFE",
            "needs_human_review": false
          },
          "final_decision": "reject",
          "report_history": [
            {
              "agent": "Protocol Compliance Agent",
              "status": "COMPLIANT",
              "verdict": "COMPLIANT",
              "iteration": 0,
              "confidence": 0.9,
              "violations": [],
              "explanation": "Intervention complies with protocol NCT00699998 standard trial inclusion criteria."
            },
            {
              "agent": "Safety & Toxicity Agent",
              "status": "SAFE",
              "verdict": "SAFE",
              "concerns": [],
              "iteration": 0,
              "confidence": 0.91,
              "explanation": "Empagliflozin 10 mg once daily is appropriate for this patient. eGFR 52 mL/min/1.73m2 is above the threshold for dose adjustment (typically <45 for glycemic indication, but renal benefit indication allows use down to eGFR 30). No drug-drug interactions with losartan or torsemide beyond standard monitoring for volume depletion. Liver function and other labs are within normal limits. No safety concerns identified."
            },
            {
              "agent": "Financial Risk Agent",
              "status": "COVERED",
              "verdict": "COVERED",
              "iteration": 0,
              "confidence": 0.95,
              "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per sponsor clinical trial agreement, this is 100% covered with $0 patient liability. No prior authorization required."
            },
            {
              "agent": "Arbitration Reducer",
              "status": "JUSTIFIED",
              "summary": "All three assessments (protocol compliance, safety, and financial coverage) are favorable with high confidence. The patient meets inclusion criteria, empagliflozin 10 mg is safe given eGFR 52 mL/min/1.73m\u00b2, and the intervention is fully covered under the trial agreement. No violations, safety concerns, or financial liability are present.",
              "verdict": "JUSTIFIED",
              "iteration": 0,
              "explanation": "All three assessments (protocol compliance, safety, and financial coverage) are favorable with high confidence. The patient meets inclusion criteria, empagliflozin 10 mg is safe given eGFR 52 mL/min/1.73m\u00b2, and the intervention is fully covered under the trial agreement. No violations, safety concerns, or financial liability are present."
            }
          ],
          "iteration_count": 0,
          "safety_evidence": [
            "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
          ],
          "financial_result": {
            "tier": "Tier-1 Investigational Coverage",
            "callout": "100% Protocol & Investigational Coverage under Sponsor Trial Agreement for Empagliflozin (Zero Patient Liability).",
            "patientId": "P009",
            "confidence": 0.95,
            "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per sponsor clinical trial agreement, this is 100% covered with $0 patient liability. No prior authorization required.",
            "coverage_status": "COVERED",
            "financialExposure": 0,
            "pre_auth_required": false,
            "sponsor_billing_eligible": true
          },
          "protocol_evidence": [
            {
              "text": "Cohort B Standard Protocol: Empagliflozin 10 mg orally once daily. Patients on renal stratification require eGFR >= 30 mL/min/1.73m2.",
              "score": 0.95,
              "source": "ClinicalTrials.gov",
              "section": "dosing_protocol",
              "chunk_id": "NCT00699998-dosing-001",
              "trial_id": "NCT00699998"
            },
            {
              "text": "Dialysis or severe end-stage renal failure excludes participation.",
              "score": 0.92,
              "source": "ClinicalTrials.gov",
              "section": "eligibility",
              "chunk_id": "NCT00699998-eligibility-003",
              "trial_id": "NCT00699998"
            }
          ],
          "decision_timestamp": "2026-09-17T01:47:47.834Z",
          "clinician_justification": "Order rejected due to protocol non-compliance (40 mg BID exceeds 5 mg BID standard) and acute hemorrhage contraindication.",
          "final_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "original_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "protocol_compliance_result": {
            "valid": true,
            "sources": [
              "ClinicalTrials.gov Protocol NCT00699998"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.9,
            "violations": [],
            "explanation": "Intervention complies with protocol NCT00699998 standard trial inclusion criteria.",
            "compliance_status": "COMPLIANT",
            "needs_human_review": false
          }
        },
        {
          "summary": "All three assessments (protocol compliance, safety, and financial coverage) are favorable with high confidence. The patient meets inclusion criteria, empagliflozin 10 mg is safe given eGFR 52 mL/min/1.73m\u00b2, and the intervention is fully covered under the trial agreement. No violations, safety concerns, or financial liability are present.",
          "saved_at": "2026-09-17T01:47:49.803795+00:00",
          "trial_id": "NCT00699998",
          "report_id": "039a82b2-2607-4e73-a832-549943c5ffcb",
          "patient_id": "P009",
          "protocol_id": "NCT00699998",
          "agent_metrics": {
            "Arbitration Reducer": {
              "confidence": 0.95,
              "latency_ms": 1636
            },
            "Financial Risk Agent": {
              "confidence": 0.95,
              "latency_ms": 7389
            },
            "Safety & Toxicity Agent": {
              "latency_ms": 8002
            },
            "Protocol Compliance Agent": {
              "latency_ms": 7391
            }
          },
          "final_verdict": "JUSTIFIED",
          "safety_result": {
            "safe": true,
            "concerns": [],
            "evidence": [
              "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.91,
            "patient_id": "P009",
            "explanation": "Empagliflozin 10 mg once daily is appropriate for this patient. eGFR 52 mL/min/1.73m2 is above the threshold for dose adjustment (typically <45 for glycemic indication, but renal benefit indication allows use down to eGFR 30). No drug-drug interactions with losartan or torsemide beyond standard monitoring for volume depletion. Liver function and other labs are within normal limits. No safety concerns identified.",
            "safety_status": "SAFE",
            "needs_human_review": false
          },
          "final_decision": "reject",
          "report_history": [
            {
              "agent": "Protocol Compliance Agent",
              "status": "COMPLIANT",
              "verdict": "COMPLIANT",
              "iteration": 0,
              "confidence": 0.9,
              "violations": [],
              "explanation": "Intervention complies with protocol NCT00699998 standard trial inclusion criteria."
            },
            {
              "agent": "Safety & Toxicity Agent",
              "status": "SAFE",
              "verdict": "SAFE",
              "concerns": [],
              "iteration": 0,
              "confidence": 0.91,
              "explanation": "Empagliflozin 10 mg once daily is appropriate for this patient. eGFR 52 mL/min/1.73m2 is above the threshold for dose adjustment (typically <45 for glycemic indication, but renal benefit indication allows use down to eGFR 30). No drug-drug interactions with losartan or torsemide beyond standard monitoring for volume depletion. Liver function and other labs are within normal limits. No safety concerns identified."
            },
            {
              "agent": "Financial Risk Agent",
              "status": "COVERED",
              "verdict": "COVERED",
              "iteration": 0,
              "confidence": 0.95,
              "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per sponsor clinical trial agreement, this is 100% covered with $0 patient liability. No prior authorization required."
            },
            {
              "agent": "Arbitration Reducer",
              "status": "JUSTIFIED",
              "summary": "All three assessments (protocol compliance, safety, and financial coverage) are favorable with high confidence. The patient meets inclusion criteria, empagliflozin 10 mg is safe given eGFR 52 mL/min/1.73m\u00b2, and the intervention is fully covered under the trial agreement. No violations, safety concerns, or financial liability are present.",
              "verdict": "JUSTIFIED",
              "iteration": 0,
              "explanation": "All three assessments (protocol compliance, safety, and financial coverage) are favorable with high confidence. The patient meets inclusion criteria, empagliflozin 10 mg is safe given eGFR 52 mL/min/1.73m\u00b2, and the intervention is fully covered under the trial agreement. No violations, safety concerns, or financial liability are present."
            }
          ],
          "iteration_count": 0,
          "safety_evidence": [
            "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
          ],
          "financial_result": {
            "tier": "Tier-1 Investigational Coverage",
            "callout": "100% Protocol & Investigational Coverage under Sponsor Trial Agreement for Empagliflozin (Zero Patient Liability).",
            "patientId": "P009",
            "confidence": 0.95,
            "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per sponsor clinical trial agreement, this is 100% covered with $0 patient liability. No prior authorization required.",
            "coverage_status": "COVERED",
            "financialExposure": 0,
            "pre_auth_required": false,
            "sponsor_billing_eligible": true
          },
          "protocol_evidence": [
            {
              "text": "Cohort B Standard Protocol: Empagliflozin 10 mg orally once daily. Patients on renal stratification require eGFR >= 30 mL/min/1.73m2.",
              "score": 0.95,
              "source": "ClinicalTrials.gov",
              "section": "dosing_protocol",
              "chunk_id": "NCT00699998-dosing-001",
              "trial_id": "NCT00699998"
            },
            {
              "text": "Dialysis or severe end-stage renal failure excludes participation.",
              "score": 0.92,
              "source": "ClinicalTrials.gov",
              "section": "eligibility",
              "chunk_id": "NCT00699998-eligibility-003",
              "trial_id": "NCT00699998"
            }
          ],
          "decision_timestamp": "2026-09-17T01:47:49.798Z",
          "clinician_justification": "Order rejected due to protocol non-compliance (40 mg BID exceeds 5 mg BID standard) and acute hemorrhage contraindication.",
          "final_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "original_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "protocol_compliance_result": {
            "valid": true,
            "sources": [
              "ClinicalTrials.gov Protocol NCT00699998"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.9,
            "violations": [],
            "explanation": "Intervention complies with protocol NCT00699998 standard trial inclusion criteria.",
            "compliance_status": "COMPLIANT",
            "needs_human_review": false
          }
        },
        {
          "summary": "All three assessments (protocol compliance, safety, and financial coverage) are favorable with high confidence. The patient meets inclusion criteria, empagliflozin 10 mg is safe given eGFR 52 mL/min/1.73m\u00b2, and the intervention is fully covered under the trial agreement. No violations, safety concerns, or financial liability are present.",
          "saved_at": "2026-09-17T01:47:51.545921+00:00",
          "trial_id": "NCT00699998",
          "report_id": "16de4dfc-8961-4067-9b36-813f1efbae6e",
          "patient_id": "P009",
          "protocol_id": "NCT00699998",
          "agent_metrics": {
            "Arbitration Reducer": {
              "confidence": 0.95,
              "latency_ms": 1636
            },
            "Financial Risk Agent": {
              "confidence": 0.95,
              "latency_ms": 7389
            },
            "Safety & Toxicity Agent": {
              "latency_ms": 8002
            },
            "Protocol Compliance Agent": {
              "latency_ms": 7391
            }
          },
          "final_verdict": "JUSTIFIED",
          "safety_result": {
            "safe": true,
            "concerns": [],
            "evidence": [
              "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.91,
            "patient_id": "P009",
            "explanation": "Empagliflozin 10 mg once daily is appropriate for this patient. eGFR 52 mL/min/1.73m2 is above the threshold for dose adjustment (typically <45 for glycemic indication, but renal benefit indication allows use down to eGFR 30). No drug-drug interactions with losartan or torsemide beyond standard monitoring for volume depletion. Liver function and other labs are within normal limits. No safety concerns identified.",
            "safety_status": "SAFE",
            "needs_human_review": false
          },
          "final_decision": "accept",
          "report_history": [
            {
              "agent": "Protocol Compliance Agent",
              "status": "COMPLIANT",
              "verdict": "COMPLIANT",
              "iteration": 0,
              "confidence": 0.9,
              "violations": [],
              "explanation": "Intervention complies with protocol NCT00699998 standard trial inclusion criteria."
            },
            {
              "agent": "Safety & Toxicity Agent",
              "status": "SAFE",
              "verdict": "SAFE",
              "concerns": [],
              "iteration": 0,
              "confidence": 0.91,
              "explanation": "Empagliflozin 10 mg once daily is appropriate for this patient. eGFR 52 mL/min/1.73m2 is above the threshold for dose adjustment (typically <45 for glycemic indication, but renal benefit indication allows use down to eGFR 30). No drug-drug interactions with losartan or torsemide beyond standard monitoring for volume depletion. Liver function and other labs are within normal limits. No safety concerns identified."
            },
            {
              "agent": "Financial Risk Agent",
              "status": "COVERED",
              "verdict": "COVERED",
              "iteration": 0,
              "confidence": 0.95,
              "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per sponsor clinical trial agreement, this is 100% covered with $0 patient liability. No prior authorization required."
            },
            {
              "agent": "Arbitration Reducer",
              "status": "JUSTIFIED",
              "summary": "All three assessments (protocol compliance, safety, and financial coverage) are favorable with high confidence. The patient meets inclusion criteria, empagliflozin 10 mg is safe given eGFR 52 mL/min/1.73m\u00b2, and the intervention is fully covered under the trial agreement. No violations, safety concerns, or financial liability are present.",
              "verdict": "JUSTIFIED",
              "iteration": 0,
              "explanation": "All three assessments (protocol compliance, safety, and financial coverage) are favorable with high confidence. The patient meets inclusion criteria, empagliflozin 10 mg is safe given eGFR 52 mL/min/1.73m\u00b2, and the intervention is fully covered under the trial agreement. No violations, safety concerns, or financial liability are present."
            }
          ],
          "iteration_count": 0,
          "safety_evidence": [
            "Diabetic Nephropathy Renal Filtration Safety Confirmed (eGFR >= 30 mL/min/1.73m2)"
          ],
          "financial_result": {
            "tier": "Tier-1 Investigational Coverage",
            "callout": "100% Protocol & Investigational Coverage under Sponsor Trial Agreement for Empagliflozin (Zero Patient Liability).",
            "patientId": "P009",
            "confidence": 0.95,
            "explanation": "The prescribed intervention (Empagliflozin 10 mg oral daily) matches the standard protocol dosing for NCT00699998. Per sponsor clinical trial agreement, this is 100% covered with $0 patient liability. No prior authorization required.",
            "coverage_status": "COVERED",
            "financialExposure": 0,
            "pre_auth_required": false,
            "sponsor_billing_eligible": true
          },
          "protocol_evidence": [
            {
              "text": "Cohort B Standard Protocol: Empagliflozin 10 mg orally once daily. Patients on renal stratification require eGFR >= 30 mL/min/1.73m2.",
              "score": 0.95,
              "source": "ClinicalTrials.gov",
              "section": "dosing_protocol",
              "chunk_id": "NCT00699998-dosing-001",
              "trial_id": "NCT00699998"
            },
            {
              "text": "Dialysis or severe end-stage renal failure excludes participation.",
              "score": 0.92,
              "source": "ClinicalTrials.gov",
              "section": "eligibility",
              "chunk_id": "NCT00699998-eligibility-003",
              "trial_id": "NCT00699998"
            }
          ],
          "decision_timestamp": "2026-09-17T01:47:51.543Z",
          "clinician_justification": "Order accepted and electronically co-signed by attending investigator per 21 CFR Part 11.",
          "final_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "original_prescribed_action": "Empagliflozin 10 mg oral once daily",
          "protocol_compliance_result": {
            "valid": true,
            "sources": [
              "ClinicalTrials.gov Protocol NCT00699998"
            ],
            "trial_id": "NCT00699998",
            "confidence": 0.9,
            "violations": [],
            "explanation": "Intervention complies with protocol NCT00699998 standard trial inclusion criteria.",
            "compliance_status": "COMPLIANT",
            "needs_human_review": false
          }
        }
      ],
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "64-year-old male with diabetic nephropathy stage 3a and membranous nephropathy. Preserved renal function with eGFR 52. On empagliflozin, losartan, and torsemide, with no prior bleeding or anticoagulation.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P010",
    "name": "Rohan Deshpande",
    "dob": "1961-03-15",
    "age": 65,
    "sex": "M",
    "cohort": "Cohort A - Standard Protocol - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "non-valvular atrial fibrillation",
    "creatinine": "CrCl 72.0 mL/min",
    "trial_id": "NCT00781573",
    "medications": [
      "apixaban 5mg BID",
      "clopidogrel 75mg daily",
      "atorvastatin 40mg daily"
    ],
    "clinical_data": {
      "age": 65,
      "dob": "1961-03-15",
      "sex": "male",
      "cohort": "Cohort A - Standard Protocol",
      "status": "JUSTIFIED",
      "weight": 72.0,
      "fhir_id": "138792297",
      "allergies": [],
      "diagnoses": [
        "non-valvular atrial fibrillation",
        "coronary artery disease post-PCI",
        "essential hypertension"
      ],
      "birth_date": "1961-03-15",
      "patient_id": "P010",
      "ecog_status": 0,
      "internal_id": "P010",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 32.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4200.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 78.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 220000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 14.2
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.8
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.0
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 72.0
        }
      },
      "medications": [
        "apixaban 5mg BID",
        "clopidogrel 75mg daily",
        "atorvastatin 40mg daily"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": true,
        "breastfeeding": false,
        "days_since_PCI": 180,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": true,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": true,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "percutaneous coronary intervention (PCI) 6 months ago",
        "laparoscopic cholecystectomy 3 years ago"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "65-year-old male with non-valvular atrial fibrillation and coronary artery disease status post PCI 6 months ago. He also has essential hypertension and underwent laparoscopic cholecystectomy 3 years ago without complications. Currently on dual antithrombotic therapy with apixaban and clopidogrel.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P011",
    "name": "Jasleen Kaur Bajwa",
    "dob": "1974-03-15",
    "age": 52,
    "sex": "F",
    "cohort": "Cohort B - NAFLD Protocol - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "metabolic dysfunction-associated steatohepatitis (MASH)",
    "creatinine": "CrCl 65.0 mL/min",
    "trial_id": "NCT00809965",
    "medications": [
      "pioglitazone 30mg daily",
      "semaglutide 1.0mg weekly",
      "vitamin E 800 IU daily"
    ],
    "clinical_data": {
      "age": 52,
      "dob": "1974-03-15",
      "sex": "female",
      "cohort": "Cohort B - NAFLD Protocol",
      "status": "JUSTIFIED",
      "weight": 68.0,
      "fhir_id": "138792335",
      "allergies": [],
      "diagnoses": [
        "metabolic dysfunction-associated steatohepatitis (MASH)",
        "type 2 diabetes mellitus"
      ],
      "birth_date": "1974-03-15",
      "patient_id": "P011",
      "ecog_status": 0,
      "internal_id": "P011",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 35.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 3800.0
        },
        "AST": {
          "unit": "U/L",
          "value": 32.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 78.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 240000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.8
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.8
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.0
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 65.0
        }
      },
      "medications": [
        "pioglitazone 30mg daily",
        "semaglutide 1.0mg weekly",
        "vitamin E 800 IU daily"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "cholecystectomy",
        "diagnostic liver biopsy"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "52-year-old female with metabolic dysfunction-associated steatohepatitis (MASH) and type 2 diabetes mellitus. She has a history of cholecystectomy and diagnostic liver biopsy. Currently on pioglitazone, semaglutide, and vitamin E for MASH management.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P012",
    "name": "Priya Rathore",
    "dob": "1964-03-15",
    "age": 62,
    "sex": "F",
    "cohort": "Cohort C - Solid Tumor Oncology - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "non-small cell lung cancer (stage IIIB)",
    "creatinine": "CrCl 68.0 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "pembrolizumab 200mg IV Q3W",
      "capecitabine 1000mg BID",
      "ondansetron 8mg PRN"
    ],
    "clinical_data": {
      "age": 62,
      "dob": "1964-03-15",
      "sex": "female",
      "cohort": "Cohort C - Solid Tumor Oncology",
      "status": "JUSTIFIED",
      "weight": 65.0,
      "fhir_id": "138792353",
      "allergies": [],
      "diagnoses": [
        "non-small cell lung cancer (stage IIIB)",
        "colorectal adenocarcinoma"
      ],
      "birth_date": "1964-03-15",
      "patient_id": "P012",
      "ecog_status": 1,
      "internal_id": "P012",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 32.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4200.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.2
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 72.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 220000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 12.5
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.9
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 0.9
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 68.0
        }
      },
      "medications": [
        "pembrolizumab 200mg IV Q3W",
        "capecitabine 1000mg BID",
        "ondansetron 8mg PRN"
      ],
      "vital_signs": {
        "heart_rate": 78.0,
        "blood_pressure_systolic": 130,
        "blood_pressure_diastolic": 82
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 0,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "Lobectomy (right lower lobe) 2 years ago",
        "Hemicolectomy 1 year ago"
      ],
      "cardiac_function": {
        "QTc": 420.0,
        "LVEF": 60.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "fatigue",
        "mild dyspnea",
        "intermittent abdominal pain"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "Patient is a 62-year-old woman with stage IIIB non-small cell lung cancer and colorectal adenocarcinoma. She underwent a right lower lobe lobectomy 2 years ago and a hemicolectomy 1 year ago. Currently on pembrolizumab and capecitabine with mild fatigue and dyspnea.",
      "last_systemic_therapy_date": "2024-03-15"
    }
  },
  {
    "id": "P013",
    "name": "Kavita Deshmukh",
    "dob": "1961-07-22",
    "age": 64,
    "sex": "F",
    "cohort": "Cohort B - Renal Stratification - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "Diabetic nephropathy stage 3a",
    "creatinine": "CrCl 58.0 mL/min",
    "trial_id": "NCT00699998",
    "medications": [
      "Empagliflozin 10mg daily",
      "Losartan 50mg daily"
    ],
    "clinical_data": {
      "age": 64,
      "dob": "1961-07-22",
      "sex": "female",
      "name": "Kavita Deshmukh",
      "cohort": "Cohort B - Renal Stratification",
      "status": "JUSTIFIED",
      "weight": 66.0,
      "diagnoses": [
        "Diabetic nephropathy stage 3a",
        "Essential hypertension"
      ],
      "patient_id": "P013",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 24.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4100.0
        },
        "AST": {
          "unit": "U/L",
          "value": 22.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.0
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 52.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 230000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.5
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.7
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.3
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 58.0
        }
      },
      "medications": [
        "Empagliflozin 10mg daily",
        "Losartan 50mg daily"
      ],
      "vital_signs": {
        "heart_rate": 70.0,
        "blood_pressure_systolic": 122,
        "blood_pressure_diastolic": 78
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "breastfeeding": false,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "history_of_intracranial_hemorrhage": false
      },
      "coverage_status": "COVERED",
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED"
    }
  },
  {
    "id": "P014",
    "name": "Kondaveeti Anitha",
    "dob": "1961-03-15",
    "age": 65,
    "sex": "F",
    "cohort": "Cohort A - Standard Protocol - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "non-valvular atrial fibrillation",
    "creatinine": "CrCl 65.0 mL/min",
    "trial_id": "NCT00699998",
    "medications": [
      "apixaban 5mg BID",
      "clopidogrel 75mg daily",
      "atorvastatin 40mg daily"
    ],
    "clinical_data": {
      "age": 65,
      "dob": "1961-03-15",
      "sex": "female",
      "cohort": "Cohort A - Standard Protocol",
      "status": "JUSTIFIED",
      "weight": 68.0,
      "fhir_id": "138792372",
      "allergies": [],
      "diagnoses": [
        "non-valvular atrial fibrillation",
        "coronary artery disease post-PCI",
        "essential hypertension"
      ],
      "birth_date": "1961-03-15",
      "patient_id": "P014",
      "ecog_status": 0,
      "internal_id": "P014",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 28.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 3800.0
        },
        "AST": {
          "unit": "U/L",
          "value": 24.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 75.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 240000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.8
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.8
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.0
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 65.0
        }
      },
      "medications": [
        "apixaban 5mg BID",
        "clopidogrel 75mg daily",
        "atorvastatin 40mg daily"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": true,
        "breastfeeding": false,
        "days_since_PCI": 180,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": true,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": true,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "PCI for LAD stent 6 months ago",
        "history of hypertension for 10 years"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "65-year-old female with non-valvular atrial fibrillation and coronary artery disease status post PCI. She has essential hypertension and is on apixaban, clopidogrel, and atorvastatin.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P015",
    "name": "Anjali Borphukan",
    "dob": "1974-03-15",
    "age": 52,
    "sex": "F",
    "cohort": "Cohort B - NAFLD Protocol - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "metabolic dysfunction-associated steatohepatitis (MASH)",
    "creatinine": "CrCl 65.0 mL/min",
    "trial_id": "NCT00781573",
    "medications": [
      "pioglitazone 30mg daily",
      "semaglutide 1.0mg weekly",
      "vitamin E 800 IU daily"
    ],
    "clinical_data": {
      "age": 52,
      "dob": "1974-03-15",
      "sex": "female",
      "cohort": "Cohort B - NAFLD Protocol",
      "status": "JUSTIFIED",
      "weight": 72.0,
      "fhir_id": "138792410",
      "allergies": [],
      "diagnoses": [
        "metabolic dysfunction-associated steatohepatitis (MASH)",
        "type 2 diabetes mellitus"
      ],
      "birth_date": "1974-03-15",
      "patient_id": "P015",
      "ecog_status": 0,
      "internal_id": "P015",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 35.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4500.0
        },
        "AST": {
          "unit": "U/L",
          "value": 30.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 85.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 250000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.8
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.8
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.0
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 65.0
        }
      },
      "medications": [
        "pioglitazone 30mg daily",
        "semaglutide 1.0mg weekly",
        "vitamin E 800 IU daily"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "laparoscopic cholecystectomy (2018)",
        "inguinal hernia repair (2020)"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "fatigue",
        "right upper quadrant discomfort"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "52-year-old female with metabolic dysfunction-associated steatohepatitis (MASH) and type 2 diabetes mellitus. She has a history of cholecystectomy and inguinal hernia repair. Currently on pioglitazone, semaglutide, and vitamin E therapy.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P016",
    "name": "Ananya Bandyopadhyay",
    "dob": "1974-03-15",
    "age": 52,
    "sex": "F",
    "cohort": "Cohort C - Solid Tumor Oncology - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "Non-small cell lung cancer (stage IIIB)",
    "creatinine": "CrCl 68.0 mL/min",
    "trial_id": "NCT00809965",
    "medications": [
      "pembrolizumab 200mg IV Q3W",
      "capecitabine 1000mg BID",
      "ondansetron 8mg PRN"
    ],
    "clinical_data": {
      "age": 52,
      "dob": "1974-03-15",
      "sex": "female",
      "cohort": "Cohort C - Solid Tumor Oncology",
      "status": "JUSTIFIED",
      "weight": 62.0,
      "fhir_id": "138792427",
      "allergies": [
        "none known"
      ],
      "diagnoses": [
        "Non-small cell lung cancer (stage IIIB)",
        "Colorectal adenocarcinoma"
      ],
      "birth_date": "1974-03-15",
      "patient_id": "P016",
      "ecog_status": 1,
      "internal_id": "P016",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 32.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4200.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.0
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 72.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 210000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 12.5
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.7
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 0.9
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 68.0
        }
      },
      "medications": [
        "pembrolizumab 200mg IV Q3W",
        "capecitabine 1000mg BID",
        "ondansetron 8mg PRN"
      ],
      "vital_signs": {
        "heart_rate": 78.0,
        "blood_pressure_systolic": 125,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "Lobectomy for NSCLC (left upper lobe)",
        "Colectomy for colorectal cancer"
      ],
      "cardiac_function": {
        "QTc": 420.0,
        "LVEF": 60.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "fatigue",
        "mild cough"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "Patient is a 52-year-old female with metastatic non-small cell lung cancer (stage IIIB) and history of colorectal adenocarcinoma. She underwent left upper lobectomy and colectomy. Currently on pembrolizumab and capecitabine.",
      "last_systemic_therapy_date": "2025-03-15"
    }
  },
  {
    "id": "P017",
    "name": "Meenakshi Chettiar",
    "dob": "1964-03-15",
    "age": 62,
    "sex": "F",
    "cohort": "Cohort B - Renal Stratification - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "diabetic nephropathy stage 3a",
    "creatinine": "CrCl 55.0 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "empagliflozin 10mg daily",
      "losartan 50mg daily",
      "torsemide 10mg daily"
    ],
    "clinical_data": {
      "age": 62,
      "dob": "1964-03-15",
      "sex": "female",
      "cohort": "Cohort B - Renal Stratification",
      "status": "JUSTIFIED",
      "weight": 68.0,
      "fhir_id": "138792446",
      "allergies": [],
      "diagnoses": [
        "diabetic nephropathy stage 3a",
        "membranous nephropathy"
      ],
      "birth_date": "1964-03-15",
      "patient_id": "P017",
      "ecog_status": 1,
      "internal_id": "P017",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 30.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4500.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 52.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 250000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 12.0
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.7
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.3
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 55.0
        }
      },
      "medications": [
        "empagliflozin 10mg daily",
        "losartan 50mg daily",
        "torsemide 10mg daily"
      ],
      "vital_signs": {
        "heart_rate": 74.0,
        "blood_pressure_systolic": 130,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "renal biopsy",
        "appendectomy"
      ],
      "cardiac_function": {
        "QTc": 420.0,
        "LVEF": 60.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "lower extremity edema",
        "fatigue"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "62-year-old female with diabetic nephropathy stage 3a and membranous nephropathy, on empagliflozin and losartan. History of renal biopsy and appendectomy. No prior bleeding or anticoagulation.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P018",
    "name": "Smita Deshpande",
    "dob": "1958-03-15",
    "age": 68,
    "sex": "F",
    "cohort": "Cohort A - Standard Protocol - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "Non-valvular atrial fibrillation",
    "creatinine": "CrCl 60.0 mL/min",
    "trial_id": "NCT00699998",
    "medications": [
      "Apixaban 5mg BID",
      "Clopidogrel 75mg daily",
      "Atorvastatin 40mg daily"
    ],
    "clinical_data": {
      "age": 68,
      "dob": "1958-03-15",
      "sex": "female",
      "cohort": "Cohort A - Standard Protocol",
      "status": "JUSTIFIED",
      "weight": 72.0,
      "fhir_id": "138792464",
      "allergies": [
        "No known allergies"
      ],
      "diagnoses": [
        "Non-valvular atrial fibrillation",
        "Coronary artery disease status post-PCI",
        "Essential hypertension"
      ],
      "birth_date": "1958-03-15",
      "patient_id": "P018",
      "ecog_status": 1,
      "internal_id": "P018",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 32.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4200.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.2
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 72.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 220000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.5
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.9
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.1
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 60.0
        }
      },
      "medications": [
        "Apixaban 5mg BID",
        "Clopidogrel 75mg daily",
        "Atorvastatin 40mg daily"
      ],
      "vital_signs": {
        "heart_rate": 74.0,
        "blood_pressure_systolic": 132,
        "blood_pressure_diastolic": 82
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": true,
        "breastfeeding": false,
        "days_since_PCI": 7,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": true,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": true,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "Percutaneous coronary intervention (PCI) with drug-eluting stent to left anterior descending artery 7 days ago",
        "Laparoscopic cholecystectomy 5 years ago"
      ],
      "cardiac_function": {
        "QTc": 430.0,
        "LVEF": 50.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "No active chest pain",
        "Occasional palpitations",
        "Fatigue"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "68-year-old female with non-valvular atrial fibrillation and coronary artery disease status post-PCI with drug-eluting stent 7 days ago. She has essential hypertension and is currently on triple therapy with apixaban, clopidogrel, and atorvastatin. No history of bleeding or intracranial hemorrhage.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P019",
    "name": "Gurpreet Bajwa",
    "dob": "1974-03-15",
    "age": 52,
    "sex": "F",
    "cohort": "Cohort B - NAFLD Protocol - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "metabolic dysfunction-associated steatohepatitis (MASH)",
    "creatinine": "CrCl 65.0 mL/min",
    "trial_id": "NCT00781573",
    "medications": [
      "pioglitazone 30mg daily",
      "semaglutide 1.0mg weekly",
      "vitamin E 800 IU daily"
    ],
    "clinical_data": {
      "age": 52,
      "dob": "1974-03-15",
      "sex": "female",
      "cohort": "Cohort B - NAFLD Protocol",
      "status": "JUSTIFIED",
      "weight": 68.0,
      "fhir_id": "138792483",
      "allergies": [],
      "diagnoses": [
        "metabolic dysfunction-associated steatohepatitis (MASH)",
        "type 2 diabetes mellitus"
      ],
      "birth_date": "1974-03-15",
      "patient_id": "P019",
      "ecog_status": 0,
      "internal_id": "P019",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 42.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4000.0
        },
        "AST": {
          "unit": "U/L",
          "value": 35.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 70.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 220000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.5
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.8
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.0
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 65.0
        }
      },
      "medications": [
        "pioglitazone 30mg daily",
        "semaglutide 1.0mg weekly",
        "vitamin E 800 IU daily"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "cholecystectomy (2018)",
        "laparoscopic adjustable gastric banding (2015)"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "fatigue",
        "right upper quadrant discomfort"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "52-year-old female with metabolic dysfunction-associated steatohepatitis and type 2 diabetes mellitus. She has a history of cholecystectomy and gastric banding. Currently on pioglitazone, semaglutide, and vitamin E for NAFLD management.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P020",
    "name": "Meera Solanki",
    "dob": "1964-03-15",
    "age": 62,
    "sex": "F",
    "cohort": "Cohort C - Solid Tumor Oncology - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "Non-small cell lung cancer, stage IIIB",
    "creatinine": "CrCl 68.0 mL/min",
    "trial_id": "NCT00809965",
    "medications": [
      "Pembrolizumab 200mg IV Q3W",
      "Capecitabine 1000mg BID",
      "Ondansetron 8mg PRN"
    ],
    "clinical_data": {
      "age": 62,
      "dob": "1964-03-15",
      "sex": "female",
      "cohort": "Cohort C - Solid Tumor Oncology",
      "status": "JUSTIFIED",
      "weight": 68.0,
      "fhir_id": "138792501",
      "allergies": [],
      "diagnoses": [
        "Non-small cell lung cancer, stage IIIB",
        "Colorectal adenocarcinoma"
      ],
      "birth_date": "1964-03-15",
      "patient_id": "P020",
      "ecog_status": 0,
      "internal_id": "P020",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 32.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4200.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 82.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 250000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.2
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.7
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 0.9
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 68.0
        }
      },
      "medications": [
        "Pembrolizumab 200mg IV Q3W",
        "Capecitabine 1000mg BID",
        "Ondansetron 8mg PRN"
      ],
      "vital_signs": {
        "heart_rate": 74.0,
        "blood_pressure_systolic": 128,
        "blood_pressure_diastolic": 82
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "Lobectomy left lower lobe",
        "Partial colectomy",
        "Pneumonia requiring hospitalization"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "62-year-old female with stage IIIB non-small cell lung cancer and colorectal adenocarcinoma. She underwent left lower lobectomy and partial colectomy; history of pneumonia. Currently on pembrolizumab and capecitabine with good performance status.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P021",
    "name": "Ramesh Kushwaha",
    "dob": "1964-03-15",
    "age": 62,
    "sex": "M",
    "cohort": "Cohort B - Renal Stratification - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "diabetic nephropathy stage 3a",
    "creatinine": "CrCl 70.0 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "empagliflozin 10mg daily",
      "losartan 50mg daily",
      "torsemide 10mg daily"
    ],
    "clinical_data": {
      "age": 62,
      "dob": "1964-03-15",
      "sex": "male",
      "cohort": "Cohort B - Renal Stratification",
      "status": "JUSTIFIED",
      "weight": 78.0,
      "fhir_id": "138792529",
      "allergies": [],
      "diagnoses": [
        "diabetic nephropathy stage 3a",
        "membranous nephropathy",
        "type 2 diabetes mellitus",
        "hypertension"
      ],
      "birth_date": "1964-03-15",
      "patient_id": "P021",
      "ecog_status": 1,
      "internal_id": "P021",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 30.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4000.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 65.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 220000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 12.5
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.7
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.3
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 70.0
        }
      },
      "medications": [
        "empagliflozin 10mg daily",
        "losartan 50mg daily",
        "torsemide 10mg daily"
      ],
      "vital_signs": {
        "heart_rate": 76.0,
        "blood_pressure_systolic": 135,
        "blood_pressure_diastolic": 85
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 0,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "renal biopsy for membranous nephropathy",
        "diagnosis of type 2 diabetes mellitus 8 years ago",
        "hypertension diagnosis 5 years ago"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "bilateral leg edema",
        "fatigue"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "62-year-old male with diabetic nephropathy stage 3a and membranous nephropathy. Currently managed with SGLT2 inhibitor, ARB, and diuretic. History of renal biopsy confirming membranous nephropathy. Stable renal function with eGFR 65.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P022",
    "name": "Kondaveeti Padma",
    "dob": "1961-03-15",
    "age": 65,
    "sex": "F",
    "cohort": "Cohort A - Standard Protocol - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "non-valvular atrial fibrillation",
    "creatinine": "CrCl 62.0 mL/min",
    "trial_id": "NCT00699998",
    "medications": [
      "apixaban 5mg BID",
      "clopidogrel 75mg daily",
      "atorvastatin 40mg daily"
    ],
    "clinical_data": {
      "age": 65,
      "dob": "1961-03-15",
      "sex": "female",
      "cohort": "Cohort A - Standard Protocol",
      "status": "JUSTIFIED",
      "weight": 72.0,
      "fhir_id": "138792559",
      "allergies": [
        "none known"
      ],
      "diagnoses": [
        "non-valvular atrial fibrillation",
        "coronary artery disease status post-PCI",
        "essential hypertension"
      ],
      "birth_date": "1961-03-15",
      "patient_id": "P022",
      "ecog_status": 1,
      "internal_id": "P022",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 32.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4200.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.2
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 78.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 220000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.5
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.7
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 0.9
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 62.0
        }
      },
      "medications": [
        "apixaban 5mg BID",
        "clopidogrel 75mg daily",
        "atorvastatin 40mg daily"
      ],
      "vital_signs": {
        "heart_rate": 68.0,
        "blood_pressure_systolic": 118,
        "blood_pressure_diastolic": 76
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": true,
        "breastfeeding": false,
        "days_since_PCI": 30,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": true,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": true,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "Laparoscopic cholecystectomy (2018)",
        "Cataract surgery (2020)"
      ],
      "cardiac_function": {
        "QTc": 420.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "palpitations",
        "fatigue"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "65-year-old female with non-valvular atrial fibrillation and coronary artery disease status post-PCI. History of hypertension. Currently on apixaban and clopidogrel for antithrombotic therapy. No prior bleeding or intracranial hemorrhage.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P023",
    "name": "Mitali Borphukan",
    "dob": "1974-03-15",
    "age": 52,
    "sex": "F",
    "cohort": "Cohort B - NAFLD Protocol - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "metabolic dysfunction-associated steatohepatitis (MASH)",
    "creatinine": "CrCl 72.0 mL/min",
    "trial_id": "NCT00781573",
    "medications": [
      "pioglitazone 30mg daily",
      "semaglutide 1.0mg weekly",
      "vitamin E 800 IU daily"
    ],
    "clinical_data": {
      "age": 52,
      "dob": "1974-03-15",
      "sex": "female",
      "cohort": "Cohort B - NAFLD Protocol",
      "status": "JUSTIFIED",
      "weight": 72.0,
      "fhir_id": "138792520",
      "allergies": [],
      "diagnoses": [
        "metabolic dysfunction-associated steatohepatitis (MASH)",
        "type 2 diabetes mellitus"
      ],
      "birth_date": "1974-03-15",
      "patient_id": "P023",
      "ecog_status": 1,
      "internal_id": "P023",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 35.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4000.0
        },
        "AST": {
          "unit": "U/L",
          "value": 30.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.0
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 80.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 220000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.5
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.7
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 0.9
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 72.0
        }
      },
      "medications": [
        "pioglitazone 30mg daily",
        "semaglutide 1.0mg weekly",
        "vitamin E 800 IU daily"
      ],
      "vital_signs": {
        "heart_rate": 76.0,
        "blood_pressure_systolic": 130,
        "blood_pressure_diastolic": 82
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 0,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "cholecystectomy (2018)",
        "laparoscopic sleeve gastrectomy (2020)"
      ],
      "cardiac_function": {
        "QTc": 420.0,
        "LVEF": 60.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "fatigue",
        "right upper quadrant discomfort"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "52-year-old female with MASH and type 2 diabetes. History of cholecystectomy and sleeve gastrectomy. Currently on pioglitazone, semaglutide, and vitamin E.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P024",
    "name": "Smita Bandyopadhyay",
    "dob": "1968-03-15",
    "age": 58,
    "sex": "F",
    "cohort": "Cohort C - Solid Tumor Oncology - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "Non-small cell lung cancer (stage IIIB)",
    "creatinine": "CrCl 62.0 mL/min",
    "trial_id": "NCT00809965",
    "medications": [
      "pembrolizumab 200mg IV Q3W",
      "capecitabine 1000mg BID",
      "ondansetron 8mg PRN"
    ],
    "clinical_data": {
      "age": 58,
      "dob": "1968-03-15",
      "sex": "female",
      "cohort": "Cohort C - Solid Tumor Oncology",
      "status": "JUSTIFIED",
      "weight": 64.5,
      "fhir_id": "138792578",
      "allergies": [
        "sulfonamides"
      ],
      "diagnoses": [
        "Non-small cell lung cancer (stage IIIB)",
        "Colorectal adenocarcinoma"
      ],
      "birth_date": "1968-03-15",
      "patient_id": "P024",
      "ecog_status": 1,
      "internal_id": "P024",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 32.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4200.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.0
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 68.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 210000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 12.5
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.7
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 0.9
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 62.0
        }
      },
      "medications": [
        "pembrolizumab 200mg IV Q3W",
        "capecitabine 1000mg BID",
        "ondansetron 8mg PRN"
      ],
      "vital_signs": {
        "heart_rate": 76.0,
        "blood_pressure_systolic": 128,
        "blood_pressure_diastolic": 82
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": true,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "Laparoscopic right hemicolectomy for colorectal adenocarcinoma (2 years ago)",
        "Radiotherapy to chest for lung cancer (6 months ago)"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "Fatigue (grade 1)",
        "Mild nausea"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "Patient with stage IIIB non-small cell lung cancer and history of colorectal adenocarcinoma. She underwent laparoscopic right hemicolectomy two years ago and chest radiotherapy six months ago. Currently on pembrolizumab and capecitabine with good tolerance.",
      "last_systemic_therapy_date": "2025-03-15"
    }
  },
  {
    "id": "P025",
    "name": "Rajesh Paswan",
    "dob": "1964-03-15",
    "age": 62,
    "sex": "M",
    "cohort": "Cohort B - Renal Stratification - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "Diabetic nephropathy stage 3a",
    "creatinine": "CrCl 55.0 mL/min",
    "trial_id": "NCT00699998",
    "medications": [
      "Empagliflozin 10mg daily",
      "Losartan 50mg daily",
      "Torsemide 10mg daily"
    ],
    "clinical_data": {
      "age": 62,
      "dob": "1964-03-15",
      "sex": "male",
      "cohort": "Cohort B - Renal Stratification",
      "status": "JUSTIFIED",
      "weight": 72.0,
      "fhir_id": "1728",
      "allergies": [],
      "diagnoses": [
        "Diabetic nephropathy stage 3a",
        "Membranous nephropathy",
        "Type 2 diabetes mellitus"
      ],
      "birth_date": "1964-03-15",
      "patient_id": "P025",
      "ecog_status": 0,
      "internal_id": "P025",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 28.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 3800.0
        },
        "AST": {
          "unit": "U/L",
          "value": 24.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 55.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 240000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.8
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.8
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.3
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 55.0
        }
      },
      "medications": [
        "Empagliflozin 10mg daily",
        "Losartan 50mg daily",
        "Torsemide 10mg daily"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 130,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "Renal biopsy (left kidney) 2022",
        "Cataract extraction right eye 2020"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "Pedal edema",
        "Fatigue"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "62-year-old male with diabetic nephropathy stage 3a and membranous nephropathy, on empagliflozin and losartan. History of renal biopsy and cataract surgery. Current symptoms include mild pedal edema and fatigue.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P026",
    "name": "Srinidhi Yarlagadda",
    "dob": "1972-03-15",
    "age": 54,
    "sex": "F",
    "cohort": "Cohort B - NAFLD Protocol - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "metabolic dysfunction-associated steatohepatitis (MASH)",
    "creatinine": "CrCl 68.0 mL/min",
    "trial_id": "NCT00781573",
    "medications": [
      "pioglitazone 30mg daily",
      "semaglutide 1.0mg weekly",
      "vitamin E 800 IU daily"
    ],
    "clinical_data": {
      "age": 54,
      "dob": "1972-03-15",
      "sex": "female",
      "cohort": "Cohort B - NAFLD Protocol",
      "status": "JUSTIFIED",
      "weight": 72.5,
      "fhir_id": "1710",
      "allergies": [],
      "diagnoses": [
        "metabolic dysfunction-associated steatohepatitis (MASH)",
        "type 2 diabetes mellitus"
      ],
      "birth_date": "1972-03-15",
      "patient_id": "P026",
      "ecog_status": 0,
      "internal_id": "P026",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 42.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4200.0
        },
        "AST": {
          "unit": "U/L",
          "value": 36.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.0
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 78.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 220000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.2
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.7
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 0.9
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 68.0
        }
      },
      "medications": [
        "pioglitazone 30mg daily",
        "semaglutide 1.0mg weekly",
        "vitamin E 800 IU daily"
      ],
      "vital_signs": {
        "heart_rate": 74.0,
        "blood_pressure_systolic": 128,
        "blood_pressure_diastolic": 82
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "cholecystectomy (2019)",
        "diagnosed with type 2 diabetes (2017)"
      ],
      "cardiac_function": {
        "QTc": 420.0,
        "LVEF": 60.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "fatigue",
        "mild right upper quadrant discomfort"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "54-year-old female with metabolic dysfunction-associated steatohepatitis and type 2 diabetes. She underwent cholecystectomy in 2019 and has been on pioglitazone, semaglutide, and vitamin E for liver and metabolic management. Current labs show mild transaminase elevation with preserved renal function.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P027",
    "name": "Smita Bandyopadhyay",
    "dob": "1964-03-15",
    "age": 62,
    "sex": "F",
    "cohort": "Cohort C - Solid Tumor Oncology - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "Non-small cell lung cancer, stage IIIB",
    "creatinine": "CrCl 65.0 mL/min",
    "trial_id": "NCT00809965",
    "medications": [
      "pembrolizumab 200mg IV Q3W",
      "capecitabine 1000mg BID",
      "ondansetron 8mg PRN"
    ],
    "clinical_data": {
      "age": 62,
      "dob": "1964-03-15",
      "sex": "female",
      "cohort": "Cohort C - Solid Tumor Oncology",
      "status": "JUSTIFIED",
      "weight": 68.0,
      "fhir_id": "1691",
      "allergies": [],
      "diagnoses": [
        "Non-small cell lung cancer, stage IIIB",
        "Colorectal adenocarcinoma"
      ],
      "birth_date": "1964-03-15",
      "patient_id": "P027",
      "ecog_status": 0,
      "internal_id": "P027",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 32.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 3800.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 78.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 240000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.8
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.8
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.0
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 65.0
        }
      },
      "medications": [
        "pembrolizumab 200mg IV Q3W",
        "capecitabine 1000mg BID",
        "ondansetron 8mg PRN"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "Lobectomy for non-small cell lung cancer (left upper lobe) - 18 months ago",
        "Partial colectomy for colorectal adenocarcinoma - 2 years ago",
        "Adjuvant chemotherapy with FOLFOX completed 1 year ago"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "62-year-old female with history of stage IIIB non-small cell lung cancer treated with lobectomy and now on pembrolizumab. She also has a history of colorectal adenocarcinoma status post partial colectomy and adjuvant FOLFOX. Currently receiving capecitabine and pembrolizumab with good tolerance.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P028",
    "name": "Ramanathan Chettiar",
    "dob": "1958-03-15",
    "age": 68,
    "sex": "M",
    "cohort": "Cohort A - Standard Protocol - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "non-valvular atrial fibrillation",
    "creatinine": "CrCl 65.0 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "apixaban 5mg BID",
      "clopidogrel 75mg daily",
      "atorvastatin 40mg daily"
    ],
    "clinical_data": {
      "age": 68,
      "dob": "1958-03-15",
      "sex": "male",
      "cohort": "Cohort A - Standard Protocol",
      "status": "JUSTIFIED",
      "weight": 72.0,
      "fhir_id": "1747",
      "allergies": [],
      "diagnoses": [
        "non-valvular atrial fibrillation",
        "coronary artery disease post-PCI",
        "essential hypertension"
      ],
      "birth_date": "1958-03-15",
      "patient_id": "P028",
      "ecog_status": 0,
      "internal_id": "P028",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 32.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4200.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 78.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 220000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 14.2
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.8
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.0
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 65.0
        }
      },
      "medications": [
        "apixaban 5mg BID",
        "clopidogrel 75mg daily",
        "atorvastatin 40mg daily"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": true,
        "breastfeeding": false,
        "days_since_PCI": 7,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": true,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": true,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "percutaneous coronary intervention with drug-eluting stent 7 days ago",
        "cataract surgery 2 years ago"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "Mr. Chettiar is a 68-year-old male with non-valvular atrial fibrillation and coronary artery disease status post-PCI 7 days ago. He has essential hypertension and is currently on apixaban and clopidogrel for antithrombotic therapy. His recovery has been uneventful with no bleeding complications.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P029",
    "name": "Simran Kaur",
    "dob": "1974-03-15",
    "age": 52,
    "sex": "F",
    "cohort": "Cohort B - NAFLD Protocol - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "metabolic dysfunction-associated steatohepatitis (MASH)",
    "creatinine": "CrCl 65.0 mL/min",
    "trial_id": "NCT00699998",
    "medications": [
      "pioglitazone 30mg daily",
      "semaglutide 1.0mg weekly",
      "vitamin E 800 IU daily"
    ],
    "clinical_data": {
      "age": 52,
      "dob": "1974-03-15",
      "sex": "female",
      "name": "Simran Kaur",
      "cohort": "Cohort B - NAFLD Protocol",
      "status": "JUSTIFIED",
      "weight": 75.0,
      "fhir_id": "4201",
      "allergies": [],
      "diagnoses": [
        "metabolic dysfunction-associated steatohepatitis (MASH)",
        "type 2 diabetes mellitus"
      ],
      "birth_date": "1974-03-15",
      "patient_id": "P029",
      "ecog_status": 0,
      "internal_id": "P029",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 35.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 3800.0
        },
        "AST": {
          "unit": "U/L",
          "value": 30.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 75.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 240000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.8
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.8
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.0
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 65.0
        }
      },
      "medications": [
        "pioglitazone 30mg daily",
        "semaglutide 1.0mg weekly",
        "vitamin E 800 IU daily"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 0,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "laparoscopic cholecystectomy (2018)",
        "diagnostic liver biopsy (2021)"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "fatigue",
        "right upper quadrant discomfort"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "52-year-old female with metabolic dysfunction-associated steatohepatitis (MASH) and type 2 diabetes mellitus. Past surgical history includes cholecystectomy and liver biopsy. Currently on pioglitazone, semaglutide, and vitamin E.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P030",
    "name": "Arunoday Saikia",
    "dob": "1964-03-15",
    "age": 62,
    "sex": "M",
    "cohort": "Cohort B - Renal Stratification - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "diabetic nephropathy stage 3a",
    "creatinine": "CrCl 55.0 mL/min",
    "trial_id": "NCT00781573",
    "medications": [
      "empagliflozin 10mg daily",
      "losartan 50mg daily",
      "torsemide 10mg daily"
    ],
    "clinical_data": {
      "age": 62,
      "dob": "1964-03-15",
      "sex": "male",
      "name": "Arunoday Saikia",
      "cohort": "Cohort B - Renal Stratification",
      "status": "JUSTIFIED",
      "weight": 72.0,
      "fhir_id": "4202",
      "allergies": [],
      "diagnoses": [
        "diabetic nephropathy stage 3a",
        "membranous nephropathy"
      ],
      "birth_date": "1964-03-15",
      "patient_id": "P030",
      "ecog_status": 1,
      "internal_id": "P030",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 32.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 4200.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.0
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 68.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 220000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.2
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.7
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.2
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 55.0
        }
      },
      "medications": [
        "empagliflozin 10mg daily",
        "losartan 50mg daily",
        "torsemide 10mg daily"
      ],
      "vital_signs": {
        "heart_rate": 76.0,
        "blood_pressure_systolic": 134,
        "blood_pressure_diastolic": 82
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 0,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "kidney biopsy (membranous nephropathy) - 2 years ago",
        "laparoscopic cholecystectomy - 5 years ago"
      ],
      "cardiac_function": {
        "QTc": 420.0,
        "LVEF": 58.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "mild ankle edema",
        "fatigue"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "62-year-old male with diabetic nephropathy stage 3a and membranous nephropathy diagnosed by kidney biopsy two years ago. He has preserved renal function but requires ongoing management with SGLT2 inhibitor and ARB. Past surgical history includes laparoscopic cholecystectomy.",
      "last_systemic_therapy_date": null
    }
  },
  {
    "id": "P031",
    "name": "Ananya Mahapatra",
    "dob": "1964-03-15",
    "age": 62,
    "sex": "F",
    "cohort": "Cohort C - Solid Tumor Oncology - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "Non-small cell lung cancer (stage IIIB)",
    "creatinine": "CrCl 60.0 mL/min",
    "trial_id": "NCT00809965",
    "medications": [
      "pembrolizumab 200mg IV Q3W",
      "capecitabine 1000mg BID",
      "ondansetron 8mg PRN"
    ],
    "clinical_data": {
      "age": 62,
      "dob": "1964-03-15",
      "sex": "female",
      "name": "Ananya Mahapatra",
      "cohort": "Cohort C - Solid Tumor Oncology",
      "status": "JUSTIFIED",
      "weight": 68.0,
      "fhir_id": "4182",
      "allergies": [
        "none known"
      ],
      "diagnoses": [
        "Non-small cell lung cancer (stage IIIB)",
        "Colorectal adenocarcinoma"
      ],
      "birth_date": "1964-03-15",
      "patient_id": "P031",
      "ecog_status": 1,
      "internal_id": "P031",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 30.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 3200.0
        },
        "AST": {
          "unit": "U/L",
          "value": 28.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.0
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 70.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 200000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 12.5
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.7
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 0.9
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 60.0
        }
      },
      "medications": [
        "pembrolizumab 200mg IV Q3W",
        "capecitabine 1000mg BID",
        "ondansetron 8mg PRN"
      ],
      "vital_signs": {
        "heart_rate": 78.0,
        "blood_pressure_systolic": 130,
        "blood_pressure_diastolic": 85
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": false,
        "breastfeeding": false,
        "days_since_PCI": null,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": false,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": false,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "Video-assisted thoracoscopic surgery (VATS) lung biopsy",
        "Laparoscopic right hemicolectomy",
        "Adjuvant chemotherapy completed"
      ],
      "cardiac_function": {
        "QTc": 420.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [
        "fatigue",
        "nausea"
      ],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "This 62-year-old female with history of stage IIIB non-small cell lung cancer and colorectal adenocarcinoma presents for monitoring on pembrolizumab and capecitabine. She has undergone VATS lung biopsy and right hemicolectomy. Current symptoms include mild fatigue and occasional nausea.",
      "last_systemic_therapy_date": "2023-10-15"
    }
  },
  {
    "id": "P032",
    "name": "Ravi Vangapandu",
    "dob": "1961-03-15",
    "age": 65,
    "sex": "M",
    "cohort": "Cohort A - Standard Protocol - [JUSTIFIED \u00b7 Eligible]",
    "diagnosis": "Non-valvular atrial fibrillation",
    "creatinine": "CrCl 65.0 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "Apixaban 5mg BID",
      "Clopidogrel 75mg daily",
      "Atorvastatin 40mg daily"
    ],
    "clinical_data": {
      "age": 65,
      "dob": "1961-03-15",
      "sex": "male",
      "name": "Ravi Vangapandu",
      "cohort": "Cohort A - Standard Protocol",
      "status": "JUSTIFIED",
      "weight": 68.0,
      "fhir_id": "4237",
      "allergies": [],
      "diagnoses": [
        "Non-valvular atrial fibrillation",
        "Coronary artery disease (status post PCI)",
        "Essential hypertension"
      ],
      "birth_date": "1961-03-15",
      "patient_id": "P032",
      "ecog_status": 0,
      "internal_id": "P032",
      "lab_results": {
        "ALT": {
          "unit": "U/L",
          "value": 28.0
        },
        "ANC": {
          "unit": "/uL",
          "value": 3800.0
        },
        "AST": {
          "unit": "U/L",
          "value": 24.0
        },
        "INR": {
          "unit": "ratio",
          "value": 1.1
        },
        "eGFR": {
          "unit": "mL/min/1.73m2",
          "value": 75.0
        },
        "platelets": {
          "unit": "/uL",
          "value": 240000.0
        },
        "hemoglobin": {
          "unit": "g/dL",
          "value": 13.8
        },
        "total_bilirubin": {
          "unit": "mg/dL",
          "value": 0.8
        },
        "serum_creatinine": {
          "unit": "mg/dL",
          "value": 1.0
        },
        "creatinine_clearance": {
          "unit": "mL/min",
          "value": 65.0
        }
      },
      "medications": [
        "Apixaban 5mg BID",
        "Clopidogrel 75mg daily",
        "Atorvastatin 40mg daily"
      ],
      "vital_signs": {
        "heart_rate": 72.0,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80
      },
      "final_verdict": "JUSTIFIED",
      "safety_status": "SAFE",
      "protocol_facts": {
        "pregnant": false,
        "acs_pathway": false,
        "pci_pathway": true,
        "breastfeeding": false,
        "days_since_PCI": 60,
        "prior_bleeding": false,
        "ongoing_bleeding": false,
        "cabg_for_index_acs": false,
        "known_coagulopathy": false,
        "drug_contraindication": [],
        "planned_p2y12_duration": 6,
        "pregnancy_test_negative": true,
        "oral_anticoagulation_required": true,
        "woman_of_childbearing_potential": false,
        "days_since_acute_coronary_syndrome": null,
        "history_of_intracranial_hemorrhage": false,
        "planned_or_existing_oral_anticoagulation": true,
        "other_condition_requiring_chronic_anticoagulation": false
      },
      "coverage_status": "COVERED",
      "medical_history": [
        "Percutaneous coronary intervention (PCI) - 2 months ago",
        "Atrial fibrillation diagnosis - 1 year ago"
      ],
      "cardiac_function": {
        "QTc": 415.0,
        "LVEF": 55.0
      },
      "consent_capacity": true,
      "current_symptoms": [],
      "compliance_status": "COMPLIANT",
      "adjudication_status": "JUSTIFIED",
      "pregnancy_test_result": "negative",
      "medical_history_narrative": "The patient is a 65-year-old male with non-valvular atrial fibrillation and coronary artery disease, status post PCI. He has essential hypertension and is currently on triple therapy with apixaban, clopidogrel, and atorvastatin. He has no history of bleeding or coagulopathy.",
      "last_systemic_therapy_date": null
    }
  },
  {
    id: "PT-4471-0293",
    name: "Eleanor Vance",
    dob: "1958-03-14",
    age: 67,
    sex: "F",
    cohort: "Cohort B - Dose Escalation",
    diagnosis: "Stage III Renal Cell Carcinoma",
    creatinine: "1.9 mg/dL",
    trial_id: "NCT02415400",
    medications: ["Apixaban 5mg BID"],
  },
  {
    id: "PT-8821-4412",
    name: "Marcus Delgado",
    dob: "1971-11-02",
    age: 54,
    sex: "M",
    cohort: "Cohort A - Standard Dose",
    diagnosis: "Metastatic Colorectal Adenocarcinoma",
    creatinine: "1.1 mg/dL",
    trial_id: "NCT00781573",
    medications: ["Apixaban 5mg BID", "Clopidogrel 75mg daily"],
  },
  {
    id: "PT-1092-9934",
    name: "Priya Nair",
    dob: "1983-06-27",
    age: 42,
    sex: "F",
    cohort: "Cohort B - Dose Escalation",
    diagnosis: "Hepatocellular Carcinoma",
    creatinine: "1.4 mg/dL",
    trial_id: "NCT00809965",
    medications: ["Pioglitazone 30mg daily"],
  },
  {
    id: "PT-3310-7781",
    name: "James Okafor",
    dob: "1965-09-19",
    age: 60,
    sex: "M",
    cohort: "Cohort C - Maintenance",
    diagnosis: "Non-Small Cell Lung Carcinoma",
    creatinine: "1.0 mg/dL",
    trial_id: "NCT02415400",
    medications: ["Pembrolizumab 200mg IV Q3W"],
  },
  {
    id: "P034",
    name: "Elena Rostova",
    dob: "Unrecorded",
    age: 0,
    sex: "",
    cohort: "Cohort A - [G1 Ingress Failure] Missing Demographics",
    diagnosis: "Non-valvular atrial fibrillation",
    creatinine: "CrCl 65 mL/min",
    trial_id: "NCT02415400",
    medications: ["Apixaban 5mg BID"],
    clinical_data: {
      patient_id: "P034",
      name: "Elena Rostova",
      age: null,
      sex: "",
      dob: "Unrecorded",
      diagnoses: ["Non-valvular atrial fibrillation"],
      medications: ["Apixaban 5mg BID"],
      lab_results: {
        creatinine_clearance: { value: 65.0, unit: "mL/min" },
        serum_creatinine: { value: 1.0, unit: "mg/dL" },
        ALT: { value: 24.0, unit: "U/L" },
        AST: { value: 22.0, unit: "U/L" },
      },
    },
  },
  {
    id: "P035",
    name: "Kavita Sharma",
    dob: "1974-05-18",
    age: 52,
    sex: "F",
    cohort: "Cohort B - [G2 Hard Boundary Breach] Catastrophic Hepatotoxicity",
    diagnosis: "MASH with bridging fibrosis",
    creatinine: "CrCl 58 mL/min",
    trial_id: "NCT00809965",
    medications: ["Pioglitazone 30mg daily"],
    clinical_data: {
      patient_id: "P035",
      name: "Kavita Sharma",
      age: 52,
      sex: "female",
      diagnoses: ["MASH with bridging fibrosis", "Acute drug-induced hepatotoxicity"],
      medications: ["Pioglitazone 30mg daily"],
      lab_results: {
        ALT: { value: 620.0, unit: "U/L" },
        AST: { value: 480.0, unit: "U/L" },
        total_bilirubin: { value: 4.5, unit: "mg/dL" },
        creatinine_clearance: { value: 58.0, unit: "mL/min" },
        serum_creatinine: { value: 1.1, unit: "mg/dL" },
      },
    },
  },
  {
    id: "P036",
    name: "Darius Vance",
    dob: "1958-11-12",
    age: 68,
    sex: "M",
    cohort: "Cohort A - [Dosing Non-Compliant] Supratherapeutic Dose (40 mg BID)",
    diagnosis: "Non-valvular atrial fibrillation",
    creatinine: "CrCl 68 mL/min",
    trial_id: "NCT02415400",
    medications: ["Apixaban 40mg BID", "Atorvastatin 20mg daily"],
    action: "Apixaban 40 mg oral twice daily",
    clinical_data: {
      patient_id: "P036",
      name: "Darius Vance",
      age: 68,
      sex: "male",
      diagnoses: ["Non-valvular atrial fibrillation"],
      medications: ["Apixaban 40mg BID", "Atorvastatin 20mg daily"],
      prescribed_action: "Apixaban 40 mg oral twice daily",
      protocol_facts: {
        ongoing_bleeding: false,
        days_since_major_bleed: null,
        oral_anticoagulation_required: true,
      },
      lab_results: {
        creatinine_clearance: { value: 68.0, unit: "mL/min" },
        serum_creatinine: { value: 1.0, unit: "mg/dL" },
        eGFR: { value: 72.0, unit: "mL/min/1.73m2" },
        ALT: { value: 26.0, unit: "U/L" },
        AST: { value: 22.0, unit: "U/L" },
        total_bilirubin: { value: 0.8, unit: "mg/dL" },
        ANC: { value: 4100.0, unit: "/uL" },
        platelets: { value: 230000.0, unit: "/uL" },
        hemoglobin: { value: 14.1, unit: "g/dL" },
      },
      vital_signs: {
        heart_rate: 72,
        blood_pressure_systolic: 124,
        blood_pressure_diastolic: 78,
      },
    },
  },
  {
    id: "P037",
    name: "Mei-Ling Zhou",
    dob: "1965-02-24",
    age: 61,
    sex: "F",
    cohort: "Cohort C - [4 A2A Pipelines Rejection] Unapproved Dose & Multi-Organ Conflict",
    diagnosis: "Stage IV Non-Small Cell Lung Carcinoma",
    creatinine: "CrCl 52 mL/min",
    trial_id: "NCT02415400",
    medications: ["Pembrolizumab 400mg IV Q3W", "Ketoconazole 400mg daily", "Prednisone 40mg daily"],
    clinical_data: {
      patient_id: "P037",
      name: "Mei-Ling Zhou",
      age: 61,
      sex: "female",
      diagnoses: ["Stage IV Non-Small Cell Lung Carcinoma", "Grade 3 Immune-Related Colitis"],
      medications: ["Pembrolizumab 400mg IV Q3W", "Ketoconazole 400mg daily", "Prednisone 40mg daily"],
      protocol_facts: {
        active_autoimmune_disease: true,
        systemic_immunosuppression: true,
      },
      lab_results: {
        ANC: { value: 1200.0, unit: "/uL" },
        platelets: { value: 85000.0, unit: "/uL" },
        creatinine_clearance: { value: 52.0, unit: "mL/min" },
        serum_creatinine: { value: 1.2, unit: "mg/dL" },
        ALT: { value: 75.0, unit: "U/L" },
        AST: { value: 68.0, unit: "U/L" },
      },
    },
  },
  {
    "id": "P038",
    "name": "Ananya Deshmukh",
    "dob": "1964-08-14",
    "age": 62,
    "sex": "",
    "cohort": "Cohort A - [G1 Ingress Failure] Missing Biological Sex",
    "diagnosis": "Non-valvular atrial fibrillation",
    "creatinine": "CrCl 68 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "Apixaban 5mg BID",
      "Lisinopril 10mg daily"
    ],
    "clinical_data": {
      "patient_id": "P038",
      "name": "Ananya Deshmukh",
      "dob": "1964-08-14",
      "birth_date": "1964-08-14",
      "age": 62,
      "sex": "",
      "cohort": "Cohort A - [G1 Ingress Failure] Missing Biological Sex",
      "diagnoses": [
        "Non-valvular atrial fibrillation",
        "Essential hypertension"
      ],
      "medications": [
        "Apixaban 5mg BID",
        "Lisinopril 10mg daily"
      ],
      "medical_history": [
        "Catheter ablation 2021",
        "Appendectomy 1995"
      ],
      "medical_history_narrative": "62-year-old presenting for antithrombotic trial intake with unrecorded biological sex.",
      "protocol_facts": {
        "oral_anticoagulation_required": true,
        "ongoing_bleeding": false,
        "days_since_major_bleed": null
      },
      "lab_results": {
        "creatinine_clearance": {
          "value": 68.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 1.0,
          "unit": "mg/dL"
        },
        "eGFR": {
          "value": 72.0,
          "unit": "mL/min/1.73m2"
        },
        "ALT": {
          "value": 24.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 22.0,
          "unit": "U/L"
        },
        "total_bilirubin": {
          "value": 0.8,
          "unit": "mg/dL"
        },
        "ANC": {
          "value": 4100.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 230000.0,
          "unit": "/uL"
        },
        "hemoglobin": {
          "value": 13.8,
          "unit": "g/dL"
        },
        "INR": {
          "value": 1.1,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 72,
        "blood_pressure_systolic": 126,
        "blood_pressure_diastolic": 78
      }
    }
  },
  {
    "id": "P039",
    "name": "Robert Chen",
    "dob": "Unrecorded",
    "age": 0,
    "sex": "M",
    "cohort": "Cohort B - [G1 Ingress Failure] Missing Patient Age",
    "diagnosis": "Diabetic nephropathy stage 3a",
    "creatinine": "CrCl 58 mL/min",
    "trial_id": "NCT00699998",
    "medications": [
      "Empagliflozin 10mg daily",
      "Metformin 500mg BID"
    ],
    "clinical_data": {
      "patient_id": "P039",
      "name": "Robert Chen",
      "dob": "Unrecorded",
      "birth_date": null,
      "age": 0,
      "sex": "male",
      "cohort": "Cohort B - [G1 Ingress Failure] Missing Patient Age",
      "diagnoses": [
        "Diabetic nephropathy stage 3a",
        "Type 2 diabetes mellitus"
      ],
      "medications": [
        "Empagliflozin 10mg daily",
        "Metformin 500mg BID"
      ],
      "medical_history": [
        "Type 2 diabetes for 12 years",
        "Laser photocoagulation 2018"
      ],
      "medical_history_narrative": "Male subject with diabetic nephropathy missing birth date and age records.",
      "protocol_facts": {
        "dialysis_required": false
      },
      "lab_results": {
        "creatinine_clearance": {
          "value": 58.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 1.3,
          "unit": "mg/dL"
        },
        "eGFR": {
          "value": 60.0,
          "unit": "mL/min/1.73m2"
        },
        "ALT": {
          "value": 28.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 25.0,
          "unit": "U/L"
        },
        "total_bilirubin": {
          "value": 0.7,
          "unit": "mg/dL"
        },
        "ANC": {
          "value": 4500.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 250000.0,
          "unit": "/uL"
        },
        "hemoglobin": {
          "value": 13.2,
          "unit": "g/dL"
        },
        "INR": {
          "value": 1.0,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 76,
        "blood_pressure_systolic": 130,
        "blood_pressure_diastolic": 82
      }
    }
  },
  {
    "id": "P040",
    "name": "Fatima Al-Mansoor",
    "dob": "Unrecorded",
    "age": 0,
    "sex": "",
    "cohort": "Cohort C - [G1 Ingress Failure] Missing Age & Sex (21 CFR 312.62)",
    "diagnosis": "Colorectal adenocarcinoma (Stage IIIA)",
    "creatinine": "CrCl 62 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "Capecitabine 1000mg BID",
      "Ondansetron 8mg PRN"
    ],
    "clinical_data": {
      "patient_id": "P040",
      "name": "Fatima Al-Mansoor",
      "dob": "Unrecorded",
      "birth_date": null,
      "age": 0,
      "sex": "",
      "cohort": "Cohort C - [G1 Ingress Failure] Missing Age & Sex (21 CFR 312.62)",
      "diagnoses": [
        "Colorectal adenocarcinoma (Stage IIIA)",
        "Anemia of chronic disease"
      ],
      "medications": [
        "Capecitabine 1000mg BID",
        "Ondansetron 8mg PRN"
      ],
      "medical_history": [
        "Partial colectomy 2023"
      ],
      "medical_history_narrative": "Oncology patient transferred from outside facility without demographic identity attributes.",
      "protocol_facts": {
        "active_autoimmune_disease": false,
        "systemic_immunosuppression": false
      },
      "lab_results": {
        "creatinine_clearance": {
          "value": 62.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 1.1,
          "unit": "mg/dL"
        },
        "eGFR": {
          "value": 68.0,
          "unit": "mL/min/1.73m2"
        },
        "ALT": {
          "value": 26.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 23.0,
          "unit": "U/L"
        },
        "total_bilirubin": {
          "value": 0.6,
          "unit": "mg/dL"
        },
        "ANC": {
          "value": 3600.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 210000.0,
          "unit": "/uL"
        },
        "hemoglobin": {
          "value": 11.2,
          "unit": "g/dL"
        },
        "INR": {
          "value": 1.1,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 78,
        "blood_pressure_systolic": 118,
        "blood_pressure_diastolic": 74
      }
    }
  },
  {
    "id": "P041",
    "name": "Vikram Malhotra",
    "dob": "1955-04-12",
    "age": 71,
    "sex": "M",
    "cohort": "Cohort B - [G2 Hard Boundary Breach] Catastrophic Renal Collapse",
    "diagnosis": "End-stage diabetic glomerulosclerosis",
    "creatinine": "CrCl 12 mL/min",
    "trial_id": "NCT00699998",
    "medications": [
      "Empagliflozin 10mg daily",
      "Furosemide 80mg daily",
      "Sodium bicarbonate 650mg TID"
    ],
    "clinical_data": {
      "patient_id": "P041",
      "name": "Vikram Malhotra",
      "dob": "1955-04-12",
      "birth_date": "1955-04-12",
      "age": 71,
      "sex": "male",
      "cohort": "Cohort B - [G2 Hard Boundary Breach] Catastrophic Renal Collapse",
      "diagnoses": [
        "End-stage diabetic glomerulosclerosis",
        "Severe metabolic acidosis"
      ],
      "medications": [
        "Empagliflozin 10mg daily",
        "Furosemide 80mg daily",
        "Sodium bicarbonate 650mg TID"
      ],
      "medical_history": [
        "Acute-on-chronic renal injury",
        "Hypertensive nephrosclerosis"
      ],
      "medical_history_narrative": "71-year-old male with acute renal collapse triggering G2 ESRD stopping rules.",
      "protocol_facts": {
        "dialysis_required": true
      },
      "lab_results": {
        "eGFR": {
          "value": 11.0,
          "unit": "mL/min/1.73m2"
        },
        "creatinine_clearance": {
          "value": 12.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 5.2,
          "unit": "mg/dL"
        },
        "ALT": {
          "value": 25.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 22.0,
          "unit": "U/L"
        },
        "total_bilirubin": {
          "value": 1.1,
          "unit": "mg/dL"
        },
        "ANC": {
          "value": 4200.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 180000.0,
          "unit": "/uL"
        },
        "hemoglobin": {
          "value": 8.9,
          "unit": "g/dL"
        },
        "INR": {
          "value": 1.2,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 84,
        "blood_pressure_systolic": 158,
        "blood_pressure_diastolic": 96
      }
    }
  },
  {
    "id": "P042",
    "name": "Zoe Washington",
    "dob": "1968-09-22",
    "age": 58,
    "sex": "F",
    "cohort": "Cohort B - [G2 Hard Boundary Breach] Severe Hyperbilirubinemia & Liver Collapse",
    "diagnosis": "Decompensated MASH cirrhosis with jaundice",
    "creatinine": "CrCl 54 mL/min",
    "trial_id": "NCT00809965",
    "medications": [
      "Pioglitazone 30mg daily",
      "Spironolactone 50mg daily",
      "Lactulose 20g daily"
    ],
    "clinical_data": {
      "patient_id": "P042",
      "name": "Zoe Washington",
      "dob": "1968-09-22",
      "birth_date": "1968-09-22",
      "age": 58,
      "sex": "female",
      "cohort": "Cohort B - [G2 Hard Boundary Breach] Severe Hyperbilirubinemia & Liver Collapse",
      "diagnoses": [
        "Decompensated MASH cirrhosis with jaundice",
        "Hepatic coagulopathy"
      ],
      "medications": [
        "Pioglitazone 30mg daily",
        "Spironolactone 50mg daily",
        "Lactulose 20g daily"
      ],
      "medical_history": [
        "Ascites requiring paracentesis 2023",
        "Portal hypertension"
      ],
      "medical_history_narrative": "58-year-old female with acute-on-chronic hepatic failure, icterus, and profound transaminitis.",
      "protocol_facts": {
        "prior_bleeding": false,
        "ongoing_bleeding": false
      },
      "lab_results": {
        "total_bilirubin": {
          "value": 6.8,
          "unit": "mg/dL"
        },
        "ALT": {
          "value": 310.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 285.0,
          "unit": "U/L"
        },
        "creatinine_clearance": {
          "value": 54.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 1.3,
          "unit": "mg/dL"
        },
        "eGFR": {
          "value": 56.0,
          "unit": "mL/min/1.73m2"
        },
        "ANC": {
          "value": 3500.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 92000.0,
          "unit": "/uL"
        },
        "hemoglobin": {
          "value": 10.8,
          "unit": "g/dL"
        },
        "INR": {
          "value": 2.1,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 88,
        "blood_pressure_systolic": 112,
        "blood_pressure_diastolic": 68
      }
    }
  },
  {
    "id": "P043",
    "name": "Suresh Patel",
    "dob": "1962-01-30",
    "age": 64,
    "sex": "M",
    "cohort": "Cohort C - [G2 Hard Boundary Breach] Severe Agranulocytosis & Marrow Failure",
    "diagnosis": "Metastatic NSCLC post-myeloablative chemo",
    "creatinine": "CrCl 65 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "Pembrolizumab 200mg IV Q3W",
      "Filgrastim 300mcg SubQ",
      "Cefepime 2g IV Q8H"
    ],
    "clinical_data": {
      "patient_id": "P043",
      "name": "Suresh Patel",
      "dob": "1962-01-30",
      "birth_date": "1962-01-30",
      "age": 64,
      "sex": "male",
      "cohort": "Cohort C - [G2 Hard Boundary Breach] Severe Agranulocytosis & Marrow Failure",
      "diagnoses": [
        "Metastatic NSCLC post-myeloablative chemo",
        "Febrile neutropenia"
      ],
      "medications": [
        "Pembrolizumab 200mg IV Q3W",
        "Filgrastim 300mcg SubQ",
        "Cefepime 2g IV Q8H"
      ],
      "medical_history": [
        "Carboplatin + Pemetrexed cycle 4 10 days ago"
      ],
      "medical_history_narrative": "64-year-old male with profound agranulocytosis triggering G2 safety stopping rule.",
      "protocol_facts": {
        "active_autoimmune_disease": false,
        "systemic_immunosuppression": false
      },
      "lab_results": {
        "ANC": {
          "value": 320.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 28000.0,
          "unit": "/uL"
        },
        "creatinine_clearance": {
          "value": 65.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 1.1,
          "unit": "mg/dL"
        },
        "eGFR": {
          "value": 70.0,
          "unit": "mL/min/1.73m2"
        },
        "ALT": {
          "value": 32.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 28.0,
          "unit": "U/L"
        },
        "total_bilirubin": {
          "value": 0.9,
          "unit": "mg/dL"
        },
        "hemoglobin": {
          "value": 8.4,
          "unit": "g/dL"
        },
        "INR": {
          "value": 1.1,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 102,
        "blood_pressure_systolic": 108,
        "blood_pressure_diastolic": 64
      }
    }
  },
  {
    "id": "P044",
    "name": "Claire Dubois",
    "dob": "1960-07-04",
    "age": 66,
    "sex": "F",
    "cohort": "Cohort A - [RAG Rule Violation] Massive Overdose (60 mg BID)",
    "diagnosis": "Non-valvular atrial fibrillation",
    "creatinine": "CrCl 70 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "Apixaban 60mg BID",
      "Atorvastatin 40mg daily"
    ],
    "clinical_data": {
      "patient_id": "P044",
      "name": "Claire Dubois",
      "dob": "1960-07-04",
      "birth_date": "1960-07-04",
      "age": 66,
      "sex": "female",
      "cohort": "Cohort A - [RAG Rule Violation] Massive Overdose (60 mg BID)",
      "diagnoses": [
        "Non-valvular atrial fibrillation",
        "Dyslipidemia"
      ],
      "medications": [
        "Apixaban 60mg BID",
        "Atorvastatin 40mg daily"
      ],
      "medical_history": [
        "Transient ischemic attack 2022",
        "Cholecystectomy 2014"
      ],
      "medical_history_narrative": "66-year-old female with unapproved 12-fold supratherapeutic prescription.",
      "protocol_facts": {
        "ongoing_bleeding": false,
        "days_since_major_bleed": null,
        "oral_anticoagulation_required": true
      },
      "lab_results": {
        "creatinine_clearance": {
          "value": 70.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 0.9,
          "unit": "mg/dL"
        },
        "eGFR": {
          "value": 75.0,
          "unit": "mL/min/1.73m2"
        },
        "ALT": {
          "value": 28.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 24.0,
          "unit": "U/L"
        },
        "total_bilirubin": {
          "value": 0.8,
          "unit": "mg/dL"
        },
        "ANC": {
          "value": 4200.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 240000.0,
          "unit": "/uL"
        },
        "hemoglobin": {
          "value": 14.1,
          "unit": "g/dL"
        },
        "INR": {
          "value": 1.1,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 70,
        "blood_pressure_systolic": 122,
        "blood_pressure_diastolic": 76
      }
    }
  },
  {
    "id": "P045",
    "name": "Tariq Mahmoud",
    "dob": "1957-03-19",
    "age": 69,
    "sex": "M",
    "cohort": "Cohort A - [RAG Rule Violation] Acute GI Bleed Washout (8 Days)",
    "diagnosis": "Atrial fibrillation post-ablation",
    "creatinine": "CrCl 58 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "Apixaban 5mg BID",
      "Pantoprazole 40mg daily"
    ],
    "clinical_data": {
      "patient_id": "P045",
      "name": "Tariq Mahmoud",
      "dob": "1957-03-19",
      "birth_date": "1957-03-19",
      "age": 69,
      "sex": "male",
      "cohort": "Cohort A - [RAG Rule Violation] Acute GI Bleed Washout (8 Days)",
      "diagnoses": [
        "Atrial fibrillation post-ablation",
        "Recent peptic ulcer hemorrhage"
      ],
      "medications": [
        "Apixaban 5mg BID",
        "Pantoprazole 40mg daily"
      ],
      "medical_history": [
        "Acute lower GI hemorrhage requiring 2 units PRBC 8 days ago"
      ],
      "medical_history_narrative": "69-year-old male with recent major bleed 8 days prior, violating 30-day washout rule.",
      "protocol_facts": {
        "ongoing_bleeding": true,
        "days_since_major_bleed": 8,
        "oral_anticoagulation_required": true
      },
      "lab_results": {
        "creatinine_clearance": {
          "value": 58.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 1.2,
          "unit": "mg/dL"
        },
        "eGFR": {
          "value": 64.0,
          "unit": "mL/min/1.73m2"
        },
        "ALT": {
          "value": 30.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 26.0,
          "unit": "U/L"
        },
        "total_bilirubin": {
          "value": 1.0,
          "unit": "mg/dL"
        },
        "ANC": {
          "value": 4600.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 215000.0,
          "unit": "/uL"
        },
        "hemoglobin": {
          "value": 10.4,
          "unit": "g/dL"
        },
        "INR": {
          "value": 1.1,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 74,
        "blood_pressure_systolic": 116,
        "blood_pressure_diastolic": 72
      }
    }
  },
  {
    "id": "P046",
    "name": "Devraj Sengupta",
    "dob": "1953-12-08",
    "age": 73,
    "sex": "M",
    "cohort": "Cohort B - [RAG Rule Violation] Renal Trial Floor Exclusion (CrCl 22 mL/min)",
    "diagnosis": "Diabetic nephropathy with reduced filtration",
    "creatinine": "CrCl 22 mL/min",
    "trial_id": "NCT00699998",
    "medications": [
      "Empagliflozin 10mg daily",
      "Amlodipine 5mg daily"
    ],
    "clinical_data": {
      "patient_id": "P046",
      "name": "Devraj Sengupta",
      "dob": "1953-12-08",
      "birth_date": "1953-12-08",
      "age": 73,
      "sex": "male",
      "cohort": "Cohort B - [RAG Rule Violation] Renal Trial Floor Exclusion (CrCl 22 mL/min)",
      "diagnoses": [
        "Diabetic nephropathy with reduced filtration",
        "Hypertension"
      ],
      "medications": [
        "Empagliflozin 10mg daily",
        "Amlodipine 5mg daily"
      ],
      "medical_history": [
        "Type 2 diabetes for 20 years",
        "Coronary artery bypass 2012"
      ],
      "medical_history_narrative": "73-year-old male with CrCl 22 mL/min below the >= 30 mL/min protocol floor.",
      "protocol_facts": {
        "dialysis_required": false
      },
      "lab_results": {
        "creatinine_clearance": {
          "value": 22.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 2.4,
          "unit": "mg/dL"
        },
        "eGFR": {
          "value": 24.0,
          "unit": "mL/min/1.73m2"
        },
        "ALT": {
          "value": 22.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 20.0,
          "unit": "U/L"
        },
        "total_bilirubin": {
          "value": 0.7,
          "unit": "mg/dL"
        },
        "ANC": {
          "value": 3900.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 195000.0,
          "unit": "/uL"
        },
        "hemoglobin": {
          "value": 11.5,
          "unit": "g/dL"
        },
        "INR": {
          "value": 1.0,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 68,
        "blood_pressure_systolic": 134,
        "blood_pressure_diastolic": 80
      }
    }
  },
  {
    "id": "P047",
    "name": "Hannah Rosen",
    "dob": "1967-11-15",
    "age": 59,
    "sex": "F",
    "cohort": "Cohort C - [RAG Rule Violation] Active Autoimmune Disease Exclusion",
    "diagnosis": "Colorectal carcinoma",
    "creatinine": "CrCl 65 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "Pembrolizumab 200mg IV Q3W",
      "Prednisone 30mg daily",
      "Mesalamine 2.4g daily"
    ],
    "clinical_data": {
      "patient_id": "P047",
      "name": "Hannah Rosen",
      "dob": "1967-11-15",
      "birth_date": "1967-11-15",
      "age": 59,
      "sex": "female",
      "cohort": "Cohort C - [RAG Rule Violation] Active Autoimmune Disease Exclusion",
      "diagnoses": [
        "Colorectal carcinoma",
        "Active Crohn's colitis on systemic steroid"
      ],
      "medications": [
        "Pembrolizumab 200mg IV Q3W",
        "Prednisone 30mg daily",
        "Mesalamine 2.4g daily"
      ],
      "medical_history": [
        "Crohn's disease for 8 years",
        "Right hemicolectomy 2022"
      ],
      "medical_history_narrative": "59-year-old female with active autoimmune bowel disease contraindicating checkpoint inhibitor.",
      "protocol_facts": {
        "active_autoimmune_disease": true,
        "systemic_immunosuppression": true
      },
      "lab_results": {
        "creatinine_clearance": {
          "value": 65.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 1.0,
          "unit": "mg/dL"
        },
        "eGFR": {
          "value": 72.0,
          "unit": "mL/min/1.73m2"
        },
        "ALT": {
          "value": 26.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 24.0,
          "unit": "U/L"
        },
        "total_bilirubin": {
          "value": 0.8,
          "unit": "mg/dL"
        },
        "ANC": {
          "value": 3900.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 230000.0,
          "unit": "/uL"
        },
        "hemoglobin": {
          "value": 12.8,
          "unit": "g/dL"
        },
        "INR": {
          "value": 1.0,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 76,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 75
      }
    }
  },
  {
    "id": "P048",
    "name": "Carlos Mendoza",
    "dob": "1963-06-25",
    "age": 63,
    "sex": "M",
    "cohort": "Cohort A - [A2A Safety Rejection] Fatal Dual CYP3A4 / P-gp Interaction",
    "diagnosis": "Non-valvular atrial fibrillation",
    "creatinine": "CrCl 68 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "Apixaban 5mg BID",
      "Ketoconazole 400mg daily",
      "Clarithromycin 500mg BID"
    ],
    "clinical_data": {
      "patient_id": "P048",
      "name": "Carlos Mendoza",
      "dob": "1963-06-25",
      "birth_date": "1963-06-25",
      "age": 63,
      "sex": "male",
      "cohort": "Cohort A - [A2A Safety Rejection] Fatal Dual CYP3A4 / P-gp Interaction",
      "diagnoses": [
        "Non-valvular atrial fibrillation",
        "Systemic fungal infection"
      ],
      "medications": [
        "Apixaban 5mg BID",
        "Ketoconazole 400mg daily",
        "Clarithromycin 500mg BID"
      ],
      "medical_history": [
        "Histoplasmosis 2024",
        "Coronary angioplasty 2019"
      ],
      "medical_history_narrative": "63-year-old male with severe pharmacokinetic CYP3A4 + P-gp drug interaction resulting in anticoagulant toxicity.",
      "protocol_facts": {
        "ongoing_bleeding": false,
        "days_since_major_bleed": null,
        "oral_anticoagulation_required": true
      },
      "lab_results": {
        "creatinine_clearance": {
          "value": 68.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 1.1,
          "unit": "mg/dL"
        },
        "eGFR": {
          "value": 74.0,
          "unit": "mL/min/1.73m2"
        },
        "ALT": {
          "value": 35.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 30.0,
          "unit": "U/L"
        },
        "total_bilirubin": {
          "value": 1.1,
          "unit": "mg/dL"
        },
        "ANC": {
          "value": 4200.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 220000.0,
          "unit": "/uL"
        },
        "hemoglobin": {
          "value": 14.2,
          "unit": "g/dL"
        },
        "INR": {
          "value": 1.2,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 78,
        "blood_pressure_systolic": 128,
        "blood_pressure_diastolic": 82
      }
    }
  },
  {
    "id": "P049",
    "name": "Aditi Joshi",
    "dob": "1971-08-30",
    "age": 55,
    "sex": "F",
    "cohort": "Cohort C - [A2A Financial Denial] Unapproved Biologic Off-Label Billing ($52,800)",
    "diagnosis": "Refractory leiomyosarcoma (exploratory off-label arm)",
    "creatinine": "CrCl 72 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "Pembrolizumab 200mg IV Q3W",
      "Amlodipine 5mg daily"
    ],
    "clinical_data": {
      "patient_id": "P049",
      "name": "Aditi Joshi",
      "dob": "1971-08-30",
      "birth_date": "1971-08-30",
      "age": 55,
      "sex": "female",
      "cohort": "Cohort C - [A2A Financial Denial] Unapproved Biologic Off-Label Billing ($52,800)",
      "diagnoses": [
        "Refractory leiomyosarcoma (exploratory off-label arm)",
        "Hypertension"
      ],
      "medications": [
        "Pembrolizumab 200mg IV Q3W",
        "Amlodipine 5mg daily"
      ],
      "medical_history": [
        "Surgical resection of pelvic sarcoma 2021"
      ],
      "medical_history_narrative": "55-year-old female in exploratory off-label cohort resulting in complete sponsor reimbursement denial ($52,800 liability).",
      "protocol_facts": {
        "active_autoimmune_disease": false,
        "systemic_immunosuppression": false
      },
      "lab_results": {
        "creatinine_clearance": {
          "value": 72.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 0.9,
          "unit": "mg/dL"
        },
        "eGFR": {
          "value": 78.0,
          "unit": "mL/min/1.73m2"
        },
        "ALT": {
          "value": 25.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 22.0,
          "unit": "U/L"
        },
        "total_bilirubin": {
          "value": 0.7,
          "unit": "mg/dL"
        },
        "ANC": {
          "value": 4500.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 260000.0,
          "unit": "/uL"
        },
        "hemoglobin": {
          "value": 13.5,
          "unit": "g/dL"
        },
        "INR": {
          "value": 1.0,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 72,
        "blood_pressure_systolic": 124,
        "blood_pressure_diastolic": 76
      }
    }
  },
  {
    "id": "P050",
    "name": "Benjamin Sterling",
    "dob": "1952-05-14",
    "age": 74,
    "sex": "M",
    "cohort": "Cohort A - [A2A Multi-Specialist Dissent] Triple Antiplatelet Hemorrhage Hazard & Prior Auth",
    "diagnosis": "Post-PCI with complex bifurcation stenting",
    "creatinine": "CrCl 52 mL/min",
    "trial_id": "NCT00781573",
    "medications": [
      "Apixaban 5mg BID",
      "Aspirin 81mg daily",
      "Clopidogrel 75mg daily",
      "Ticagrelor 90mg BID"
    ],
    "clinical_data": {
      "patient_id": "P050",
      "name": "Benjamin Sterling",
      "dob": "1952-05-14",
      "birth_date": "1952-05-14",
      "age": 74,
      "sex": "male",
      "cohort": "Cohort A - [A2A Multi-Specialist Dissent] Triple Antiplatelet Hemorrhage Hazard & Prior Auth",
      "diagnoses": [
        "Post-PCI with complex bifurcation stenting",
        "Atrial fibrillation"
      ],
      "medications": [
        "Apixaban 5mg BID",
        "Aspirin 81mg daily",
        "Clopidogrel 75mg daily",
        "Ticagrelor 90mg BID"
      ],
      "medical_history": [
        "DES placement LAD and LCx 2024",
        "Hypertension 25 years"
      ],
      "medical_history_narrative": "74-year-old male with unapproved triple antiplatelet combination causing safety dissent and $6,400 billing dispute.",
      "protocol_facts": {
        "pci_pathway": true,
        "days_since_PCI": 14,
        "ongoing_bleeding": false,
        "oral_anticoagulation_required": true
      },
      "lab_results": {
        "creatinine_clearance": {
          "value": 52.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 1.3,
          "unit": "mg/dL"
        },
        "eGFR": {
          "value": 55.0,
          "unit": "mL/min/1.73m2"
        },
        "ALT": {
          "value": 30.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 28.0,
          "unit": "U/L"
        },
        "total_bilirubin": {
          "value": 0.9,
          "unit": "mg/dL"
        },
        "ANC": {
          "value": 3800.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 155000.0,
          "unit": "/uL"
        },
        "hemoglobin": {
          "value": 12.9,
          "unit": "g/dL"
        },
        "INR": {
          "value": 1.1,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 74,
        "blood_pressure_systolic": 132,
        "blood_pressure_diastolic": 82
      }
    }
  },
  {
    "id": "P051",
    "name": "Lakshmi Ramanathan",
    "dob": "1961-09-17",
    "age": 65,
    "sex": "F",
    "cohort": "Cohort A - [All Pass: Unanimous Justified] Standard Atrial Fibrillation",
    "diagnosis": "Non-valvular atrial fibrillation post-flutter ablation",
    "creatinine": "CrCl 74 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "Apixaban 5mg BID",
      "Metoprolol succinate 50mg daily"
    ],
    "clinical_data": {
      "patient_id": "P051",
      "name": "Lakshmi Ramanathan",
      "dob": "1961-09-17",
      "birth_date": "1961-09-17",
      "age": 65,
      "sex": "female",
      "cohort": "Cohort A - [All Pass: Unanimous Justified] Standard Atrial Fibrillation",
      "diagnoses": [
        "Non-valvular atrial fibrillation post-flutter ablation"
      ],
      "medications": [
        "Apixaban 5mg BID",
        "Metoprolol succinate 50mg daily"
      ],
      "medical_history": [
        "Atrial flutter ablation 2023"
      ],
      "medical_history_narrative": "65-year-old female fully eligible for antithrombotic arm. All guardrails and agents unanimous pass.",
      "protocol_facts": {
        "oral_anticoagulation_required": true,
        "ongoing_bleeding": false,
        "days_since_major_bleed": null,
        "history_of_intracranial_hemorrhage": false
      },
      "lab_results": {
        "creatinine_clearance": {
          "value": 74.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 0.9,
          "unit": "mg/dL"
        },
        "eGFR": {
          "value": 78.0,
          "unit": "mL/min/1.73m2"
        },
        "ALT": {
          "value": 22.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 20.0,
          "unit": "U/L"
        },
        "total_bilirubin": {
          "value": 0.7,
          "unit": "mg/dL"
        },
        "ANC": {
          "value": 4400.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 245000.0,
          "unit": "/uL"
        },
        "hemoglobin": {
          "value": 14.0,
          "unit": "g/dL"
        },
        "INR": {
          "value": 1.1,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 68,
        "blood_pressure_systolic": 118,
        "blood_pressure_diastolic": 74
      }
    }
  },
  {
    "id": "P052",
    "name": "Alexander Wright",
    "dob": "1969-02-11",
    "age": 57,
    "sex": "M",
    "cohort": "Cohort C - [All Pass: Unanimous Justified] Solid Tumor Oncology",
    "diagnosis": "Stage IIIB Non-Small Cell Lung Carcinoma (PD-L1 > 50%)",
    "creatinine": "CrCl 75 mL/min",
    "trial_id": "NCT02415400",
    "medications": [
      "Pembrolizumab 200mg IV Q3W",
      "Ondansetron 8mg PRN"
    ],
    "clinical_data": {
      "patient_id": "P052",
      "name": "Alexander Wright",
      "dob": "1969-02-11",
      "birth_date": "1969-02-11",
      "age": 57,
      "sex": "male",
      "cohort": "Cohort C - [All Pass: Unanimous Justified] Solid Tumor Oncology",
      "diagnoses": [
        "Stage IIIB Non-Small Cell Lung Carcinoma (PD-L1 > 50%)"
      ],
      "medications": [
        "Pembrolizumab 200mg IV Q3W",
        "Ondansetron 8mg PRN"
      ],
      "medical_history": [
        "Lobectomy 2022",
        "No autoimmune history"
      ],
      "medical_history_narrative": "57-year-old male with intact bone marrow reserve and organ clearance, fully protocol-compliant.",
      "protocol_facts": {
        "active_autoimmune_disease": false,
        "systemic_immunosuppression": false
      },
      "lab_results": {
        "ANC": {
          "value": 4200.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 260000.0,
          "unit": "/uL"
        },
        "creatinine_clearance": {
          "value": 75.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 0.95,
          "unit": "mg/dL"
        },
        "eGFR": {
          "value": 80.0,
          "unit": "mL/min/1.73m2"
        },
        "ALT": {
          "value": 24.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 21.0,
          "unit": "U/L"
        },
        "total_bilirubin": {
          "value": 0.8,
          "unit": "mg/dL"
        },
        "hemoglobin": {
          "value": 14.5,
          "unit": "g/dL"
        },
        "INR": {
          "value": 1.0,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 72,
        "blood_pressure_systolic": 122,
        "blood_pressure_diastolic": 76
      }
    }
  },
  {
    "id": "P053",
    "name": "Sneha Kulkarni",
    "dob": "1975-07-23",
    "age": 51,
    "sex": "F",
    "cohort": "Cohort B - [All Pass: Unanimous Justified] Metabolic NAFLD / MASH",
    "diagnosis": "MASH with Stage F2 fibrosis",
    "creatinine": "CrCl 78 mL/min",
    "trial_id": "NCT00809965",
    "medications": [
      "Pioglitazone 30mg daily",
      "Vitamin E 800 IU daily"
    ],
    "clinical_data": {
      "patient_id": "P053",
      "name": "Sneha Kulkarni",
      "dob": "1975-07-23",
      "birth_date": "1975-07-23",
      "age": 51,
      "sex": "female",
      "cohort": "Cohort B - [All Pass: Unanimous Justified] Metabolic NAFLD / MASH",
      "diagnoses": [
        "MASH with Stage F2 fibrosis",
        "Impaired fasting glucose"
      ],
      "medications": [
        "Pioglitazone 30mg daily",
        "Vitamin E 800 IU daily"
      ],
      "medical_history": [
        "Liver biopsy confirmed steatohepatitis 2023"
      ],
      "medical_history_narrative": "51-year-old female meeting all MASH protocol inclusion criteria with normal baseline transaminases.",
      "protocol_facts": {
        "prior_bleeding": false,
        "ongoing_bleeding": false
      },
      "lab_results": {
        "ALT": {
          "value": 34.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 29.0,
          "unit": "U/L"
        },
        "total_bilirubin": {
          "value": 0.9,
          "unit": "mg/dL"
        },
        "creatinine_clearance": {
          "value": 78.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 0.85,
          "unit": "mg/dL"
        },
        "eGFR": {
          "value": 82.0,
          "unit": "mL/min/1.73m2"
        },
        "ANC": {
          "value": 4100.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 240000.0,
          "unit": "/uL"
        },
        "hemoglobin": {
          "value": 13.6,
          "unit": "g/dL"
        },
        "INR": {
          "value": 1.0,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 70,
        "blood_pressure_systolic": 118,
        "blood_pressure_diastolic": 72
      }
    }
  },
  {
    "id": "P054",
    "name": "David Kim",
    "dob": "1963-10-05",
    "age": 63,
    "sex": "M",
    "cohort": "Cohort B - [All Pass: Unanimous Justified] Renal SGLT2i Stratification",
    "diagnosis": "Diabetic nephropathy stage 3a (preserved eGFR)",
    "creatinine": "CrCl 62 mL/min",
    "trial_id": "NCT00699998",
    "medications": [
      "Empagliflozin 10mg daily",
      "Losartan 50mg daily"
    ],
    "clinical_data": {
      "patient_id": "P054",
      "name": "David Kim",
      "dob": "1963-10-05",
      "birth_date": "1963-10-05",
      "age": 63,
      "sex": "male",
      "cohort": "Cohort B - [All Pass: Unanimous Justified] Renal SGLT2i Stratification",
      "diagnoses": [
        "Diabetic nephropathy stage 3a (preserved eGFR)",
        "Hypertension"
      ],
      "medications": [
        "Empagliflozin 10mg daily",
        "Losartan 50mg daily"
      ],
      "medical_history": [
        "Type 2 diabetes 14 years",
        "No cardiovascular events"
      ],
      "medical_history_narrative": "63-year-old male with preserved filtration conforming to SGLT2i protocol eligibility.",
      "protocol_facts": {
        "dialysis_required": false
      },
      "lab_results": {
        "eGFR": {
          "value": 58.0,
          "unit": "mL/min/1.73m2"
        },
        "creatinine_clearance": {
          "value": 62.0,
          "unit": "mL/min"
        },
        "serum_creatinine": {
          "value": 1.2,
          "unit": "mg/dL"
        },
        "ALT": {
          "value": 23.0,
          "unit": "U/L"
        },
        "AST": {
          "value": 21.0,
          "unit": "U/L"
        },
        "total_bilirubin": {
          "value": 0.8,
          "unit": "mg/dL"
        },
        "ANC": {
          "value": 4300.0,
          "unit": "/uL"
        },
        "platelets": {
          "value": 235000.0,
          "unit": "/uL"
        },
        "hemoglobin": {
          "value": 14.1,
          "unit": "g/dL"
        },
        "INR": {
          "value": 1.0,
          "unit": "ratio"
        }
      },
      "vital_signs": {
        "heart_rate": 72,
        "blood_pressure_systolic": 126,
        "blood_pressure_diastolic": 78
      }
    }
  },
]

export const PROTOCOLS = [
  "NCT02415400 - Phase II Antithrombotic Trial (Arm A: Apixaban 5mg BID)",
  "NCT02415400 - Cohort C Solid Tumor Oncology (Pembrolizumab 200mg Q3W)",
  "NCT00781573 - Post-PCI Dual Therapy Protocol (Arm A)",
  "NCT00699998 - Renal Stratification SGLT2i Study (Cohort B)",
  "NCT00809965 - NAFLD / MASH Dose Escalation Protocol (Cohort B)",
  "FDA-CTP-2024-1187 (Phase II Renal Safety)",
  "FDA-CTP-2023-0941 (Phase I Dose Finding)",
]

export type AgentStatus = "pending" | "processing" | "completed"

export type AgentCard = {
  name: string
  status: AgentStatus
  description: string
  callout: string
  subtext?: string
  latency?: string
  confidence?: string
}

export const AGENTS: AgentCard[] = [
  {
    name: "Protocol Compliance Agent",
    status: "pending",
    description: "Validates telemetry against FDA inclusion/exclusion criteria.",
    callout: ".",
    latency: "",
    confidence: "",
  },
  {
    name: "Financial Risk Agent",
    status: "pending",
    description: "Projects reimbursement exposure and SAE liability.",
    callout: "",
    latency: "",
    confidence: "",
  },
  {
    name: "Safety & Toxicity Agent",
    status: "pending",
    description: "Evaluates drug-drug interactions & metabolic clearance markers.",
    callout: "",
    latency: "",
    confidence: "",
  },
  {
    name: "Arbitration Reducer",
    status: "pending",
    description: "Reconciles parallel agent inputs into a single consensus recommendation.",
    callout: ".",
    subtext: "",
  },
]
