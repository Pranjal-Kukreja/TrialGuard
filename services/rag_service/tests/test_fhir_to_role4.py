from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_mock_fhir_patient_to_role4_evaluate():
    fhir_response = client.get(
        "/mock-fhir/patients/AUGUSTUS_FAIL_01"
    )

    assert fhir_response.status_code == 200

    patient = fhir_response.json()
    assert patient["patient_id"] == "AUGUSTUS_FAIL_01"
    assert patient["lab_results"]["creatinine_clearance"]

    evaluate_response = client.post(
        "/evaluate",
        json={
            "trial_id": "NCT02415400",
            "patient": patient,
            "query": "Check eligibility",
        },
    )

    assert evaluate_response.status_code == 200

    result = evaluate_response.json()
    assert result["trial_id"] == "NCT02415400"
    assert result["decision"] == "FAIL"
    assert result["eligibility"] == "INELIGIBLE"
    assert result["explanation"]
    assert "generation_metadata" in result
