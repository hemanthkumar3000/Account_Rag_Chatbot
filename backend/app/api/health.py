from fastapi import APIRouter, Request
import os

router = APIRouter()


@router.get("/")
def root():
    return {"message": "RAG Assistant backend is running"}


@router.get("/health")
def health_check(request: Request):
    vector_db = getattr(request.app.state, "vector_db", [])
    return {
        "status": "ok",
        "llm_api_key_present": bool(os.getenv("LLM_API_KEY")),
        "vector_db_size": len(vector_db),
    }