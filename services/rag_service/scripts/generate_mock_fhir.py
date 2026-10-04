import copy
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "mock_fhir"
    / "patients.json"
)


BASE_PATIENT = {
    "age": 67,
    "sex": "male",
    "weight": 75.0,

    "diagnoses": [
        "non-valvular atrial fibrillation",
        "coronary artery disease"
    ],

    "medications": [
        "aspirin",
        "clopidogrel"
    ],

    "allergies": [],

    "lab_results": {
        "ALT": {
            "value": 1.1,
            "unit": "ULN"
        },
        "AST": {
            "value": 1.0,
            "unit": "ULN"
        },
        "eGFR": {
            "value": 55.0,
            "unit": "mL/min/1.73m2"
        },
        "serum_creatinine": {
            "value": 1.2,
            "unit": "mg/dL"
        },
        "creatinine_clearance": {
            "value": 45.0,
            "unit": "mL/min"
        }
    },

    "vital_signs": {
        "heart_rate": {
            "value": 76,
            "unit": "bpm"
        },
        "blood_pressure_systolic": {
            "value": 128,
            "unit": "mmHg"
        }
    },

    "medical_history": [],

    "current_symptoms": [],

    "protocol_facts": {
        "oral_anticoagulation_required": True,

        "acs_pathway": False,
        "days_since_acute_coronary_syndrome": None,

        "pci_pathway": True,
        "days_since_PCI": 7,

        "planned_p2y12_duration": 6,

        "history_of_intracranial_hemorrhage": False,
        "ongoing_bleeding": False,
        "known_coagulopathy": False,

        "cabg_for_index_acs": False,

        "other_condition_requiring_chronic_anticoagulation": False,

        "drug_contraindication": [],

        "pregnant": False,
        "breastfeeding": False,

        "woman_of_childbearing_potential": False,
        "pregnancy_test_negative": None
    }
}


def patient(patient_id):
    p = copy.deepcopy(BASE_PATIENT)
    p["patient_id"] = patient_id
    return p


def set_lab(p, name, value, unit=None):
    if unit is None:
        unit = p["lab_results"].get(
            name,
            {}
        ).get("unit")

    p["lab_results"][name] = {
        "value": value,
        "unit": unit
    }


def generate_pass_cases():

    patients = []

    # P001 - standard passing case
    p = patient("P001")
    patients.append(p)

    # P002 - older but still acceptable
    p = patient("P002")
    p["age"] = 72
    p["weight"] = 82
    set_lab(p, "creatinine_clearance", 60)
    patients.append(p)

    # P003
    p = patient("P003")
    p["age"] = 55
    p["sex"] = "female"
    p["protocol_facts"][
        "woman_of_childbearing_potential"
    ] = True
    p["protocol_facts"][
        "pregnancy_test_negative"
    ] = True
    p["protocol_facts"]["pregnant"] = False
    p["protocol_facts"]["breastfeeding"] = False
    patients.append(p)

    # P004 - renal value close to boundary but above it
    p = patient("P004")
    set_lab(
        p,
        "creatinine_clearance",
        31.0
    )
    set_lab(
        p,
        "serum_creatinine",
        2.4
    )
    patients.append(p)

    # P005 - ACS pathway
    p = patient("P005")
    p["protocol_facts"]["acs_pathway"] = True
    p["protocol_facts"][
        "days_since_acute_coronary_syndrome"
    ] = 10
    p["protocol_facts"]["pci_pathway"] = False
    p["protocol_facts"]["days_since_PCI"] = None
    patients.append(p)

    # P006
    p = patient("P006")
    p["age"] = 45
    p["weight"] = 90
    set_lab(p, "creatinine_clearance", 75)
    patients.append(p)

    # P007 - exactly CrCl boundary
    p = patient("P007")
    set_lab(
        p,
        "creatinine_clearance",
        30.0
    )
    patients.append(p)

    # P008 - exactly creatinine boundary
    p = patient("P008")
    set_lab(
        p,
        "serum_creatinine",
        2.5
    )
    patients.append(p)

    # P009 - atrial flutter alternative
    p = patient("P009")
    p["diagnoses"] = [
        "atrial flutter",
        "coronary artery disease"
    ]
    patients.append(p)

    # P010 - age minimum boundary
    p = patient("P010")
    p["age"] = 18
    p["weight"] = 70
    patients.append(p)

    return patients


