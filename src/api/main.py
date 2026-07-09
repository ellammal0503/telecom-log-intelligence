from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from src.pipeline.predict import predict_with_reason

app = FastAPI(
    title="Telecom Log Intelligence API",
    version="1.0.0",
    description="Predict VoLTE call failures with reason and severity"
)

# -----------------------------
# Input Schema
# -----------------------------
class PredictRequest(BaseModel):
    rrc_fail: int = Field(ge=0)
    ho_fail: int = Field(ge=0)
    packet_loss: int = Field(ge=0)
    latency: int = Field(ge=0)
    bgp_down: int = Field(ge=0)
    if_down: int = Field(ge=0)


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------------
# Prediction Endpoint
# -----------------------------
@app.post("/predict")
def predict(data: PredictRequest):
    try:
        result = predict_with_reason(data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))