from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.database.repositories.chat_repository import get_history

router = APIRouter(prefix="/api", tags=["History"])


@router.get("/history/{session_id}")
def history(session_id: str):
    try:
        return {
            "session_id": session_id,
            "messages": get_history(session_id),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
