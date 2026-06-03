from pathlib import Path
from typing import List, Dict, Any, Tuple

import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from backend.app.rag.embeddings import embed_texts


def load_documents() -> List[Dict[str, Any]]:
    """
    Load docs.json from backend/docs.json (same as before).
    """
    docs_path = Path(__file__).resolve().parents[3] / "docs.json"
    print(f"[RAG] Loading docs from: {docs_path}")

    if not docs_path.exists():
        print("[RAG] docs.json does NOT exist!")
        return []

    with open(docs_path, "r", encoding="utf-8") as f:
        documents = json.load(f)

    print(f"[RAG] Loaded {len(documents)} documents")
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
    and return a list of {id, title, category, chunk, embedding}.
    """
    documents = load_documents()

    all_chunks: List[str] = []
    all_metadata: List[Dict[str, Any]] = []

    for doc_idx, doc in enumerate(documents):
        title = doc.get("title", f"Document {doc_idx}")
        category = doc.get("category")
        content = doc.get("content", "")
        chunks = simple_chunk_text(content)
        for chunk_idx, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadata.append(
                {
                    "id": f"doc{doc_idx}_chunk{chunk_idx}",
                    "title": title,
                    "category": category,
                }
            )

    print(f"[RAG] Total chunks: {len(all_chunks)}")

    if not all_chunks:
        return []

    embeddings = embed_texts(all_chunks)
    print(f"[RAG] Generated {len(embeddings)} embeddings")

    vector_db: List[Dict[str, Any]] = []
    for chunk, emb, meta in zip(all_chunks, embeddings, all_metadata):
        vector_db.append(
            {
                "id": meta["id"],
                "title": meta["title"],
                "category": meta.get("category"),
                "chunk": chunk,
                "embedding": emb,
            }
        )

    print(f"[RAG] vector_db size in build_vector_db: {len(vector_db)}")
    return vector_db


def similarity_search(
    query: str,
    vector_db: List[Dict[str, Any]],
    top_k: int = 3,
    threshold: float = 0.0,
) -> List[Tuple[Dict[str, Any], float]]:
    """
    Return list of (item_dict, score).
    """
    if not vector_db:
        return []

    query_vec = np.array(embed_texts([query])[0]).reshape(1, -1)
    doc_vectors = np.array([item["embedding"] for item in vector_db])

    scores = cosine_similarity(query_vec, doc_vectors)[0]

    scored_items: List[Tuple[Dict[str, Any], float]] = []
    for item, score in zip(vector_db, scores):
        print(f"[RAG] similarity score for chunk '{item['chunk'][:40]}...': {score}")
        if score >= threshold:
            scored_items.append((item, float(score)))

    if not scored_items:
        best_idx = int(np.argmax(scores))
        best_item = vector_db[best_idx]
        return [(best_item, float(scores[best_idx]))]

    scored_items.sort(key=lambda x: x[1], reverse=True)
    return scored_items[:top_k]