from __future__ import annotations

from backend.database.repositories.session_repository import (
    create_session,
    get_session,
)
from backend.memory.history import get_recent_history
from backend.memory.memory import get_memories


def build_context(
    session_id: str | None,
) -> dict:
    """
    Build the conversation context for a request.

    If session_id is provided and exists in the database, reuse it
    so that history accumulates across turns.

    If session_id is provided but does NOT exist yet (first message
    from a new frontend conversation), register it so the same id
    is reused on subsequent turns — this is what makes multi-turn
    history work when the frontend generates its own conversation id.

    If no session_id is provided, create a fresh session.
    """

    if session_id:
        existing = get_session(session_id)

        if existing:
            # Known session — reuse it.
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
        else:
            # First message with this id — register the session so
            # subsequent messages can find it.
            _register_session(session_id)
            return {
                "session_id": session_id,
                "history": [],
                "memory": [],
            }

    # No session_id supplied — create a brand-new one.
    session = create_session()
    return {
        "session_id": session["session_id"],
        "history": [],
        "memory": [],
    }


def _register_session(session_id: str) -> None:
    """Insert a session row with a caller-supplied id."""
    from datetime import datetime, timezone
    from backend.database.mongodb import get_database

    now = datetime.now(timezone.utc)
    db = get_database()

    db.sessions.update_one(
        {"session_id": session_id},
        {
            "$setOnInsert": {
                "session_id": session_id,
                "created_at": now,
                "updated_at": now,
            }
        },
        upsert=True,
    )