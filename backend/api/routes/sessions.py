from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.database.repositories.session_repository import (
    create_session,
    delete_session,
    get_session,
)

router = APIRouter(prefix="/api", tags=["Sessions"])


@router.post("/sessions")
def new_session():
    return create_session()


@router.get("/sessions/{session_id}")
def session(session_id: str):
    result = get_session(session_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.delete("/sessions/{session_id}")
def remove_session(session_id: str):
    return delete_session(session_id)
