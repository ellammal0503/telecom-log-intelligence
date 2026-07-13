from fastapi import FastAPI
from pydantic import BaseModel
from src.pipeline.predict import predict_with_reason
from src.llm.explainer import generate_explanation

app = FastAPI(
    title="Telecom Log Intelligence API",
    version="2.0",
    description="Production-grade VoLTE failure prediction + explanation"
)


# ---------------- REQUEST MODEL ----------------
class AnalyzeRequest(BaseModel):
    logs: str


# ---------------- HEALTH ----------------
@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------- ANALYZE ----------------
@app.post("/analyze")
def analyze(data: AnalyzeRequest):
    try:
        logs = data.logs

        pred, reasons, confidence = predict_with_reason(logs)

        label = "FAIL" if pred == 1 else "SUCCESS"

        # ---------------- LLM ----------------
        try:
            explanation = generate_explanation(logs, label, reasons)
        except Exception:
            explanation = "LLM not available"

        # ---------------- ALIGNMENT FIX ----------------
        if pred == 1 and "success" in explanation.lower():
            explanation = (
                "Call failed due to poor radio conditions and signaling issues."
            )

        return {
            "prediction": label,
            "confidence": round(float(confidence), 2),
            "key_factors": reasons,
            "explanation": explanation
        }

    except Exception as e:
        return {"error": str(e)}