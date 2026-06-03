from fastapi import APIRouter, HTTPException, Request
from typing import List

from backend.app.models.schemas import ChatRequest, ChatResponse, SourceInfo
from backend.app.rag.retrieval.vector_store import similarity_search
from backend.llm import call_llm

router = APIRouter(prefix="/api", tags=["chat"])

_SESSIONS: dict[str, list[str]] = {}


@router.post("/chat", response_model=ChatResponse)
def chat(request: Request, request_body: ChatRequest):
    # 0. Validate input
    if not request_body.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if not request_body.sessionId:
        raise HTTPException(status_code=400, detail="sessionId is required")

    # 1. Get vector DB from app state
    vector_db = getattr(request.app.state, "vector_db", [])
    print("Vector DB size:", len(vector_db))
    if vector_db:
        print("First item keys:", list(vector_db[0].keys()))
    else:
        print("Vector DB is EMPTY")

    if not vector_db:
        return ChatResponse(
            reply="I do not have enough information to answer that.",
            tokensUsed=0,
            retrievedChunks=0,
            sources=[],
            error=None,
        )

    # 2. Similarity search
    retrieved = similarity_search(
        query=request_body.message,
        vector_db=vector_db,
        top_k=3,
        threshold=0.0,
    )

    if not retrieved:
        return ChatResponse(
            reply="I do not have enough information to answer that.",
            tokensUsed=0,
            retrievedChunks=0,
            sources=[],
            error=None,
        )

    # retrieved: List[(item_dict, score)]
    items = [item for (item, score) in retrieved]
    scores = [score for (item, score) in retrieved]
    retrieved_chunks = [item["chunk"] for item in items]

    # 3. Session history
    session_id = request_body.sessionId
    history = _SESSIONS.get(session_id, [])
    history = history[-4:]
    history.append(f"User: {request_body.message}")

    # 4. Build prompt and call LLM
    context_text = "\n\n".join(retrieved_chunks)
    question = request_body.message

    prompt = f"""
You are a helpful customer support assistant. Use the following context to answer the user's question.
If the context does not contain enough information, say so politely.

Context:
{context_text}

Question: {question}

Answer (in 1–3 short sentences):
""".strip()

    reply_text = call_llm(prompt)

    if not reply_text or reply_text.strip() == "":
        reply_text = "I do not have enough information to answer that."

    history.append(f"Assistant: {reply_text}")
    _SESSIONS[session_id] = history

    # 5. Build sources
    sources: List[SourceInfo] = []
    for (item, score) in retrieved:
        sources.append(
            SourceInfo(
                id=item.get("id", ""),
                title=item.get("title", ""),
                category=item.get("category"),
                score=score,
            )
        )

    return ChatResponse(
        reply=reply_text,
        tokensUsed=0,
        retrievedChunks=len(items),
        sources=sources,
        error=None,
    )
@router.post("/debug/retrieve")
def debug_retrieve(request: Request, request_body: ChatRequest):
    if not request_body.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    vector_db = getattr(request.app.state, "vector_db", [])
    if not vector_db:
        raise HTTPException(status_code=500, detail="Vector DB is empty")

    retrieved = similarity_search(
        query=request_body.message,
        vector_db=vector_db,
        top_k=5,
        threshold=0.0,
    )

    results = []
    for item, score in retrieved:
        results.append(
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "category": item.get("category"),
                "chunk": item.get("chunk"),
                "score": score,
            }
        )

    return {"results": results}