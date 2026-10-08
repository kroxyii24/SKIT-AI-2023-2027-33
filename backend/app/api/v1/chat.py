from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.rbac import get_current_user, TokenPayload
from app.core.prompt_guard import sanitize_user_message
from app.db.session import get_db
from app.services.emergency.detector import run_emergency_check
from app.services.rag.generation import generate_answer
from app.schemas.chat import ChatRequest, ChatResponse
from app.models.domain import ChatSession, ChatMessage
import json

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
def send_message(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: TokenPayload = Depends(get_current_user),
):
    # 0. Input sanitization / prompt-injection defense — runs before anything
    # else touches this message.
    sanitization = sanitize_user_message(payload.message)
    if not sanitization.is_safe:
        return ChatResponse(
            session_id=payload.session_id,
            answer=(
                "I couldn't process that message. Please rephrase your health question "
                "in plain language."
            ),
            sources=[],
            confidence=None,
            is_emergency=False,
        )
    payload.message = sanitization.sanitized_text

    # 1. Emergency gate — runs BEFORE any retrieval/generation, always.
    emergency_result = run_emergency_check(payload.message, language=payload.language)

    session = db.get(ChatSession, payload.session_id) if payload.session_id else None
    if session is None:
        session = ChatSession(user_id=user.sub, language=payload.language)
        db.add(session)
        db.flush()

    db.add(ChatMessage(session_id=session.id, role="user", content=payload.message))

    if emergency_result.is_emergency:
        db.add(ChatMessage(
            session_id=session.id, role="assistant",
            content=emergency_result.response_message, was_emergency_flagged=True,
        ))
        db.commit()
        return ChatResponse(
            session_id=session.id,
            answer=emergency_result.response_message,
            sources=[],
            confidence=None,
            is_emergency=True,
        )

    # 2. Normal path — grounded RAG generation
    rag_result = generate_answer(payload.message, language=payload.language)

    db.add(ChatMessage(
        session_id=session.id, role="assistant", content=rag_result.answer,
        sources=json.dumps(rag_result.sources), confidence_score=rag_result.confidence,
    ))
    db.commit()

    return ChatResponse(
        session_id=session.id,
        answer=rag_result.answer,
        sources=rag_result.sources,
        confidence=rag_result.confidence,
        is_emergency=False,
    )
