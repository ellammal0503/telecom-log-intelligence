# 📡 Telecom Log Intelligence Platform

An AI-powered system to **predict telecom call failures** and provide **top root-cause analysis** using SIP, RRC, and CSR logs.

---

## 🚀 Overview

Modern telecom networks generate massive logs across multiple layers:

* SIP (Call signaling)
* RRC (Radio control)
* CSR (Backhaul / router logs)

Manual troubleshooting is slow and reactive.

👉 This project builds an **end-to-end ML pipeline** that:

* Predicts call success/failure
* Identifies **top 3 root causes**
* Displays results in a **real-time dashboard**

---

## 🧠 Key Features

✅ Synthetic telecom log generator (SIP + RRC + CSR)
✅ Feature engineering across multiple network layers
✅ Machine Learning model (Random Forest)
✅ Root Cause Engine (Top 3 ranked reasons)
✅ FastAPI backend (production-ready API)
✅ Streamlit dashboard (NOC-style UI)

---

## 📊 Sample Output

```
Prediction: FAIL
Probability: 0.92

Top Reasons:
1. Backhaul Failure (BGP Down) | HIGH
2. High Packet Loss            | HIGH
3. Handover Failure            | MEDIUM
```

---

## 🏗️ Project Architecture

```
Data Generation → Feature Engineering → Model Training
        ↓
    FastAPI Backend (/predict)
        ↓
 Streamlit Dashboard (UI)
```

---

## 📂 Project Structure

```
telecom-log-intelligence/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── models/
│   └── rf_model.pkl
│
├── src/
│   ├── ingestion/         # Log generators
│   ├── features/          # Feature engineering
│   ├── models/            # Training logic
│   ├── pipeline/          # Prediction logic
│   ├── utils/             # Reason engine
│   └── api/               # FastAPI app
│
├── dashboard/
│   └── app.py             # Streamlit UI
│
├── run_pipeline.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone repo

```bash
git clone https://github.com/ellammal0503/telecom-log-intelligence.git
cd telecom-log-intelligence
```

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Run the Project

### Step 1: Run Pipeline

```bash
python run_pipeline.py
```

This will:

* Generate logs
* Build features
* Train model
* Save model in `models/`

---

### Step 2: Start API

```bash
uvicorn src.api.main:app --reload
```

👉 API Docs:
http://127.0.0.1:8000/docs

---

### Step 3: Start Dashboard

```bash
streamlit run dashboard/app.py
```

👉 Open:
http://localhost:8501

---

## 🔍 Root Cause Engine

The system explains failures using:

* Backhaul issues (BGP Down)
* Packet loss
* Latency spikes
* RRC failures
* Handover failures
* SIP errors

👉 Returns **Top 3 ranked reasons with severity**

---

## 📈 Model Details

* Algorithm: Random Forest Classifier
* Input: Engineered telecom KPIs
* Output: Failure prediction + probability
* Explainability: Rule-based reason engine

---

## 🎯 Use Cases

* Telecom NOC monitoring
* Call failure analysis
* Network troubleshooting automation
* AI-based observability systems

---

## ⚠️ Note

This is a **simulation project**, not production data.
Logs are synthetically generated to mimic real telecom scenarios.

---

## 🚀 Future Improvements

* Real log ingestion (Wireshark / QXDM)
* Time-series anomaly detection
* Alerting system
* Grafana / Prometheus integration
* LLM-based log summarization

---

## 👤 Author

Karthick Kumarasamy
Telecom QA → AI/ML Engineer

---

## ⭐ If you like this project

Give it a star ⭐ on GitHub!
