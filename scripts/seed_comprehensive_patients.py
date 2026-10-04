"""
Script to synthesize 17 new comprehensive clinical patients (P038 - P054)
covering all permutations of:
  - Guardrail-1 (Accept vs Reject on missing demographics)
  - Guardrail-2 (Accept vs Reject on catastrophic boundary breaches)
  - RAG Protocol Rules (Accept vs Decline on overdose, washout, renal floor, autoimmune)
  - 4 A2A Pipelines (Accept vs Decline on DDI safety, billing exposure, multi-agent dissent)
  - All Pass / Unanimous Consensus Justified across all 4 trial cohorts
"""

import json
import os
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

NEW_PATIENTS = [
    # -------------------------------------------------------------
    # Category 1: G1 REJECT (Ingress Demographic Integrity Failure)
    # -------------------------------------------------------------
    {
        "patient_id": "P038",
        "name": "Ananya Deshmukh",
        "assigned_demo_trial_id": "NCT02415400",
        "cohort": "Cohort A - [G1 Ingress Failure] Missing Biological Sex",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P038",
            "name": "Ananya Deshmukh",
            "dob": "1964-08-14",
            "birth_date": "1964-08-14",
            "age": 62,
            "sex": "",  # Empty string triggers Guardrail-1
            "cohort": "Cohort A - [G1 Ingress Failure] Missing Biological Sex",
            "diagnoses": ["Non-valvular atrial fibrillation", "Essential hypertension"],
            "medications": ["Apixaban 5mg BID", "Lisinopril 10mg daily"],
            "medical_history": ["Catheter ablation 2021", "Appendectomy 1995"],
            "medical_history_narrative": "62-year-old presenting for antithrombotic trial intake with unrecorded biological sex.",
            "protocol_facts": {
                "oral_anticoagulation_required": True,
                "ongoing_bleeding": False,
                "days_since_major_bleed": None,
            },
            "lab_results": {
                "creatinine_clearance": {"value": 68.0, "unit": "mL/min"},
                "serum_creatinine": {"value": 1.0, "unit": "mg/dL"},
                "eGFR": {"value": 72.0, "unit": "mL/min/1.73m2"},
                "ALT": {"value": 24.0, "unit": "U/L"},
                "AST": {"value": 22.0, "unit": "U/L"},
                "total_bilirubin": {"value": 0.8, "unit": "mg/dL"},
                "ANC": {"value": 4100.0, "unit": "/uL"},
                "platelets": {"value": 230000.0, "unit": "/uL"},
                "hemoglobin": {"value": 13.8, "unit": "g/dL"},
                "INR": {"value": 1.1, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 72,
                "blood_pressure_systolic": 126,
                "blood_pressure_diastolic": 78,
            },
        },
    },
    {
        "patient_id": "P039",
        "name": "Robert Chen",
        "assigned_demo_trial_id": "NCT00699998",
        "cohort": "Cohort B - [G1 Ingress Failure] Missing Patient Age",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P039",
            "name": "Robert Chen",
            "dob": "Unrecorded",
            "birth_date": None,
            "age": 0,  # 0 / null triggers Guardrail-1
            "sex": "male",
            "cohort": "Cohort B - [G1 Ingress Failure] Missing Patient Age",
            "diagnoses": ["Diabetic nephropathy stage 3a", "Type 2 diabetes mellitus"],
            "medications": ["Empagliflozin 10mg daily", "Metformin 500mg BID"],
            "medical_history": ["Type 2 diabetes for 12 years", "Laser photocoagulation 2018"],
            "medical_history_narrative": "Male subject with diabetic nephropathy missing birth date and age records.",
            "protocol_facts": {
                "dialysis_required": False,
            },
            "lab_results": {
                "creatinine_clearance": {"value": 58.0, "unit": "mL/min"},
                "serum_creatinine": {"value": 1.3, "unit": "mg/dL"},
                "eGFR": {"value": 60.0, "unit": "mL/min/1.73m2"},
                "ALT": {"value": 28.0, "unit": "U/L"},
                "AST": {"value": 25.0, "unit": "U/L"},
                "total_bilirubin": {"value": 0.7, "unit": "mg/dL"},
                "ANC": {"value": 4500.0, "unit": "/uL"},
                "platelets": {"value": 250000.0, "unit": "/uL"},
                "hemoglobin": {"value": 13.2, "unit": "g/dL"},
                "INR": {"value": 1.0, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 76,
                "blood_pressure_systolic": 130,
                "blood_pressure_diastolic": 82,
            },
        },
    },
    {
        "patient_id": "P040",
        "name": "Fatima Al-Mansoor",
        "assigned_demo_trial_id": "NCT02415400",
        "cohort": "Cohort C - [G1 Ingress Failure] Missing Age & Sex (21 CFR 312.62)",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P040",
            "name": "Fatima Al-Mansoor",
            "dob": "Unrecorded",
            "birth_date": None,
            "age": 0,
            "sex": "",
            "cohort": "Cohort C - [G1 Ingress Failure] Missing Age & Sex (21 CFR 312.62)",
            "diagnoses": ["Colorectal adenocarcinoma (Stage IIIA)", "Anemia of chronic disease"],
            "medications": ["Capecitabine 1000mg BID", "Ondansetron 8mg PRN"],
            "medical_history": ["Partial colectomy 2023"],
            "medical_history_narrative": "Oncology patient transferred from outside facility without demographic identity attributes.",
            "protocol_facts": {
                "active_autoimmune_disease": False,
                "systemic_immunosuppression": False,
            },
            "lab_results": {
                "creatinine_clearance": {"value": 62.0, "unit": "mL/min"},
                "serum_creatinine": {"value": 1.1, "unit": "mg/dL"},
                "eGFR": {"value": 68.0, "unit": "mL/min/1.73m2"},
                "ALT": {"value": 26.0, "unit": "U/L"},
                "AST": {"value": 23.0, "unit": "U/L"},
                "total_bilirubin": {"value": 0.6, "unit": "mg/dL"},
                "ANC": {"value": 3600.0, "unit": "/uL"},
                "platelets": {"value": 210000.0, "unit": "/uL"},
                "hemoglobin": {"value": 11.2, "unit": "g/dL"},
                "INR": {"value": 1.1, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 78,
                "blood_pressure_systolic": 118,
                "blood_pressure_diastolic": 74,
            },
        },
    },

    # -------------------------------------------------------------
    # Category 2: G1 ACCEPT, G2 REJECT (Hard Boundary Breaches)
    # -------------------------------------------------------------
    {
        "patient_id": "P041",
        "name": "Vikram Malhotra",
        "assigned_demo_trial_id": "NCT00699998",
        "cohort": "Cohort B - [G2 Hard Boundary Breach] Catastrophic Renal Collapse",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P041",
            "name": "Vikram Malhotra",
            "dob": "1955-04-12",
            "birth_date": "1955-04-12",
            "age": 71,
            "sex": "male",
            "cohort": "Cohort B - [G2 Hard Boundary Breach] Catastrophic Renal Collapse",
            "diagnoses": ["End-stage diabetic glomerulosclerosis", "Severe metabolic acidosis"],
            "medications": ["Empagliflozin 10mg daily", "Furosemide 80mg daily", "Sodium bicarbonate 650mg TID"],
            "medical_history": ["Acute-on-chronic renal injury", "Hypertensive nephrosclerosis"],
            "medical_history_narrative": "71-year-old male with acute renal collapse triggering G2 ESRD stopping rules.",
            "protocol_facts": {
                "dialysis_required": True,
            },
            "lab_results": {
                "eGFR": {"value": 11.0, "unit": "mL/min/1.73m2"},  # < 15.0 G2 Boundary Breach
                "creatinine_clearance": {"value": 12.0, "unit": "mL/min"},
                "serum_creatinine": {"value": 5.2, "unit": "mg/dL"},
                "ALT": {"value": 25.0, "unit": "U/L"},
                "AST": {"value": 22.0, "unit": "U/L"},
                "total_bilirubin": {"value": 1.1, "unit": "mg/dL"},
                "ANC": {"value": 4200.0, "unit": "/uL"},
                "platelets": {"value": 180000.0, "unit": "/uL"},
                "hemoglobin": {"value": 8.9, "unit": "g/dL"},
                "INR": {"value": 1.2, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 84,
                "blood_pressure_systolic": 158,
                "blood_pressure_diastolic": 96,
            },
        },
    },
    {
        "patient_id": "P042",
        "name": "Zoe Washington",
        "assigned_demo_trial_id": "NCT00809965",
        "cohort": "Cohort B - [G2 Hard Boundary Breach] Severe Hyperbilirubinemia & Liver Collapse",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P042",
            "name": "Zoe Washington",
            "dob": "1968-09-22",
            "birth_date": "1968-09-22",
            "age": 58,
            "sex": "female",
            "cohort": "Cohort B - [G2 Hard Boundary Breach] Severe Hyperbilirubinemia & Liver Collapse",
            "diagnoses": ["Decompensated MASH cirrhosis with jaundice", "Hepatic coagulopathy"],
            "medications": ["Pioglitazone 30mg daily", "Spironolactone 50mg daily", "Lactulose 20g daily"],
            "medical_history": ["Ascites requiring paracentesis 2023", "Portal hypertension"],
            "medical_history_narrative": "58-year-old female with acute-on-chronic hepatic failure, icterus, and profound transaminitis.",
            "protocol_facts": {
                "prior_bleeding": False,
                "ongoing_bleeding": False,
            },
            "lab_results": {
                "total_bilirubin": {"value": 6.8, "unit": "mg/dL"},  # > 4.0 G2 Boundary Breach
                "ALT": {"value": 310.0, "unit": "U/L"},             # > 200.0 G2 Boundary Breach
                "AST": {"value": 285.0, "unit": "U/L"},             # > 200.0 G2 Boundary Breach
                "creatinine_clearance": {"value": 54.0, "unit": "mL/min"},
                "serum_creatinine": {"value": 1.3, "unit": "mg/dL"},
                "eGFR": {"value": 56.0, "unit": "mL/min/1.73m2"},
                "ANC": {"value": 3500.0, "unit": "/uL"},
                "platelets": {"value": 92000.0, "unit": "/uL"},
                "hemoglobin": {"value": 10.8, "unit": "g/dL"},
                "INR": {"value": 2.1, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 88,
                "blood_pressure_systolic": 112,
                "blood_pressure_diastolic": 68,
            },
        },
    },
    {
        "patient_id": "P043",
        "name": "Suresh Patel",
        "assigned_demo_trial_id": "NCT02415400",
        "cohort": "Cohort C - [G2 Hard Boundary Breach] Severe Agranulocytosis & Marrow Failure",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P043",
            "name": "Suresh Patel",
            "dob": "1962-01-30",
            "birth_date": "1962-01-30",
            "age": 64,
            "sex": "male",
            "cohort": "Cohort C - [G2 Hard Boundary Breach] Severe Agranulocytosis & Marrow Failure",
            "diagnoses": ["Metastatic NSCLC post-myeloablative chemo", "Febrile neutropenia"],
            "medications": ["Pembrolizumab 200mg IV Q3W", "Filgrastim 300mcg SubQ", "Cefepime 2g IV Q8H"],
            "medical_history": ["Carboplatin + Pemetrexed cycle 4 10 days ago"],
            "medical_history_narrative": "64-year-old male with profound agranulocytosis triggering G2 safety stopping rule.",
            "protocol_facts": {
                "active_autoimmune_disease": False,
                "systemic_immunosuppression": False,
            },
            "lab_results": {
                "ANC": {"value": 320.0, "unit": "/uL"},             # < 500.0 G2 Boundary Breach
                "platelets": {"value": 28000.0, "unit": "/uL"},
                "creatinine_clearance": {"value": 65.0, "unit": "mL/min"},
                "serum_creatinine": {"value": 1.1, "unit": "mg/dL"},
                "eGFR": {"value": 70.0, "unit": "mL/min/1.73m2"},
                "ALT": {"value": 32.0, "unit": "U/L"},
                "AST": {"value": 28.0, "unit": "U/L"},
                "total_bilirubin": {"value": 0.9, "unit": "mg/dL"},
                "hemoglobin": {"value": 8.4, "unit": "g/dL"},
                "INR": {"value": 1.1, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 102,
                "blood_pressure_systolic": 108,
                "blood_pressure_diastolic": 64,
            },
        },
    },

    # -------------------------------------------------------------
    # Category 3: G1 ACCEPT, G2 ACCEPT, RAG DECLINE (Protocol Rules)
    # -------------------------------------------------------------
    {
        "patient_id": "P044",
        "name": "Claire Dubois",
        "assigned_demo_trial_id": "NCT02415400",
        "cohort": "Cohort A - [RAG Rule Violation] Massive Overdose (60 mg BID)",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P044",
            "name": "Claire Dubois",
            "dob": "1960-07-04",
            "birth_date": "1960-07-04",
            "age": 66,
            "sex": "female",
            "cohort": "Cohort A - [RAG Rule Violation] Massive Overdose (60 mg BID)",
            "diagnoses": ["Non-valvular atrial fibrillation", "Dyslipidemia"],
            "medications": ["Apixaban 60mg BID", "Atorvastatin 40mg daily"],
            "medical_history": ["Transient ischemic attack 2022", "Cholecystectomy 2014"],
            "medical_history_narrative": "66-year-old female with unapproved 12-fold supratherapeutic prescription.",
            "protocol_facts": {
                "ongoing_bleeding": False,
                "days_since_major_bleed": None,
                "oral_anticoagulation_required": True,
            },
            "lab_results": {
                "creatinine_clearance": {"value": 70.0, "unit": "mL/min"},
                "serum_creatinine": {"value": 0.9, "unit": "mg/dL"},
                "eGFR": {"value": 75.0, "unit": "mL/min/1.73m2"},
                "ALT": {"value": 28.0, "unit": "U/L"},
                "AST": {"value": 24.0, "unit": "U/L"},
                "total_bilirubin": {"value": 0.8, "unit": "mg/dL"},
                "ANC": {"value": 4200.0, "unit": "/uL"},
                "platelets": {"value": 240000.0, "unit": "/uL"},
                "hemoglobin": {"value": 14.1, "unit": "g/dL"},
                "INR": {"value": 1.1, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 70,
                "blood_pressure_systolic": 122,
                "blood_pressure_diastolic": 76,
            },
        },
    },
    {
        "patient_id": "P045",
        "name": "Tariq Mahmoud",
        "assigned_demo_trial_id": "NCT02415400",
        "cohort": "Cohort A - [RAG Rule Violation] Acute GI Bleed Washout (8 Days)",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P045",
            "name": "Tariq Mahmoud",
            "dob": "1957-03-19",
            "birth_date": "1957-03-19",
            "age": 69,
            "sex": "male",
            "cohort": "Cohort A - [RAG Rule Violation] Acute GI Bleed Washout (8 Days)",
            "diagnoses": ["Atrial fibrillation post-ablation", "Recent peptic ulcer hemorrhage"],
            "medications": ["Apixaban 5mg BID", "Pantoprazole 40mg daily"],
            "medical_history": ["Acute lower GI hemorrhage requiring 2 units PRBC 8 days ago"],
            "medical_history_narrative": "69-year-old male with recent major bleed 8 days prior, violating 30-day washout rule.",
            "protocol_facts": {
                "ongoing_bleeding": True,
                "days_since_major_bleed": 8,
                "oral_anticoagulation_required": True,
            },
            "lab_results": {
                "creatinine_clearance": {"value": 58.0, "unit": "mL/min"},
                "serum_creatinine": {"value": 1.2, "unit": "mg/dL"},
                "eGFR": {"value": 64.0, "unit": "mL/min/1.73m2"},
                "ALT": {"value": 30.0, "unit": "U/L"},
                "AST": {"value": 26.0, "unit": "U/L"},
                "total_bilirubin": {"value": 1.0, "unit": "mg/dL"},
                "ANC": {"value": 4600.0, "unit": "/uL"},
                "platelets": {"value": 215000.0, "unit": "/uL"},
                "hemoglobin": {"value": 10.4, "unit": "g/dL"},
                "INR": {"value": 1.1, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 74,
                "blood_pressure_systolic": 116,
                "blood_pressure_diastolic": 72,
            },
        },
    },
    {
        "patient_id": "P046",
        "name": "Devraj Sengupta",
        "assigned_demo_trial_id": "NCT00699998",
        "cohort": "Cohort B - [RAG Rule Violation] Renal Trial Floor Exclusion (CrCl 22 mL/min)",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P046",
            "name": "Devraj Sengupta",
            "dob": "1953-12-08",
            "birth_date": "1953-12-08",
            "age": 73,
            "sex": "male",
            "cohort": "Cohort B - [RAG Rule Violation] Renal Trial Floor Exclusion (CrCl 22 mL/min)",
            "diagnoses": ["Diabetic nephropathy with reduced filtration", "Hypertension"],
            "medications": ["Empagliflozin 10mg daily", "Amlodipine 5mg daily"],
            "medical_history": ["Type 2 diabetes for 20 years", "Coronary artery bypass 2012"],
            "medical_history_narrative": "73-year-old male with CrCl 22 mL/min below the >= 30 mL/min protocol floor.",
            "protocol_facts": {
                "dialysis_required": False,
            },
            "lab_results": {
                "creatinine_clearance": {"value": 22.0, "unit": "mL/min"},  # < 30 RAG Rule Violation
                "serum_creatinine": {"value": 2.4, "unit": "mg/dL"},
                "eGFR": {"value": 24.0, "unit": "mL/min/1.73m2"},           # > 15 so G2 passes!
                "ALT": {"value": 22.0, "unit": "U/L"},
                "AST": {"value": 20.0, "unit": "U/L"},
                "total_bilirubin": {"value": 0.7, "unit": "mg/dL"},
                "ANC": {"value": 3900.0, "unit": "/uL"},
                "platelets": {"value": 195000.0, "unit": "/uL"},
                "hemoglobin": {"value": 11.5, "unit": "g/dL"},
                "INR": {"value": 1.0, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 68,
                "blood_pressure_systolic": 134,
                "blood_pressure_diastolic": 80,
            },
        },
    },
    {
        "patient_id": "P047",
        "name": "Hannah Rosen",
        "assigned_demo_trial_id": "NCT02415400",
        "cohort": "Cohort C - [RAG Rule Violation] Active Autoimmune Disease Exclusion",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P047",
            "name": "Hannah Rosen",
            "dob": "1967-11-15",
            "birth_date": "1967-11-15",
            "age": 59,
            "sex": "female",
            "cohort": "Cohort C - [RAG Rule Violation] Active Autoimmune Disease Exclusion",
            "diagnoses": ["Colorectal carcinoma", "Active Crohn's colitis on systemic steroid"],
            "medications": ["Pembrolizumab 200mg IV Q3W", "Prednisone 30mg daily", "Mesalamine 2.4g daily"],
            "medical_history": ["Crohn's disease for 8 years", "Right hemicolectomy 2022"],
            "medical_history_narrative": "59-year-old female with active autoimmune bowel disease contraindicating checkpoint inhibitor.",
            "protocol_facts": {
                "active_autoimmune_disease": True,
                "systemic_immunosuppression": True,
            },
            "lab_results": {
                "creatinine_clearance": {"value": 65.0, "unit": "mL/min"},
                "serum_creatinine": {"value": 1.0, "unit": "mg/dL"},
                "eGFR": {"value": 72.0, "unit": "mL/min/1.73m2"},
                "ALT": {"value": 26.0, "unit": "U/L"},
                "AST": {"value": 24.0, "unit": "U/L"},
                "total_bilirubin": {"value": 0.8, "unit": "mg/dL"},
                "ANC": {"value": 3900.0, "unit": "/uL"},
                "platelets": {"value": 230000.0, "unit": "/uL"},
                "hemoglobin": {"value": 12.8, "unit": "g/dL"},
                "INR": {"value": 1.0, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 76,
                "blood_pressure_systolic": 120,
                "blood_pressure_diastolic": 75,
            },
        },
    },

    # -------------------------------------------------------------
    # Category 4: G1 ACCEPT, G2 ACCEPT, RAG ACCEPT, A2A DECLINE
    # -------------------------------------------------------------
    {
        "patient_id": "P048",
        "name": "Carlos Mendoza",
        "assigned_demo_trial_id": "NCT02415400",
        "cohort": "Cohort A - [A2A Safety Rejection] Fatal Dual CYP3A4 / P-gp Interaction",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P048",
            "name": "Carlos Mendoza",
            "dob": "1963-06-25",
            "birth_date": "1963-06-25",
            "age": 63,
            "sex": "male",
            "cohort": "Cohort A - [A2A Safety Rejection] Fatal Dual CYP3A4 / P-gp Interaction",
            "diagnoses": ["Non-valvular atrial fibrillation", "Systemic fungal infection"],
            "medications": ["Apixaban 5mg BID", "Ketoconazole 400mg daily", "Clarithromycin 500mg BID"],
            "medical_history": ["Histoplasmosis 2024", "Coronary angioplasty 2019"],
            "medical_history_narrative": "63-year-old male with severe pharmacokinetic CYP3A4 + P-gp drug interaction resulting in anticoagulant toxicity.",
            "protocol_facts": {
                "ongoing_bleeding": False,
                "days_since_major_bleed": None,
                "oral_anticoagulation_required": True,
            },
            "lab_results": {
                "creatinine_clearance": {"value": 68.0, "unit": "mL/min"},
                "serum_creatinine": {"value": 1.1, "unit": "mg/dL"},
                "eGFR": {"value": 74.0, "unit": "mL/min/1.73m2"},
                "ALT": {"value": 35.0, "unit": "U/L"},
                "AST": {"value": 30.0, "unit": "U/L"},
                "total_bilirubin": {"value": 1.1, "unit": "mg/dL"},
                "ANC": {"value": 4200.0, "unit": "/uL"},
                "platelets": {"value": 220000.0, "unit": "/uL"},
                "hemoglobin": {"value": 14.2, "unit": "g/dL"},
                "INR": {"value": 1.2, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 78,
                "blood_pressure_systolic": 128,
                "blood_pressure_diastolic": 82,
            },
        },
    },
    {
        "patient_id": "P049",
        "name": "Aditi Joshi",
        "assigned_demo_trial_id": "NCT02415400",
        "cohort": "Cohort C - [A2A Financial Denial] Unapproved Biologic Off-Label Billing ($52,800)",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P049",
            "name": "Aditi Joshi",
            "dob": "1971-08-30",
            "birth_date": "1971-08-30",
            "age": 55,
            "sex": "female",
            "cohort": "Cohort C - [A2A Financial Denial] Unapproved Biologic Off-Label Billing ($52,800)",
            "diagnoses": ["Refractory leiomyosarcoma (exploratory off-label arm)", "Hypertension"],
            "medications": ["Pembrolizumab 200mg IV Q3W", "Amlodipine 5mg daily"],
            "medical_history": ["Surgical resection of pelvic sarcoma 2021"],
            "medical_history_narrative": "55-year-old female in exploratory off-label cohort resulting in complete sponsor reimbursement denial ($52,800 liability).",
            "protocol_facts": {
                "active_autoimmune_disease": False,
                "systemic_immunosuppression": False,
            },
            "lab_results": {
                "creatinine_clearance": {"value": 72.0, "unit": "mL/min"},
                "serum_creatinine": {"value": 0.9, "unit": "mg/dL"},
                "eGFR": {"value": 78.0, "unit": "mL/min/1.73m2"},
                "ALT": {"value": 25.0, "unit": "U/L"},
                "AST": {"value": 22.0, "unit": "U/L"},
                "total_bilirubin": {"value": 0.7, "unit": "mg/dL"},
                "ANC": {"value": 4500.0, "unit": "/uL"},
                "platelets": {"value": 260000.0, "unit": "/uL"},
                "hemoglobin": {"value": 13.5, "unit": "g/dL"},
                "INR": {"value": 1.0, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 72,
                "blood_pressure_systolic": 124,
                "blood_pressure_diastolic": 76,
            },
        },
    },
    {
        "patient_id": "P050",
        "name": "Benjamin Sterling",
        "assigned_demo_trial_id": "NCT00781573",
        "cohort": "Cohort A - [A2A Multi-Specialist Dissent] Triple Antiplatelet Hemorrhage Hazard & Prior Auth",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P050",
            "name": "Benjamin Sterling",
            "dob": "1952-05-14",
            "birth_date": "1952-05-14",
            "age": 74,
            "sex": "male",
            "cohort": "Cohort A - [A2A Multi-Specialist Dissent] Triple Antiplatelet Hemorrhage Hazard & Prior Auth",
            "diagnoses": ["Post-PCI with complex bifurcation stenting", "Atrial fibrillation"],
            "medications": ["Apixaban 5mg BID", "Aspirin 81mg daily", "Clopidogrel 75mg daily", "Ticagrelor 90mg BID"],
            "medical_history": ["DES placement LAD and LCx 2024", "Hypertension 25 years"],
            "medical_history_narrative": "74-year-old male with unapproved triple antiplatelet combination causing safety dissent and $6,400 billing dispute.",
            "protocol_facts": {
                "pci_pathway": True,
                "days_since_PCI": 14,
                "ongoing_bleeding": False,
                "oral_anticoagulation_required": True,
            },
            "lab_results": {
                "creatinine_clearance": {"value": 52.0, "unit": "mL/min"},
                "serum_creatinine": {"value": 1.3, "unit": "mg/dL"},
                "eGFR": {"value": 55.0, "unit": "mL/min/1.73m2"},
                "ALT": {"value": 30.0, "unit": "U/L"},
                "AST": {"value": 28.0, "unit": "U/L"},
                "total_bilirubin": {"value": 0.9, "unit": "mg/dL"},
                "ANC": {"value": 3800.0, "unit": "/uL"},
                "platelets": {"value": 155000.0, "unit": "/uL"},
                "hemoglobin": {"value": 12.9, "unit": "g/dL"},
                "INR": {"value": 1.1, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 74,
                "blood_pressure_systolic": 132,
                "blood_pressure_diastolic": 82,
            },
        },
    },

    # -------------------------------------------------------------
    # Category 5: ALL PASS / UNANIMOUS JUSTIFIED (Clean Baseline Cases)
    # -------------------------------------------------------------
    {
        "patient_id": "P051",
        "name": "Lakshmi Ramanathan",
        "assigned_demo_trial_id": "NCT02415400",
        "cohort": "Cohort A - [All Pass: Unanimous Justified] Standard Atrial Fibrillation",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P051",
            "name": "Lakshmi Ramanathan",
            "dob": "1961-09-17",
            "birth_date": "1961-09-17",
            "age": 65,
            "sex": "female",
            "cohort": "Cohort A - [All Pass: Unanimous Justified] Standard Atrial Fibrillation",
            "diagnoses": ["Non-valvular atrial fibrillation post-flutter ablation"],
            "medications": ["Apixaban 5mg BID", "Metoprolol succinate 50mg daily"],
            "medical_history": ["Atrial flutter ablation 2023"],
            "medical_history_narrative": "65-year-old female fully eligible for antithrombotic arm. All guardrails and agents unanimous pass.",
            "protocol_facts": {
                "oral_anticoagulation_required": True,
                "ongoing_bleeding": False,
                "days_since_major_bleed": None,
                "history_of_intracranial_hemorrhage": False,
            },
            "lab_results": {
                "creatinine_clearance": {"value": 74.0, "unit": "mL/min"},
                "serum_creatinine": {"value": 0.9, "unit": "mg/dL"},
                "eGFR": {"value": 78.0, "unit": "mL/min/1.73m2"},
                "ALT": {"value": 22.0, "unit": "U/L"},
                "AST": {"value": 20.0, "unit": "U/L"},
                "total_bilirubin": {"value": 0.7, "unit": "mg/dL"},
                "ANC": {"value": 4400.0, "unit": "/uL"},
                "platelets": {"value": 245000.0, "unit": "/uL"},
                "hemoglobin": {"value": 14.0, "unit": "g/dL"},
                "INR": {"value": 1.1, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 68,
                "blood_pressure_systolic": 118,
                "blood_pressure_diastolic": 74,
            },
        },
    },
    {
        "patient_id": "P052",
        "name": "Alexander Wright",
        "assigned_demo_trial_id": "NCT02415400",
        "cohort": "Cohort C - [All Pass: Unanimous Justified] Solid Tumor Oncology",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P052",
            "name": "Alexander Wright",
            "dob": "1969-02-11",
            "birth_date": "1969-02-11",
            "age": 57,
            "sex": "male",
            "cohort": "Cohort C - [All Pass: Unanimous Justified] Solid Tumor Oncology",
            "diagnoses": ["Stage IIIB Non-Small Cell Lung Carcinoma (PD-L1 > 50%)"],
            "medications": ["Pembrolizumab 200mg IV Q3W", "Ondansetron 8mg PRN"],
            "medical_history": ["Lobectomy 2022", "No autoimmune history"],
            "medical_history_narrative": "57-year-old male with intact bone marrow reserve and organ clearance, fully protocol-compliant.",
            "protocol_facts": {
                "active_autoimmune_disease": False,
                "systemic_immunosuppression": False,
            },
            "lab_results": {
                "ANC": {"value": 4200.0, "unit": "/uL"},
                "platelets": {"value": 260000.0, "unit": "/uL"},
                "creatinine_clearance": {"value": 75.0, "unit": "mL/min"},
                "serum_creatinine": {"value": 0.95, "unit": "mg/dL"},
                "eGFR": {"value": 80.0, "unit": "mL/min/1.73m2"},
                "ALT": {"value": 24.0, "unit": "U/L"},
                "AST": {"value": 21.0, "unit": "U/L"},
                "total_bilirubin": {"value": 0.8, "unit": "mg/dL"},
                "hemoglobin": {"value": 14.5, "unit": "g/dL"},
                "INR": {"value": 1.0, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 72,
                "blood_pressure_systolic": 122,
                "blood_pressure_diastolic": 76,
            },
        },
    },
    {
        "patient_id": "P053",
        "name": "Sneha Kulkarni",
        "assigned_demo_trial_id": "NCT00809965",
        "cohort": "Cohort B - [All Pass: Unanimous Justified] Metabolic NAFLD / MASH",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P053",
            "name": "Sneha Kulkarni",
            "dob": "1975-07-23",
            "birth_date": "1975-07-23",
            "age": 51,
            "sex": "female",
            "cohort": "Cohort B - [All Pass: Unanimous Justified] Metabolic NAFLD / MASH",
            "diagnoses": ["MASH with Stage F2 fibrosis", "Impaired fasting glucose"],
            "medications": ["Pioglitazone 30mg daily", "Vitamin E 800 IU daily"],
            "medical_history": ["Liver biopsy confirmed steatohepatitis 2023"],
            "medical_history_narrative": "51-year-old female meeting all MASH protocol inclusion criteria with normal baseline transaminases.",
            "protocol_facts": {
                "prior_bleeding": False,
                "ongoing_bleeding": False,
            },
            "lab_results": {
                "ALT": {"value": 34.0, "unit": "U/L"},
                "AST": {"value": 29.0, "unit": "U/L"},
                "total_bilirubin": {"value": 0.9, "unit": "mg/dL"},
                "creatinine_clearance": {"value": 78.0, "unit": "mL/min"},
                "serum_creatinine": {"value": 0.85, "unit": "mg/dL"},
                "eGFR": {"value": 82.0, "unit": "mL/min/1.73m2"},
                "ANC": {"value": 4100.0, "unit": "/uL"},
                "platelets": {"value": 240000.0, "unit": "/uL"},
                "hemoglobin": {"value": 13.6, "unit": "g/dL"},
                "INR": {"value": 1.0, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 70,
                "blood_pressure_systolic": 118,
                "blood_pressure_diastolic": 72,
            },
        },
    },
    {
        "patient_id": "P054",
        "name": "David Kim",
        "assigned_demo_trial_id": "NCT00699998",
        "cohort": "Cohort B - [All Pass: Unanimous Justified] Renal SGLT2i Stratification",
        "demo_category": "SYNTHETIC_EHR",
        "patient": {
            "patient_id": "P054",
            "name": "David Kim",
            "dob": "1963-10-05",
            "birth_date": "1963-10-05",
            "age": 63,
            "sex": "male",
            "cohort": "Cohort B - [All Pass: Unanimous Justified] Renal SGLT2i Stratification",
            "diagnoses": ["Diabetic nephropathy stage 3a (preserved eGFR)", "Hypertension"],
            "medications": ["Empagliflozin 10mg daily", "Losartan 50mg daily"],
            "medical_history": ["Type 2 diabetes 14 years", "No cardiovascular events"],
            "medical_history_narrative": "63-year-old male with preserved filtration conforming to SGLT2i protocol eligibility.",
            "protocol_facts": {
                "dialysis_required": False,
            },
            "lab_results": {
                "eGFR": {"value": 58.0, "unit": "mL/min/1.73m2"},
                "creatinine_clearance": {"value": 62.0, "unit": "mL/min"},
                "serum_creatinine": {"value": 1.2, "unit": "mg/dL"},
                "ALT": {"value": 23.0, "unit": "U/L"},
                "AST": {"value": 21.0, "unit": "U/L"},
                "total_bilirubin": {"value": 0.8, "unit": "mg/dL"},
                "ANC": {"value": 4300.0, "unit": "/uL"},
                "platelets": {"value": 235000.0, "unit": "/uL"},
                "hemoglobin": {"value": 14.1, "unit": "g/dL"},
                "INR": {"value": 1.0, "unit": "ratio"},
            },
            "vital_signs": {
                "heart_rate": 72,
                "blood_pressure_systolic": 126,
                "blood_pressure_diastolic": 78,
            },
        },
    },
]