def generate_fail_cases():

    patients = []

    # P011 - below required age
    p = patient("P011")
    p["age"] = 17
    p["_demo_expected_reason"] = "age below minimum"
    patients.append(p)

    # P012 - creatinine exclusion
    p = patient("P012")
    set_lab(
        p,
        "serum_creatinine",
        3.0
    )
    p["_demo_expected_reason"] = (
        "serum creatinine above exclusion threshold"
    )
    patients.append(p)

    # P013 - CrCl exclusion
    p = patient("P013")
    set_lab(
        p,
        "creatinine_clearance",
        24.0
    )
    p["_demo_expected_reason"] = (
        "creatinine clearance below threshold"
    )
    patients.append(p)

    # P014 - intracranial hemorrhage
    p = patient("P014")
    p["protocol_facts"][
        "history_of_intracranial_hemorrhage"
    ] = True
    p["_demo_expected_reason"] = (
        "history of intracranial hemorrhage"
    )
    patients.append(p)

    # P015 - active bleeding
    p = patient("P015")
    p["protocol_facts"][
        "ongoing_bleeding"
    ] = True
    p["current_symptoms"] = [
        "active bleeding"
    ]
    p["_demo_expected_reason"] = "ongoing bleeding"
    patients.append(p)

    # P016 - coagulopathy
    p = patient("P016")
    p["protocol_facts"][
        "known_coagulopathy"
    ] = True
    p["_demo_expected_reason"] = "known coagulopathy"
    patients.append(p)

    # P017 - CABG exclusion
    p = patient("P017")
    p["protocol_facts"][
        "cabg_for_index_acs"
    ] = True
    p["_demo_expected_reason"] = "CABG for index ACS"
    patients.append(p)

    # P018 - other chronic anticoagulation condition
    p = patient("P018")
    p["diagnoses"].append(
        "mechanical heart valve"
    )
    p["protocol_facts"][
        "other_condition_requiring_chronic_anticoagulation"
    ] = True
    p["_demo_expected_reason"] = (
        "other chronic anticoagulation indication"
    )
    patients.append(p)

    # P019 - contraindication
    p = patient("P019")
    p["protocol_facts"][
        "drug_contraindication"
    ] = [
        "apixaban"
    ]
    p["_demo_expected_reason"] = (
        "drug contraindication"
    )
    patients.append(p)

    # P020 - required P2Y12 duration not met
    p = patient("P020")
    p["protocol_facts"][
        "planned_p2y12_duration"
    ] = 3
    p["_demo_expected_reason"] = (
        "P2Y12 duration below requirement"
    )
    patients.append(p)

    return patients


def generate_review_cases():

    patients = []

    # P021 - missing creatinine
    p = patient("P021")
    del p["lab_results"][
        "serum_creatinine"
    ]
    p["_demo_expected_reason"] = (
        "missing serum creatinine"
    )
    patients.append(p)

    # P022 - missing CrCl
    p = patient("P022")
    del p["lab_results"][
        "creatinine_clearance"
    ]
    p["_demo_expected_reason"] = (
        "missing creatinine clearance"
    )
    patients.append(p)

    # P023 - PCI pathway but timing missing
    p = patient("P023")
    p["protocol_facts"]["pci_pathway"] = True
    p["protocol_facts"]["days_since_PCI"] = None
    p["_demo_expected_reason"] = (
        "PCI timing missing"
    )
    patients.append(p)

    # P024 - ACS applicability known but timing missing
    p = patient("P024")
    p["protocol_facts"]["acs_pathway"] = True
    p["protocol_facts"][
        "days_since_acute_coronary_syndrome"
    ] = None
    p["protocol_facts"]["pci_pathway"] = False
    p["_demo_expected_reason"] = (
        "ACS timing missing"
    )
    patients.append(p)

    # P025 - anticoagulation plan missing
    p = patient("P025")
    del p["protocol_facts"][
        "oral_anticoagulation_required"
    ]
    p["_demo_expected_reason"] = (
        "anticoagulation plan missing"
    )
    patients.append(p)

    # P026 - P2Y12 duration missing
    p = patient("P026")
    del p["protocol_facts"][
        "planned_p2y12_duration"
    ]
    p["_demo_expected_reason"] = (
        "P2Y12 duration missing"
    )
    patients.append(p)

    # P027 - bleeding status unknown
    p = patient("P027")
    del p["protocol_facts"][
        "ongoing_bleeding"
    ]
    p["_demo_expected_reason"] = (
        "ongoing bleeding status unknown"
    )
    patients.append(p)

    # P028 - coagulopathy status unknown
    p = patient("P028")
    del p["protocol_facts"][
        "known_coagulopathy"
    ]
    p["_demo_expected_reason"] = (
        "coagulopathy status unknown"
    )
    patients.append(p)

    # P029 - female, WOCBP, pregnancy test unknown
    p = patient("P029")
    p["sex"] = "female"
    p["protocol_facts"][
        "woman_of_childbearing_potential"
    ] = True
    p["protocol_facts"][
        "pregnancy_test_negative"
    ] = None
    p["_demo_expected_reason"] = (
        "pregnancy test missing"
    )
    patients.append(p)

    # P030 - missing weight affects dosage selection
    p = patient("P030")
    p["age"] = 82
    p["weight"] = None
    set_lab(
        p,
        "serum_creatinine",
        1.4
    )
    p["_demo_expected_reason"] = (
        "weight missing for apixaban dose evaluation"
    )
    patients.append(p)

    return patients


def main():

    records = []

    for p in generate_pass_cases():
        records.append({
            "patient_id": p["patient_id"],
            "demo_category": "PASS",
            "patient": p
        })

    for p in generate_fail_cases():
        records.append({
            "patient_id": p["patient_id"],
            "demo_category": "FAIL",
            "patient": p
        })

    for p in generate_review_cases():
        records.append({
            "patient_id": p["patient_id"],
            "demo_category": "REVIEW",
            "patient": p
        })

    output = {
        "metadata": {
            "synthetic": True,
            "purpose": (
                "TrialGuard prototype mock FHIR/EHR fixtures"
            ),
            "default_trial_id": "NCT02415400",
            "patient_count": len(records)
        },

        "patients": records
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("=" * 60)
    print("Mock FHIR dataset generated")
    print("=" * 60)

    print(
        f"Patients: {len(records)}"
    )

    print(
        f"Output: {OUTPUT}"
    )


if __name__ == "__main__":
    main()