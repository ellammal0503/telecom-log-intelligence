import ollama
from src.rag.vector_store import search_similar


def generate_explanation(logs, prediction, reasons):
    try:
        # 🔍 Retrieve context from vector DB
        context = search_similar(" ".join(reasons))

        prompt = f"""
You are a telecom network expert.

Prediction: {"FAIL" if prediction == 1 else "SUCCESS"}
Key Factors: {", ".join(reasons)}

Relevant Knowledge:
{context}

Logs:
{logs}

Give a short, production-grade RCA (2-3 lines).
"""

        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )

        return response["message"]["content"]

    except Exception as e:
        return f"LLM Error: {str(e)}"