def update_expanded_json(file_path: Path):
    if not file_path.exists():
        print(f"File {file_path} not found.")
        return
    data = json.loads(file_path.read_text(encoding="utf-8"))
    patients = data.get("patients", [])
    existing_pids = {p.get("patient_id") or p.get("patient", {}).get("patient_id") for p in patients}

    for np in NEW_PATIENTS:
        pid = np["patient_id"]
        entry = {
            "patient_id": pid,
            "name": np["name"],
            "assigned_demo_trial_id": np["assigned_demo_trial_id"],
            "cohort": np["cohort"],
            "demo_category": "SYNTHETIC_EHR",
            "patient": np["patient"],
            "fhir_id": f"synthetic-{pid}",
        }
        if pid in existing_pids:
            # Update existing
            for i, p in enumerate(patients):
                curr_pid = p.get("patient_id") or p.get("patient", {}).get("patient_id")
                if curr_pid == pid:
                    patients[i] = entry
                    break
        else:
            patients.append(entry)

    data["patients"] = patients
    data["metadata"]["patient_count"] = len(patients)
    file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"✓ Updated {file_path} with {len(NEW_PATIENTS)} new patients (total: {len(patients)}).")


def update_seeded_ids(file_path: Path):
    if not file_path.exists():
        return
    data = json.loads(file_path.read_text(encoding="utf-8"))
    for np in NEW_PATIENTS:
        data[np["patient_id"]] = {
            "fhir_id": f"synthetic-{np['patient_id']}",
            "name": np["name"],
            "cohort": np["cohort"],
        }
    file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"✓ Updated {file_path} with seeded IDs.")


