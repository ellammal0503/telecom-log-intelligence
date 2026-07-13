# 📡 Telecom Log Intelligence

## 🚀 Overview

Modern telecom networks generate massive volumes of signaling logs and KPI data.
Most troubleshooting today is **reactive, manual, and slow**.

This project builds an **AI-powered Telecom Log Intelligence System** that:

* Detects call failures automatically
* Identifies root causes (RCA)
* Generates human-readable explanations using LLM
* Visualizes insights in a NOC-style dashboard

---

## 🎯 Key Features

### 🔍 Intelligent Failure Detection

* Ensemble ML model (**Random Forest + XGBoost**)
* Predicts: `SUCCESS` or `FAIL`
* Confidence scoring

---

### 📊 Root Cause Analysis (RCA)

Automatically detects key failure drivers:

* Low SINR
* High latency
* SIP failures (503 errors)
* RRC instability

---

### 🤖 LLM-Based Explanation

* Powered by **Ollama (LLaMA3)**
* Converts logs → concise RCA explanation
* Production-style summary for NOC engineers

---

### 🖥️ NOC Dashboard (Streamlit)

* KPI Cards (Prediction, Confidence)
* RCA Panel (Key Factors)
* Timeline view of logs
* Real-time log analysis

---

## 🏗️ Architecture

```id="arch01"
Logs → Feature Extraction → ML Models → Rule Engine → LLM → FastAPI → Streamlit Dashboard
```

---

## ⚙️ Tech Stack

* **Backend:** FastAPI
* **ML Models:** Scikit-learn, XGBoost
* **LLM:** Ollama (LLaMA3)
* **Frontend:** Streamlit
* **Deployment:** Docker

---

## 📥 Input Format (Logs)

Paste telecom logs like:

```id="log01"
[RRC] event=RRC_SETUP_REQUEST | sinr=3
[SIP] event=100 Trying
[SIP] event=100 Trying
[SIP] event=503 Service Unavailable
```

---

## 📤 Output

```id="out01"
Prediction: FAIL
Confidence: 0.97

Key Factors:
- Low SINR
- SIP service failure

Explanation:
Call failed due to poor radio conditions and signaling issues.
```

---

## 🧪 API Usage

### Health Check

```id="api01"
GET /health
```

---

### Analyze Logs

```id="api02"
POST /analyze
```

Request:

```json id="api03"
{
  "logs": "your telecom logs here"
}
```

---

## 🖥️ Run Locally

### 1️⃣ Create virtual environment

```bash id="loc01"
python -m venv .venv
source .venv/bin/activate
```

---

### 2️⃣ Install dependencies

```bash id="loc02"
pip install -r requirements.txt
```

---

### 3️⃣ Start FastAPI

```bash id="loc03"
uvicorn src.api.main:app --reload
```

---

### 4️⃣ Start Streamlit

```bash id="loc04"
streamlit run dashboard/app.py
```

---

## 🤖 LLM Setup (Ollama – Required)

### 1️⃣ Install Ollama

```bash id="oll01"
brew install ollama
```

---

### 2️⃣ Start Ollama Server (MANDATORY)

```bash id="oll02"
ollama serve
```

👉 Keep this running in a separate terminal

---

### 3️⃣ Pull Model

```bash id="oll03"
ollama pull llama3
```

---

### 4️⃣ Test Model

```bash id="oll04"
ollama run llama3
```

---

## ⚠️ Important Notes

* If `ollama serve` is NOT running:

  * Prediction works
  * Explanation will show:

    ```
    LLM not available
    ```

* First model download is ~4–5 GB

---

## 🐳 Docker Run

```bash id="dock01"
docker build -t telecom-ai .
docker run -p 8000:8000 -p 8501:8501 telecom-ai
```

---

## 🌐 Access

* API Docs → http://localhost:8000/docs
* Dashboard → http://localhost:8501

---

## 📌 Project Highlights

* Combines **ML + Rule Engine + LLM**
* Real telecom debugging use case
* Production-style API + UI
* Strong fit for:

  * Telecom Analytics
  * Data Science
  * AI/ML Engineering

---

## 🔮 Future Enhancements

* RAG-based log intelligence (vector DB)
* Multi-cell correlation analysis
* Real-time streaming (Kafka)
* Grafana / NOC integration

---
**Author:** Karthick Kumarasamy
**M.Tech – Data Science & Machine Learning**

---

## 🔗 GitHub Repository

https://github.com/ellammal0503/telecom-log-intelligence.git

---

## ⭐ If you find this useful

Give a ⭐ and connect for collaboration!
