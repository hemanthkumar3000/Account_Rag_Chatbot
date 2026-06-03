# Account Support RAG Chatbot

A full-stack Retrieval-Augmented Generation (RAG) chatbot that answers account-related questions (password reset, account deletion, billing, security) using your own documents.  
Backend: FastAPI + Ollama (local LLM). Frontend: React (Vite).

## Features

- Chat interface for asking account support questions.
- RAG pipeline:
  - Knowledge base stored in `backend/docs.json`.
  - Embeddings + cosine similarity for retrieval.
  - LLM (via Ollama, e.g. `llama3.2`) generates grounded answers.
- Sources returned with each answer (document id, title, category, similarity score).
- Debug endpoint to inspect retrieval results without the LLM.

## Tech Stack

- **Backend:** Python, FastAPI, Uvicorn.
- **LLM:** Ollama (local), default model `llama3.2`.
- **RAG:** Custom embeddings + in-memory vector store + cosine similarity.
- **Frontend:** React, Vite, Fetch API.

## Project Structure

```text
project/
  backend/
    app/
      api/
        chat.py          # /api/chat and /api/debug/retrieve
      rag/
        embeddings.py    # embed_texts
        retrieval/
          vector_store.py
      models/
        schemas.py       # ChatRequest, ChatResponse, SourceInfo
    docs.json            # Knowledge base
    main.py              # FastAPI app entrypoint
  rag-frontend/
    src/
      App.jsx            # Chat UI
  README.md
  ...
```

## Running Locally

### 1. Backend + Ollama

1. Install Python dependencies (inside a virtualenv):

   ```bash
   pip install -r requirements.txt
   ```

2. Install Ollama and pull a model (once):

   ```bash
   ollama pull llama3.2
   ```

3. Start the backend:

   ```bash
   python -m uvicorn backend.app.main:app --reload --port 8000
   ```

   The app loads `backend/docs.json`, builds embeddings, and exposes:
   - `POST /api/chat`
   - `POST /api/debug/retrieve`
   - `GET /health`

### 2. Frontend

1. In another terminal:

   ```bash
   cd rag-frontend
   npm install
   npm run dev
   ```

2. Open the URL from Vite (usually `http://127.0.0.1:5173`) and start chatting.

## API Overview

- `POST /api/chat`  
  Request:

  ```json
  {
    "sessionId": "test-session",
    "message": "How can I reset my password?"
  }
  ```

  Response:

  ```json
  {
    "reply": "...",
    "tokensUsed": 0,
    "retrievedChunks": 3,
    "sources": [
      { "id": "doc0_chunk0", "title": "Reset Password", "category": "Account", "score": 0.77 }
    ],
    "error": null
  }
  ```

- `POST /api/debug/retrieve` – returns raw retrieval results (`id`, `title`, `category`, `chunk`, `score`).
- `GET /health` – basic health check.

## Documentation

- `SRS.md` – Software Requirements Specification.
- `SDD.md` – Software Design Document.
- `TEST_PLAN.md` – Test plan and test cases.

## Future Improvements

- Swap in-memory vector store for a vector DB (Chroma / Qdrant / pgvector).
- Add authentication and rate limiting.
- Deploy backend + Ollama to a cloud VM and host frontend publicly.