"""
AI chat endpoints (RAG assistant).

Matches controllers/chat_controller.py (prefix: /api/v1/chat):

    POST   /api/v1/chat/ask                            -> ask a question
    POST   /api/v1/chat/disagree                       -> dispute / re-evaluate an answer
    GET    /api/v1/chat/session/{session_id}/summary    -> conversation summary
    DELETE /api/v1/chat/session/{session_id}            -> clear a chat session

IMPORTANT changes vs. the old stub:
  * The backend has no "conversation_id" / "message" fields — it's
    `session_id` + `question`. Generate ONE session_id per browser session
    (see utils.session.get_session_id()) and reuse it for chat, image
    identification, history and compare calls so the backend can tie them
    together.
  * There's no GET /chat/history or GET /chat/{id} route. Full message
    history lives under /api/v1/history (see api/history_api.py), not
    under /chat — /chat/session/{id}/summary only gives a short summary,
    not the full message list.
"""

from api.client import api_client


def ask_question(
    question: str,
    session_id: str | None = None,
    vehicle_context: str | None = None,
    language: str | None = None,
) -> dict:
    """Ask the RAG assistant a question, optionally scoped to a vehicle.

    `vehicle_context` is a free-text description (e.g. "BMW M4 Competition
    2022"), not an id — the backend has nothing to look a detection up by.
    """
    payload = {"question": question}
    if session_id:
        payload["session_id"] = session_id
    if vehicle_context:
        payload["vehicle_context"] = vehicle_context
    if language:
        payload["language"] = language
    return api_client.post("/api/v1/chat/ask", json=payload)


def handle_disagreement(
    session_id: str,
    original_question: str,
    disputed_answer: str,
    user_claim: str | None = None,
    language: str | None = None,
) -> dict:
    """Send a 'that's wrong' correction so the assistant re-evaluates its answer."""
    payload = {
        "session_id": session_id,
        "original_question": original_question,
        "disputed_answer": disputed_answer,
    }
    if user_claim:
        payload["user_claim"] = user_claim
    if language:
        payload["language"] = language
    return api_client.post("/api/v1/chat/disagree", json=payload)


def get_session_summary(session_id: str) -> dict:
    """Short AI-generated summary of the session, not the raw message list."""
    return api_client.get(f"/api/v1/chat/session/{session_id}/summary")


def clear_chat_session(session_id: str) -> dict:
    return api_client.delete(f"/api/v1/chat/session/{session_id}")
# ----------------------------------------------------------------------
# Backward compatibility
# ----------------------------------------------------------------------

def send_message(
    message: str,
    session_id: str | None = None,
    vehicle_context: str | None = None,
    language: str | None = None,
):
    return ask_question(
        question=message,
        session_id=session_id,
        vehicle_context=vehicle_context,
        language=language,
    )