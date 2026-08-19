from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.api.schemas.chat import ChatRequest, ChatResponse
from backend.database.repositories.chat_repository import save_message
from backend.memory.manager import build_context
from backend.rag.visual_answerer import answer_visual_question

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        context = build_context(request.session_id)

        result = answer_visual_question(
            question=request.message,
        )

        answer = result.get("answer", "")
        session_id = context["session_id"]

        save_message(
            session_id=session_id,
            role="user",
            content=request.message,
            sources=[],
        )

        save_message(
            session_id=session_id,
            role="assistant",
            content=answer,
            sources=result.get("sources", []),
        )

        return ChatResponse(
            session_id=session_id,
            answer=answer,
            confidence=result.get("confidence", "low"),
            evidence_sufficient=result.get("evidence_sufficient", False),
            refusal=result.get("refusal", False),
            sources=result.get("sources", []),
            memory=context.get("memory", []),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
