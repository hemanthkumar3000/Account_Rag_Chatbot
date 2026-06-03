from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import chat, health
from backend.app.rag.retrieval.vector_store import build_vector_db

app = FastAPI(title="GenAI RAG Assistant v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    vector_db = build_vector_db()
    app.state.vector_db = vector_db
    print(f"[DEBUG] app.state.vector_db size after startup: {len(vector_db)}")


app.include_router(health.router)
app.include_router(chat.router)