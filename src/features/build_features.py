import pandas as pd

def build_features():

    print("Loading logs...")

    sip = pd.read_csv("data/raw/sip_logs.csv")
    rrc = pd.read_csv("data/raw/rrc_logs.csv")
    csr = pd.read_csv("data/raw/csr_logs.csv")

    # -----------------------------
    # SIP FEATURES
    # -----------------------------
    sip["is_failure"] = sip["sip_message"].str.contains("408|486|500").astype(int)

    sip["timeout"] = sip["sip_message"].str.contains("408").astype(int)
    sip["busy"] = sip["sip_message"].str.contains("486").astype(int)
    sip["server_error"] = sip["sip_message"].str.contains("500").astype(int)

    sip_features = sip.groupby("call_id").agg({
        "is_failure": "max",
        "timeout": "sum",
        "busy": "sum",
        "server_error": "sum"
    }).reset_index()

    sip_features.rename(columns={"is_failure": "target"}, inplace=True)

    # -----------------------------
    # RRC FEATURES
    # -----------------------------
    rrc["rrc_fail"] = (rrc["rrc_event"] == "RRC_SETUP_FAILURE").astype(int)
    rrc["ho_fail"] = (rrc["rrc_event"] == "HO_FAILURE").astype(int)

    rrc_features = rrc.groupby("call_id").agg({
        "rrc_fail": "sum",
        "ho_fail": "sum"
    }).reset_index()

    # -----------------------------
    # CSR FEATURES (FIXED)
    # -----------------------------
    # Map CSR events to numeric signals
    csr["packet_loss"] = (csr["event"] == "HIGH_PACKET_LOSS").astype(int)
    csr["latency"] = (csr["event"] == "HIGH_LATENCY").astype(int)
    csr["bgp_down"] = (csr["event"] == "BGP_DOWN").astype(int)
    csr["if_down"] = (csr["event"] == "IF_DOWN").astype(int)

    # ⚠️ CSR has no call_id → simulate mapping
    csr["call_id"] = csr.index % len(sip_features)

    csr_features = csr.groupby("call_id").agg({
        "packet_loss": "sum",
        "latency": "sum",
        "bgp_down": "sum",
        "if_down": "sum"
    }).reset_index()

    # -----------------------------
    # MERGE ALL
    # -----------------------------
    df = sip_features.merge(rrc_features, on="call_id", how="left")
    df = df.merge(csr_features, on="call_id", how="left")

    df.fillna(0, inplace=True)

    # -----------------------------
    # DEBUG (IMPORTANT)
    # -----------------------------
    print("\nTarget Distribution:")
    print(df["target"].value_counts())

    # -----------------------------
    # SAVE
    # -----------------------------
    df.to_csv("data/processed/features.csv", index=False)

    print("✅ Features saved to data/processed/features.csv")