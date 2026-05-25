try:
    from fastapi import FastAPI, HTTPException  # type: ignore
    from fastapi.middleware.cors import CORSMiddleware  # type: ignore
except ImportError as exc:
    raise ImportError(
        "fastapi is required to run this application. Install it with `pip install fastapi uvicorn`"
    ) from exc

from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import os

from backend.retrieval import build_vector_db, similarity_search  # type: ignore
from backend.rag import build_rag_prompt  # type: ignore
from backend.llm import call_llm  # type: ignore

# Load .env from project root (one level above backend/)
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

# 1. Create FastAPI app FIRST
app = FastAPI(title="GenAI RAG Assistant")

# 2. Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Build vector DB on startup and store in app.state
@app.on_event("startup")
def startup_event():
    vector_db: List[Dict[str, Any]] = build_vector_db()
    app.state.vector_db = vector_db
    print(f"[DEBUG] app.state.vector_db size after startup: {len(app.state.vector_db)}")

# 4. Simple in-memory session history
_SESSIONS: dict[str, List[str]] = {}


# 5. Pydantic models for chat API
class ChatRequest(BaseModel):
    sessionId: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    tokensUsed: int
    retrievedChunks: int
    error: Optional[str] = None


# 6. Routes
@app.get("/")
def read_root():
    return {"message": "RAG Assistant backend is running"}


@app.get("/health")
def health_check():
    vector_db = getattr(app.state, "vector_db", [])
    print(f"[DEBUG] health vector_db size from app.state: {len(vector_db)}")
    return {
        "status": "ok",
        "llm_api_key_present": bool(os.getenv("LLM_API_KEY")),
        "vector_db_size": len(vector_db),
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if not request.sessionId:
        raise HTTPException(status_code=400, detail="sessionId is required")

    # 1. Get vector DB
    vector_db = getattr(app.state, "vector_db", [])
    if not vector_db:
        return ChatResponse(
            reply="I do not have enough information to answer that.",
            tokensUsed=0,
            retrievedChunks=0,
            error=None,
        )

    # 2. Similarity search
    retrieved = similarity_search(
    query=request.message,
    vector_db=vector_db,
    top_k=3,
    threshold=0.3,
)
    print(f"[DEBUG] retrieved in chat: {retrieved}")
    if not retrieved:
        return ChatResponse(
            reply="I do not have enough information to answer that.",
            tokensUsed=0,
            retrievedChunks=0,
            error=None,
        )

    retrieved_chunks = [r[0] for r in retrieved]

    # 3. Session history
    session_id = request.sessionId
    history = _SESSIONS.get(session_id, [])
    history = history[-4:]
    history.append(f"User: {request.message}")

    # SIMPLE: answer directly from retrieved context
    if retrieved_chunks:
        reply_text = retrieved_chunks[0]
    else:
        reply_text = "I do not have enough information to answer that."

    history.append(f"Assistant: {reply_text}")
    _SESSIONS[session_id] = history

    return ChatResponse(
        reply=reply_text,
        tokensUsed=0,
        retrievedChunks=len(retrieved_chunks),
        error=None,
    )