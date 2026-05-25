import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .embeddings import embed_texts

def load_documents() -> List[Dict[str, str]]:
    docs_path = Path(__file__).resolve().parent / "docs.json"
    print(f"[DEBUG] Loading docs from: {docs_path}")

    if not docs_path.exists():
        print("[DEBUG] docs.json does NOT exist!")
        return []

    with open(docs_path, "r", encoding="utf-8") as f:
        documents = json.load(f)

    print(f"[DEBUG] Loaded {len(documents)} documents")
    return documents

def simple_chunk_text(text: str, max_chars: int = 300) -> List[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end
    return chunks

def build_vector_db() -> List[Dict[str, Any]]:
    """
    Load docs.json, chunk documents, compute embeddings,
    and return a list of {chunk, embedding}.
    """
    documents = load_documents()

    all_chunks: List[str] = []
    for doc in documents:
        chunks = simple_chunk_text(doc["content"])
        for chunk in chunks:
            all_chunks.append(chunk)

    print(f"[DEBUG] Total chunks: {len(all_chunks)}")

    if not all_chunks:
        return []

    embeddings = embed_texts(all_chunks)
    print(f"[DEBUG] Generated {len(embeddings)} embeddings")

    vector_db = [
        {"chunk": chunk, "embedding": emb}
        for chunk, emb in zip(all_chunks, embeddings)
    ]

    print(f"[DEBUG] vector_db size in build_vector_db: {len(vector_db)}")
    return vector_db

def similarity_search(
    query: str,
    vector_db: List[Dict[str, Any]],
    top_k: int = 3,
    threshold: float = 0.3
) -> List[Tuple[str, float]]:
    ...
    if not vector_db:
        return []

    query_vec = np.array(embed_texts([query])[0]).reshape(1, -1)
    doc_vectors = np.array([item["embedding"] for item in vector_db])

    scores = cosine_similarity(query_vec, doc_vectors)[0]

    scored_chunks: List[Tuple[str, float]] = []
    for item, score in zip(vector_db, scores):
        print(f"[DEBUG] similarity score for chunk '{item['chunk'][:40]}...': {score}")
        if score >= threshold:
            scored_chunks.append((item["chunk"], float(score)))

    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    return scored_chunks[:top_k]