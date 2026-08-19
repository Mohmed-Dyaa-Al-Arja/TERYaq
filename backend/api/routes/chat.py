from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.api.schemas.chat import ChatRequest, ChatResponse
from backend.database.repositories.chat_repository import save_message
from backend.memory.manager import build_context
from backend.rag.pipeline import run_pipeline

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        context = build_context(request.session_id)

        # The public API must use the same safety-first pipeline as the
        # standalone RAG entry point. Do not bypass input/output guards.
        result = run_pipeline(request.message)

        answer = result.get("answer", "")
        session_id = context["session_id"]
        sources = result.get("sources", [])

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
            sources=sources,
        )

        return ChatResponse(
            session_id=session_id,
            answer=answer,
            confidence=result.get("confidence", "low"),
            evidence_sufficient=result.get("evidence_sufficient", False),
            refusal=result.get("refusal", False),
            sources=sources,
            memory=context.get("memory", []),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