def push_new_patients_to_supabase():
    env_vars = {}
    env_file = REPO_ROOT / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip().strip("\"'")

    url = env_vars.get("SUPABASE_URL") or env_vars.get("NEXT_PUBLIC_SUPABASE_URL")
    key = (
        env_vars.get("SUPABASE_SERVICE_ROLE_KEY")
        or env_vars.get("SUPABASE_KEY")
        or env_vars.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    )

    if not url or not key:
        print("! Supabase credentials missing in .env")
        return

    rows = []
    for np in NEW_PATIENTS:
        p = np["patient"]
        pid = np["patient_id"]
        raw_dob = p.get("birth_date") or p.get("dob")
        dob_val = raw_dob if (raw_dob and str(raw_dob).count("-") == 2) else None
        age_val = (
            p.get("age")
            if (p.get("age") is not None and isinstance(p.get("age"), (int, float)) and p.get("age") > 0)
            else None
        )
        sex_val = (
            p.get("sex")
            if (p.get("sex") and str(p.get("sex")).strip().lower() not in {"unknown", "unrecorded", "none", ""})
            else None
        )
        diagnoses = p.get("diagnoses", ["Unknown"])
        primary_dx = diagnoses[0] if diagnoses else "Unknown"

        rows.append({
            "patient_id": pid,
            "trial_id": np.get("assigned_demo_trial_id") or "NCT02415400",
            "name": np["name"],
            "dob": dob_val,
            "age": age_val,
            "sex": sex_val,
            "cohort": np.get("cohort"),
            "diagnosis": primary_dx,
            "fhir_id": f"synthetic-{pid}",
            "assigned_demo_trial_id": np.get("assigned_demo_trial_id"),
            "demo_category": "SYNTHETIC_EHR",
            "clinical_data": p,
        })

    req = urllib.request.Request(
        f"{url}/rest/v1/patients",
        data=json.dumps(rows).encode("utf-8"),
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            print(f"✓ Successfully upserted {len(rows)} new patients to Supabase (HTTP {resp.status})!")
    except Exception as exc:
        print(f"! Failed to push to Supabase: {exc}")


def main():
    # 1. Update mcp_ehr JSON
    mcp_file = REPO_ROOT / "packages" / "mcp-ehr" / "src" / "mcp_ehr" / "patients_expanded.json"
    update_expanded_json(mcp_file)

    # 2. Update mock_fhir in rag_service
    rag_file = REPO_ROOT / "services" / "rag_service" / "data" / "mock_fhir" / "patients_expanded.json"
    update_expanded_json(rag_file)

    # 3. Update seeded_patient_ids.json
    seeded_file = REPO_ROOT / "packages" / "mcp-ehr" / "src" / "mcp_ehr" / "seeded_patient_ids.json"
    update_seeded_ids(seeded_file)

    # 4. Push to Supabase
    push_new_patients_to_supabase()


if __name__ == "__main__":
    main()
