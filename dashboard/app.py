import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Telecom NOC Dashboard", layout="wide")

# ---------------- HEADER ----------------
st.title("📡 Telecom Network Operations Center")
st.markdown("Real-time Call Analysis & Root Cause Detection")

# ---------------- SIDEBAR INPUT ----------------
st.sidebar.header("📥 Input Logs")

logs = st.sidebar.text_area(
    "Paste Telecom Logs",
    height=250,
    placeholder="""[RRC] event=RRC_SETUP_REQUEST sinr=3
[SIP] event=100 Trying
[SIP] event=100 Trying
[SIP] event=503 Service Unavailable"""
)

analyze_btn = st.sidebar.button("🔍 Analyze Call")


# ---------------- HELPER FUNCTION ----------------
def parse_logs_to_df(log_text):
    rows = []
    for line in log_text.split("\n"):
        if line.strip():
            rows.append({"log": line})
    return pd.DataFrame(rows)


# ---------------- MAIN ----------------
if analyze_btn:

    if not logs.strip():
        st.warning("⚠️ Please paste logs")
        st.stop()

    with st.spinner("Analyzing..."):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/analyze",
                json={"logs": logs}
            )

            result = response.json()

            if "error" in result:
                st.error(result["error"])
                st.stop()

        except Exception as e:
            st.error(f"API Failed: {e}")
            st.stop()

    prediction = result["prediction"]
    confidence = result["confidence"]
    factors = result["key_factors"]
    explanation = result["explanation"]

    # ---------------- KPI CARDS ----------------
    col1, col2, col3 = st.columns(3)

    with col1:
        status_color = "red" if prediction == "FAIL" else "green"
        st.markdown(
            f"""
            <div style="background-color:{status_color};padding:20px;border-radius:10px">
            <h3 style="color:white">Prediction</h3>
            <h1 style="color:white">{prediction}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.metric("Confidence", f"{confidence:.2f}")

    with col3:
        severity = "CRITICAL" if confidence > 0.8 and prediction == "FAIL" else "NORMAL"
        st.metric("Severity", severity)

    st.divider()

    # ---------------- RCA PANEL ----------------
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🔎 Root Cause Factors")
        for f in factors:
            st.markdown(f"• {f}")

    with col_right:
        st.subheader("🧠 AI Explanation")
        st.info(explanation)

    st.divider()

    # ---------------- TIMELINE ----------------
    st.subheader("📜 Event Timeline")

    df = parse_logs_to_df(logs)
    st.dataframe(df, use_container_width=True)

    st.divider()

    # ---------------- RAW RESPONSE ----------------
    with st.expander("📦 Raw API Response"):
        st.json(result)

else:
    st.info("Paste logs and click Analyze to view dashboard")