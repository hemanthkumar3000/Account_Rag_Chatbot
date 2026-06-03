# backend/app/rag/embeddings.py

from typing import List
import numpy as np

# Replace this with your real embedding model later
def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Very simple dummy embedding: map each text to a fixed-length vector
    based on character codes. Replace with real model (e.g. SentenceTransformer).
    """
    vectors = []
    for text in texts:
        arr = np.zeros(16, dtype=float)
        for i, ch in enumerate(text[:16]):
            arr[i] = ord(ch) % 97 / 100.0
        vectors.append(arr.tolist())
    return vectors