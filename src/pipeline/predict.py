import joblib
import numpy as np
import pandas as pd
import re

rf = joblib.load("models/rf_model.pkl")
xgb = joblib.load("models/xgb_model.pkl")
scaler = joblib.load("models/scaler.pkl")

FEATURE_ORDER = [
    "rrc_attempts",
    "retries",
    "handover_attempts",
    "sip_progress",
    "rrc_reconfig",
    "avg_sinr",
    "avg_rsrp",
    "avg_latency"
]


def extract_features_from_logs(logs: str):
    lines = logs.split("\n")

    features = {
        "rrc_attempts": 0,
        "retries": 0,
        "handover_attempts": 0,
        "sip_progress": 0,
        "rrc_reconfig": 0,
        "avg_sinr": 10,
        "avg_rsrp": -90,
        "avg_latency": 50
    }

    sinr_vals, rsrp_vals, latency_vals = [], [], []

    for line in lines:

        if "RRC_SETUP_REQUEST" in line:
            features["rrc_attempts"] += 1

        if "RECOVERY_ATTEMPT" in line:
            features["retries"] += 1

        if "HO_ATTEMPT" in line:
            features["handover_attempts"] += 1

        if "100 Trying" in line or "180 Ringing" in line:
            features["sip_progress"] += 1

        if "RRC_RECONFIGURATION" in line:
            features["rrc_reconfig"] += 1

        sinr = re.search(r"sinr=([-+]?\d*\.?\d+)", line)
        rsrp = re.search(r"rsrp=([-+]?\d*\.?\d+)", line)
        latency = re.search(r"latency_ms=([-+]?\d*\.?\d+)", line)

        if sinr:
            sinr_vals.append(float(sinr.group(1)))

        if rsrp:
            rsrp_vals.append(float(rsrp.group(1)))

        if latency:
            latency_vals.append(float(latency.group(1)))

    if sinr_vals:
        features["avg_sinr"] = np.mean(sinr_vals)

    if rsrp_vals:
        features["avg_rsrp"] = np.mean(rsrp_vals)

    if latency_vals:
        features["avg_latency"] = np.mean(latency_vals)

    return features


def predict_with_reason(logs: str):

    feature_dict = extract_features_from_logs(logs)
    feature_list = [feature_dict[f] for f in FEATURE_ORDER]

    X = pd.DataFrame([feature_list], columns=FEATURE_ORDER)
    X_scaled = scaler.transform(X)

    rf_prob = rf.predict_proba(X_scaled)[0][1]
    xgb_prob = xgb.predict_proba(X_scaled)[0][1]

    final_prob = (rf_prob + xgb_prob) / 2

    # RULE BOOSTING (not override)
    rule_score = 0

    if feature_dict["avg_sinr"] < 5:
        rule_score += 0.2

    if "503" in logs:
        rule_score += 0.3

    if feature_dict["avg_latency"] > 200:
        rule_score += 0.2

    final_prob = min(1.0, final_prob + rule_score)

    pred = 1 if final_prob > 0.5 else 0

    confidence = round(final_prob if pred == 1 else (1 - final_prob), 2)

    reasons = []

    if feature_dict["avg_sinr"] < 5:
        reasons.append("Low SINR")

    if feature_dict["avg_latency"] > 200:
        reasons.append("High latency")

    if feature_dict["sip_progress"] > 3:
        reasons.append("Excessive SIP signaling")

    if feature_dict["rrc_reconfig"] > 1:
        reasons.append("Frequent RRC reconfiguration")

    if "503" in logs:
        reasons.append("SIP service failure")

    if not reasons:
        reasons.append("Normal behavior")

    return pred, reasons, confidence