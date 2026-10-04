import copy
import json
import random
from pathlib import Path


random.seed(42)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

FHIR_FILE = (
    PROJECT_ROOT
    / "data"
    / "mock_fhir"
    / "patients.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "mock_fhir"
    / "patients_expanded.json"
)


# ============================================================
# DEMO TRIAL IDS
#
# IMPORTANT:
# These are synthetic associations for load/integration testing.
#
# Do NOT claim eligibility support for a trial unless that trial
# actually exists in your ClinicalTrials dataset AND rules/RAG
# are available for it.
# ============================================================

DEMO_TRIAL_IDS = [
    "NCT02415400",
    "NCT05930860",
    "NCT04435660",
    "NCT00000000"
]


DIAGNOSES = [
    "non-valvular atrial fibrillation",
    "atrial flutter",
    "coronary artery disease",
    "hypertension",
    "type 2 diabetes mellitus",
    "chronic kidney disease",
    "heart failure",
    "hyperlipidemia",
    "osteoarthritis"
]


MEDICATIONS = [
    "aspirin",
    "clopidogrel",
    "apixaban",
    "atorvastatin",
    "metoprolol",
    "lisinopril",
    "amlodipine",
    "metformin"
]


ALLERGIES = [
    "penicillin",
    "sulfonamide",
    "latex",
    "none"
]


def bounded(
    value,
    minimum,
    maximum
):
    return max(
        minimum,
        min(maximum, value)
    )


def random_patient(
    patient_id: str,
    trial_id: str
):

    age = random.randint(
        18,
        89
    )

    sex = random.choice(
        [
            "male",
            "female"
        ]
    )

    weight = round(
        random.uniform(
            48,
            115
        ),
        1
    )

    # --------------------------------------------------------
    # Diagnoses
    # --------------------------------------------------------

    diagnoses = random.sample(
        DIAGNOSES,
        k=random.randint(
            1,
            min(
                4,
                len(DIAGNOSES)
            )
        )
    )

    # Keep many cardiovascular patients useful for the
    # NCT02415400 demonstration.
    if (
        trial_id
        == "NCT02415400"
        and random.random() < 0.7
    ):

        if (
            "non-valvular atrial fibrillation"
            not in diagnoses
        ):
            diagnoses.insert(
                0,
                "non-valvular atrial fibrillation"
            )

    # --------------------------------------------------------
    # Medications
    # --------------------------------------------------------

    medications = random.sample(
        MEDICATIONS,
        k=random.randint(
            1,
            min(
                5,
                len(MEDICATIONS)
            )
        )
    )

    # --------------------------------------------------------
    # Allergies
    # --------------------------------------------------------

    allergy = random.choice(
        ALLERGIES
    )

    allergies = (
        []
        if allergy == "none"
        else [allergy]
    )

    # --------------------------------------------------------
    # Laboratory values
    # --------------------------------------------------------

    serum_creatinine = round(
        random.uniform(
            0.6,
            3.4
        ),
        2
    )

    crcl = round(
        random.uniform(
            18,
            95
        ),
        1
    )

    egfr = round(
        bounded(
            crcl
            + random.uniform(
                -8,
                12
            ),
            10,
            120
        ),
        1
    )

    lab_results = {
        "ALT": {
            "value": round(
                random.uniform(
                    0.5,
                    3.5
                ),
                2
            ),
            "unit": "ULN"
        },

        "AST": {
            "value": round(
                random.uniform(
                    0.5,
                    3.0
                ),
                2
            ),
            "unit": "ULN"
        },

        "eGFR": {
            "value": egfr,
            "unit": "mL/min/1.73m2"
        },

        "serum_creatinine": {
            "value": serum_creatinine,
            "unit": "mg/dL"
        },

        "creatinine_clearance": {
            "value": crcl,
            "unit": "mL/min"
        },

        "ANC": {
            "value": round(
                random.uniform(
                    1000,
                    7000
                ),
                0
            ),
            "unit": "/uL"
        },

        "platelets": {
            "value": round(
                random.uniform(
                    80000,
                    400000
                ),
                0
            ),
            "unit": "/uL"
        },

        "hemoglobin": {
            "value": round(
                random.uniform(
                    8.0,
                    16.0
                ),
                1
            ),
            "unit": "g/dL"
        },

        "INR": {
            "value": round(
                random.uniform(
                    0.8,
                    2.8
                ),
                2
            ),
            "unit": "ratio"
        },

        "total_bilirubin": {
            "value": round(
                random.uniform(
                    0.3,
                    2.5
                ),
                2
            ),
            "unit": "mg/dL"
        }
    }

    # --------------------------------------------------------
    # Vitals
    # --------------------------------------------------------

    vital_signs = {
        "heart_rate": {
            "value": random.randint(
                55,
                110
            ),
            "unit": "bpm"
        },

        "blood_pressure_systolic": {
            "value": random.randint(
                100,
                170
            ),
            "unit": "mmHg"
        },

        "blood_pressure_diastolic": {
            "value": random.randint(
                60,
                105
            ),
            "unit": "mmHg"
        }
    }

    # --------------------------------------------------------
    # Cardiac function
    # --------------------------------------------------------

    cardiac_function = {
        "LVEF": {
            "value": round(
                random.uniform(
                    35,
                    70
                ),
                1
            ),
            "unit": "%"
        },

        "QTc": {
            "value": round(
                random.uniform(
                    380,
                    490
                ),
                0
            ),
            "unit": "ms"
        }
    }

    # --------------------------------------------------------
    # Trial/protocol facts
    # --------------------------------------------------------

    acs_pathway = (
        random.random()
        < 0.35
    )

    pci_pathway = (
        not acs_pathway
        or random.random()
        < 0.5
    )

    if not acs_pathway and not pci_pathway:
        pci_pathway = True

    protocol_facts = {
        "oral_anticoagulation_required":
            random.random() < 0.85,

        "acs_pathway":
            acs_pathway,

        "days_since_acute_coronary_syndrome":
            (
                random.randint(
                    1,
                    25
                )
                if acs_pathway
                else None
            ),

        "pci_pathway":
            pci_pathway,

        "days_since_PCI":
            (
                random.randint(
                    1,
                    25
                )
                if pci_pathway
                else None
            ),

        "planned_p2y12_duration":
            random.choice(
                [
                    3,
                    6,
                    6,
                    6,
                    12
                ]
            ),

        "history_of_intracranial_hemorrhage":
            random.random() < 0.04,

        "ongoing_bleeding":
            random.random() < 0.05,

        "known_coagulopathy":
            random.random() < 0.04,

        "cabg_for_index_acs":
            random.random() < 0.04,

        "other_condition_requiring_chronic_anticoagulation":
            random.random() < 0.05,

        "drug_contraindication":
            (
                [
                    random.choice(
                        [
                            "apixaban",
                            "aspirin",
                            "P2Y12 inhibitor"
                        ]
                    )
                ]
                if random.random() < 0.04
                else []
            ),

        "pregnant":
            False,

        "breastfeeding":
            False,

        "woman_of_childbearing_potential":
            (
                sex == "female"
                and 18 <= age <= 50
            ),

        "pregnancy_test_negative":
            (
                True
                if (
                    sex == "female"
                    and 18 <= age <= 50
                )
                else None
            )
    }

    # --------------------------------------------------------
    # Medical history
    # --------------------------------------------------------

    history = []

    if random.random() < 0.20:
        history.append(
            "previous bleeding event"
        )

    if random.random() < 0.15:
        history.append(
            "previous PCI"
        )

    # --------------------------------------------------------
    # Final patient
    # --------------------------------------------------------

    return {
        "patient_id":
            patient_id,

        "age":
            age,

        "sex":
            sex,

        "weight":
            weight,

        "diagnoses":
            diagnoses,

        "medications":
            medications,

        "allergies":
            allergies,

        "lab_results":
            lab_results,

        "vital_signs":
            vital_signs,

        "cardiac_function":
            cardiac_function,

        "medical_history":
            history,

        "current_symptoms":
            [],

        "consent_capacity":
            True,

        "pregnancy_test_result":
            (
                "negative"
                if (
                    sex == "female"
                    and 18 <= age <= 50
                )
                else None
            ),

        "ecog_status":
            None,

        "last_systemic_therapy_date":
            None,

        "protocol_facts":
            protocol_facts
    }


