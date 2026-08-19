from __future__ import annotations

from backend.database.repositories.chat_repository import get_history


def get_recent_history(
    session_id: str | None,
    limit: int = 10,
) -> list[dict]:
    if not session_id:
        return []

    return get_history(
        session_id=session_id,
        limit=limit,
    )
