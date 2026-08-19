from __future__ import annotations

from uuid import uuid4

from backend.database.repositories.session_repository import create_session
from backend.memory.history import get_recent_history
from backend.memory.memory import get_memories


def build_context(
    session_id: str | None,
) -> dict:
    if not session_id:
        session = create_session()
        session_id = session["session_id"]

    return {
        "session_id": session_id,
        "history": get_recent_history(
            session_id,
            limit=10,
        ),
        "memory": get_memories(
            session_id,
            limit=20,
        ),
    }
