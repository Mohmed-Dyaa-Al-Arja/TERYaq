"""
Conversation & vehicle history endpoints.

Matches controllers/history_controller.py (prefix: /api/v1/history):

    GET    /api/v1/history/session/{session_id}              page, page_size
    GET    /api/v1/history/session/{session_id}/vehicles      vehicles seen in that session
    GET    /api/v1/history/search                             q, session_id?, limit
    GET    /api/v1/history/vehicle/{vehicle_name}              limit
    DELETE /api/v1/history/session/{session_id}                delete a whole session's history
    DELETE /api/v1/history/message/{message_id}                delete a single message
    GET    /api/v1/history/export/{session_id}                 export session as JSON

This is a NEW file — the old vehicle_api.py had a `get_detection_history()`
that doesn't map to anything real. This is the actual replacement for
"the History page" (pages/10_History.py) and it works off `session_id`
(and vehicle name for cross-session lookups), not a `detection_id`.
"""

from api.client import api_client


def get_session_history(session_id: str, page: int = 1, page_size: int = 20) -> dict:
    return api_client.get(
        f"/api/v1/history/session/{session_id}",
        params={"page": page, "page_size": page_size},
    )


def get_session_vehicles(session_id: str) -> dict:
    """All vehicles identified within one session (for the sidebar / history list)."""
    return api_client.get(f"/api/v1/history/session/{session_id}/vehicles")


def search_history(q: str, session_id: str | None = None, limit: int = 20) -> dict:
    params = {"q": q, "limit": limit}
    if session_id:
        params["session_id"] = session_id
    return api_client.get("/api/v1/history/search", params=params)


def get_vehicle_history(vehicle_name: str, limit: int = 20) -> dict:
    """Every past mention/detection of a given vehicle, across sessions."""
    return api_client.get(f"/api/v1/history/vehicle/{vehicle_name}", params={"limit": limit})


def delete_session_history(session_id: str) -> dict:
    return api_client.delete(f"/api/v1/history/session/{session_id}")


def delete_message(message_id: str) -> dict:
    return api_client.delete(f"/api/v1/history/message/{message_id}")


def export_session(session_id: str) -> dict:
    """Full JSON export of a session — useful as the data source for a
    client-side PDF report if the backend never gets a dedicated /report route."""
    return api_client.get(f"/api/v1/history/export/{session_id}")