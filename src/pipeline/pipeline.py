import pandas as pd
import joblib
# src.utils.reason_engine import 
import joblib

model = None

def load_model():
    global model
    if model is None:
        model = joblib.load("models/rf_model.pkl")

load_model()

# Load once (not per request)
model = joblib.load("models/rf_model.pkl")

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

    pred = model.predict(df[FEATURES])[0]
    prob = model.predict_proba(df[FEATURES])[0][1]

    reason, severity = get_reason(input_data)

    return {
        "prediction": "FAIL" if pred == 1 else "SUCCESS",
        "probability": round(prob, 3),
        "reason": reason,
        "severity": severity
    }