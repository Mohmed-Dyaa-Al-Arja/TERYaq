from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from backend.database.mongodb import get_database


def create_session() -> dict:
    session_id = str(uuid4())
    now = datetime.now(timezone.utc)

    get_database().sessions.insert_one({
        "session_id": session_id,
        "created_at": now,
        "updated_at": now,
    })

    return {
        "session_id": session_id,
        "created_at": now.isoformat(),
    }


def get_session(session_id: str) -> dict | None:
    doc = get_database().sessions.find_one(
        {"session_id": session_id},
        {"_id": 0},
    )

    if not doc:
        return None

    for key in ("created_at", "updated_at"):
        if key in doc and hasattr(doc[key], "isoformat"):
            doc[key] = doc[key].isoformat()

    return doc


def delete_session(session_id: str) -> dict:
    db = get_database()

    db.sessions.delete_one({"session_id": session_id})
    db.messages.delete_many({"session_id": session_id})
    db.memories.delete_many({"session_id": session_id})

    return {
        "session_id": session_id,
        "deleted": True,
    }
