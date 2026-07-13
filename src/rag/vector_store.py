import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Dummy telecom knowledge base (expand later)
documents = [
    "Low SINR causes radio link failure and call drops",
    "SIP 503 indicates server overload or service unavailability",
    "RRC setup failures occur due to poor signal or congestion",
    "High retries indicate unstable signaling conditions",
    "Frequent handovers can degrade call stability",
    "High latency impacts call quality and session setup"
]

# Convert to embeddings
embeddings = model.encode(documents)

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))


def search_similar(query, k=2):
    query_vec = model.encode([query])
    distances, indices = index.search(np.array(query_vec), k)

    results = [documents[i] for i in indices[0]]
    return results