"""
Chat request/response schemas.

Note: referenced by app/api/v1/chat.py since the RAG-chat-endpoint milestone,
but never generated as its own file — added here to make the codebase
importable/runnable.
"""
import uuid
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: uuid.UUID | None = None
    language: str = "en"


class ChatResponse(BaseModel):
    session_id: uuid.UUID
    answer: str
    sources: list[str] = []
    confidence: float | None = None
    is_emergency: bool = False
