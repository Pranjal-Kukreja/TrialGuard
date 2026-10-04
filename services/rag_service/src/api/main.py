from fastapi import (
    FastAPI,
    HTTPException
)

from src.api.models import (
    TrialGuardRequest
)

from src.llm.client import (
    is_llm_configured
)

from src.pipeline_v3 import (
    TrialGuardPipelineV3
)

from src.mock_fhir.service import (
    PatientNotFoundError,
    get_patient
)


app = FastAPI(
    title="TrialGuard AI/ML",
    version="0.3.0"
)


pipeline = (
    TrialGuardPipelineV3()
)


@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "trialguard-ai-ml",
        "rule_engine": "v3",
        "rag": "ready",
        "llm_configured": is_llm_configured()
    }


@app.post("/evaluate")
def evaluate(
    request: TrialGuardRequest
):

    try:

        return pipeline.evaluate(
            request
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@app.get("/mock-fhir/patients/{patient_id}")
def mock_fhir_patient(
    patient_id: str
):
    try:
        return get_patient(patient_id)

    except PatientNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )