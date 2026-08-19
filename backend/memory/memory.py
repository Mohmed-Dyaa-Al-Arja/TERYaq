from __future__ import annotations

from datetime import datetime, timezone

from backend.database.mongodb import get_database


def save_memory(
    session_id: str,
    key: str,
    value: str,
) -> None:
    now = datetime.now(timezone.utc)

    get_database().memories.update_one(
        {
            "session_id": session_id,
            "key": key,
        },
        {
            "$set": {
                "value": value,
                "updated_at": now,
            },
            "$setOnInsert": {
                "created_at": now,
            },
        },
        upsert=True,
    )


def get_memories(
    session_id: str,
    limit: int = 20,
) -> list[dict]:
    cursor = (
        get_database()
        .memories
        .find(
            {"session_id": session_id},
            {"_id": 0},
        )
        .sort("updated_at", -1)
        .limit(limit)
    )

    result = []

    for item in cursor:
        for key in ("created_at", "updated_at"):
            if hasattr(item.get(key), "isoformat"):
                item[key] = item[key].isoformat()
        result.append(item)

    return result
