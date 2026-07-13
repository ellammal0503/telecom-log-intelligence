import pandas as pd
import re

# ---------------- PARSER ----------------
def parse_logs(file_path="data/raw/telecom_logs.txt"):
    rows = []

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()

            match = re.match(r"\[(.*?)\]\s(\w+)\s\|\s(.+)", line)
            if not match:
                continue

            timestamp = match.group(1)
            module = match.group(2)
            rest = match.group(3)

            fields = {"timestamp": timestamp, "module": module}

            for item in rest.split("|"):
                if "=" in item:
                    k, v = item.strip().split("=", 1)
                    fields[k.strip()] = v.strip()

            rows.append(fields)

    return pd.DataFrame(rows)


# ---------------- FEATURE ENGINEERING ----------------
def build_features(df):

    df["event"] = df["event"].fillna("UNKNOWN")

    grouped = df.groupby("callId")

    features = []

    for call_id, group in grouped:
        feature = {}
        feature["callId"] = call_id

        events = group["event"].tolist()

        # ---------------- SAFE FEATURES (NO LEAKAGE) ----------------
        #feature["num_events"] = len(events)

        # Success indicators (allowed)
        #feature["rrc_success"] = int("RRC_SETUP_COMPLETE" in events)
        #feature["reg_success"] = int("REGISTRATION_ACCEPT" in events)
        #feature["sip_success"] = int("200 OK" in events)
        #feature["ho_success"] = int("HO_SUCCESS" in events)
        feature["rrc_attempts"] = events.count("RRC_SETUP_REQUEST")
        feature["retries"] = events.count("RECOVERY_ATTEMPT")
        feature["handover_attempts"] = events.count("HO_ATTEMPT")
        #feature["sip_trying"] = events.count("100 Trying")
        #feature["sip_ringing"] = events.count("180 Ringing")
        feature["sip_progress"] = (events.count("100 Trying") + events.count("180 Ringing")
)

        # Behavior indicators (NOT direct failure flags)
        feature["rrc_reconfig"] = int("RRC_RECONFIGURATION" in events)

        # ---------------- KPI FEATURES ----------------
        sinr_vals, rsrp_vals, latency_vals = [], [], []

        for _, row in group.iterrows():

            if "sinr" in row:
                try:
                    sinr_vals.append(float(row["sinr"]))
                except:
                    pass

            if "rsrp" in row:
                try:
                    rsrp_vals.append(float(row["rsrp"]))
                except:
                    pass

            if "latency_ms" in row:
                try:
                    latency_vals.append(float(row["latency_ms"]))
                except:
                    pass

        feature["avg_sinr"] = sum(sinr_vals)/len(sinr_vals) if sinr_vals else 0
        feature["avg_rsrp"] = sum(rsrp_vals)/len(rsrp_vals) if rsrp_vals else 0
        feature["avg_latency"] = sum(latency_vals)/len(latency_vals) if latency_vals else 0

        # ---------------- TARGET (REALISTIC) ----------------
        # SUCCESS only if full flow completes
        if "200 OK" in events and "RRC_SETUP_COMPLETE" in events:
            feature["target"] = 0   # SUCCESS
        else:
            feature["target"] = 1   # FAIL

        features.append(feature)

    feature_df = pd.DataFrame(features)

    # 🔥 FIX NAN ISSUE
    feature_df = feature_df.fillna(0)

    return feature_df


# ---------------- PIPELINE ----------------
def run_feature_pipeline():
    print("Loading logs...")
    df = parse_logs()

    print("Building features...")
    feature_df = build_features(df)

    feature_df.to_csv("data/processed/features.csv", index=False)

    print("\nTarget Distribution:")
    print(feature_df["target"].value_counts())

    print("✅ Features saved!")

    return feature_df


if __name__ == "__main__":
    run_feature_pipeline()