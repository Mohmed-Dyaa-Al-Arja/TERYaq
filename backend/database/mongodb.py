from __future__ import annotations

import os
from functools import lru_cache

from pymongo import MongoClient


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    uri = os.getenv(
        "MONGODB_URI",
        "mongodb://localhost:27017",
    )
    return MongoClient(uri, serverSelectionTimeoutMS=3000)


def get_database():
    name = os.getenv("MONGODB_DATABASE", "teryaq")
    return get_client()[name]


def ping_database() -> str:
    try:
        get_client().admin.command("ping")
        return "connected"
    except Exception:
        return "unavailable"


def init_indexes() -> None:
    db = get_database()

    db.sessions.create_index("session_id", unique=True)
    db.messages.create_index(
        [("session_id", 1), ("created_at", 1)]
    )
    db.memories.create_index(
        [("session_id", 1), ("updated_at", -1)]
    )
