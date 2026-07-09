import pandas as pd
import joblib
# src.utils.reason_engine import get_reason
from src.utils.reason_engine import get_top_reasons
import joblib

model = None

def load_model():
    global model
    if model is None:
        model = joblib.load("src/models/rf_model.pkl")

load_model()

model = joblib.load("src/models/rf_model.pkl")

FEATURES = [
    "rrc_fail",
    "ho_fail",
    "packet_loss",
    "latency",
    "bgp_down",
    "if_down"
]
def predict_with_reason(input_data: dict):

    df = pd.DataFrame([input_data])

    prob = model.predict_proba(df[FEATURES])[0][1]

    threshold = 0.35
    pred = 1 if prob > threshold else 0

    top_reasons = get_top_reasons(input_data)

    return {
        "prediction": "FAIL" if pred == 1 else "SUCCESS",
        "probability": round(prob, 3),
        "top_reasons": top_reasons
    }