import streamlit as st
import requests

st.set_page_config(page_title="Telecom Dashboard", layout="wide")

st.title("📡 Telecom Failure Intelligence Dashboard")

# -----------------------------

# INPUTS

# -----------------------------

st.sidebar.header("Input Parameters")

rrc_fail = st.sidebar.number_input("RRC Failures", 0, 10, 0)
ho_fail = st.sidebar.number_input("Handover Failures", 0, 10, 0)
packet_loss = st.sidebar.number_input("Packet Loss", 0, 10, 0)
latency = st.sidebar.number_input("Latency", 0, 10, 0)
bgp_down = st.sidebar.number_input("BGP Down", 0, 5, 0)
if_down = st.sidebar.number_input("Interface Down", 0, 5, 0)

# -----------------------------

# BUTTON

# -----------------------------

if st.button(" Predict"):

#```
    payload = {
    "rrc_fail": rrc_fail,
    "ho_fail": ho_fail,
    "packet_loss": packet_loss,
    "latency": latency,
    "bgp_down": bgp_down,
    "if_down": if_down
    }

    try:
        response = requests.post(
            "http://127.0.0.1:8000/predict",
        json=payload
        )

        result = response.json()

    # -----------------------------
    # KPI CARDS
    # -----------------------------
        col1, col2, col3 = st.columns(3)

        with col1:
            if result["prediction"] == "FAIL":
                st.error(" FAIL")
            else:
                st.success(" SUCCESS")

        with col2:
            st.metric("Probability", f"{result['probability']*100:.1f}%")

        with col3:
            severity = "LOW"
            if result.get("top_reasons"):
                severity = result["top_reasons"][0]["severity"]

            if severity == "HIGH":
                st.error("HIGH")
            elif severity == "MEDIUM":
                st.warning("MEDIUM")
            else:
                st.success("LOW")

        st.markdown("---")

    # -----------------------------
    # TOP REASONS
    # -----------------------------
        st.subheader("🔍 Top Root Causes")

        for r in result.get("top_reasons", []):
            text = f"{r['reason']} (Score: {r['score']})"

            if r["severity"] == "HIGH":
                st.error(f" {text}")
            elif r["severity"] == "MEDIUM":
                st.warning(f" {text}")
            else:
                st.success(f" {text}")

    except Exception as e:
        st.error(f"API Error: {e}")
#```
