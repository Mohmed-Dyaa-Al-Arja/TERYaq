from __future__ import annotations

from datetime import datetime, timezone

from backend.database.mongodb import get_database


def save_message(
    session_id: str,
    role: str,
    content: str,
    sources: list,
) -> None:
    now = datetime.now(timezone.utc)

    get_database().messages.insert_one({
        "session_id": session_id,
        "role": role,
        "content": content,
        "sources": sources,
        "created_at": now,
    })

    get_database().sessions.update_one(
        {"session_id": session_id},
        {"$set": {"updated_at": now}},
        upsert=True,
    )


def get_history(
    session_id: str,
    limit: int = 20,
) -> list[dict]:
    cursor = (
        get_database()
        .messages
        .find(
            {"session_id": session_id},
            {"_id": 0},
        )
        .sort("created_at", 1)
        .limit(limit)
    )

    result = []

    for item in cursor:
        if hasattr(item.get("created_at"), "isoformat"):
            item["created_at"] = item["created_at"].isoformat()
        result.append(item)

    return result
