import pandas as pd
import joblib
# src.utils.reason_engine import 

rf = joblib.load("models/rf_model.pkl")
xgb = joblib.load("models/xgb_model.pkl")
scaler = joblib.load("models/scaler.pkl")


def predict_with_reason(logs):

    features = extract_features_from_logs(logs)
    X = scaler.transform([features])

    # ---- Predictions ----
    rf_prob = rf.predict_proba(X)[0][1]
    xgb_prob = xgb.predict_proba(X)[0][1]

    # ---- Ensemble ----
    final_prob = (rf_prob + xgb_prob) / 2
    pred = 1 if final_prob > 0.5 else 0

    # ---- Reasons (same logic) ----
    reasons = []

    if features["sip_trying"] > 2:
        reasons.append("High SIP retries")

    if features["avg_sinr"] < 5:
        reasons.append("Low SINR")

    if features["rrc_reconfig"] > 1:
        reasons.append("Frequent RRC reconfiguration")

    return pred, reasons, final_prob