from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    sessionId: str
    message: str


class SourceInfo(BaseModel):
    id: str
    title: str
    category: Optional[str] = None
    score: Optional[float] = None


class ChatResponse(BaseModel):
    reply: str
    tokensUsed: int
    retrievedChunks: int
    sources: List[SourceInfo]
    error: Optional[str] = None