def main():

    if not FHIR_FILE.exists():

        raise FileNotFoundError(
            "\nExisting FHIR fixture not found:\n"
            f"{FHIR_FILE}\n\n"
            "Run first:\n"
            "python -m scripts.generate_mock_fhir"
        )

    # ========================================================
    # PRESERVE EXISTING 30
    # ========================================================

    with FHIR_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        existing = json.load(
            file
        )

    records = copy.deepcopy(
        existing.get(
            "patients",
            []
        )
    )

    print(
        f"Existing patients preserved: "
        f"{len(records)}"
    )

    existing_ids = {
        record[
            "patient_id"
        ]
        for record
        in records
    }

    # ========================================================
    # GENERATE ANOTHER 270
    #
    # Existing 30 + 270 = 300
    # ========================================================

    generated = 0

    for number in range(
        31,
        301
    ):

        patient_id = (
            f"P{number:03d}"
        )

        if patient_id in existing_ids:
            continue

        trial_id = (
            DEMO_TRIAL_IDS[
                generated
                % len(
                    DEMO_TRIAL_IDS
                )
            ]
        )

        p = random_patient(
            patient_id,
            trial_id
        )

        records.append({
            "patient_id":
                patient_id,

            # This is fixture metadata.
            # Do not send it to the AI model.
            "assigned_demo_trial_id":
                trial_id,

            "demo_category":
                "UNLABELED",

            "patient":
                p
        })

        generated += 1

    # ========================================================
    # OUTPUT
    # ========================================================

    output = {
        "metadata": {
            "synthetic":
                True,

            "purpose":
                (
                    "TrialGuard synthetic "
                    "mock FHIR/EHR fixtures"
                ),

            "patient_count":
                len(records),

            "note":
                (
                    "Trial associations are "
                    "development/demo metadata "
                    "and do not imply eligibility."
                )
        },

        "patients":
            records
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("=" * 70)

    print(
        "EXPANDED MOCK FHIR DATABASE CREATED"
    )

    print("=" * 70)

    print(
        f"Original patients : "
        f"{len(existing.get('patients', []))}"
    )

    print(
        f"Generated patients: "
        f"{generated}"
    )

    print(
        f"Total patients    : "
        f"{len(records)}"
    )

    print(
        f"\nOutput:\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()