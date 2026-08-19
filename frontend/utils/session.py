"""Small helpers around st.session_state so pages don't repeat key names."""

import uuid

import streamlit as st

# Keys that belong to each "concern" — used by the clear_* helpers below so
# adding a new session key only means updating one dict, not every page.
_CHAT_KEYS = ["conversation_id", "chat_messages"]
_DETECTION_KEYS = ["last_detection", "pending_image", "pending_image_name", "pending_image_type"]
_MISC_KEYS = ["selected_developer", "history_cache"]


def init_session() -> None:
    defaults = {
        "theme": "light",
        "lang": "en",
        # One id shared by chat / image / history / compare calls for this
        # browser session — the backend has no concept of its own session,
        # it just trusts whatever session_id it's given. Generated once and
        # kept for as long as the tab stays open.
        "session_id": str(uuid.uuid4()),
        "last_detection": None,      # dict returned by api.vehicle_api.identify_vehicle
        "pending_image": None,       # bytes waiting to be processed on the Loading page
        "pending_image_name": None,
        "pending_image_type": None,
        "conversation_id": None,     # kept for backward-compat with existing pages; not sent to the backend
        "chat_messages": [],         # list of {"role": "user"|"assistant", "content": str}
        "selected_developer": None,  # index into DEVELOPERS, used by Developer Profile page
        "history_cache": None,       # demo/fallback detection history list
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_session_id() -> str:
    """The one id to pass to every backend call (chat_api, vehicle_api, history_api, compare_api)."""
    return st.session_state.session_id


def set_detection(result: dict) -> None:
    st.session_state.last_detection = result


def get_detection() -> dict | None:
    return st.session_state.get("last_detection")


def set_pending_image(image_bytes: bytes, name: str, content_type: str) -> None:
    st.session_state.pending_image = image_bytes
    st.session_state.pending_image_name = name
    st.session_state.pending_image_type = content_type


def get_pending_image():
    return (
        st.session_state.get("pending_image"),
        st.session_state.get("pending_image_name"),
        st.session_state.get("pending_image_type"),
    )


def clear_pending_image() -> None:
    st.session_state.pending_image = None
    st.session_state.pending_image_name = None
    st.session_state.pending_image_type = None


# --------------------------------------------------------------------- #
# Cleanup helpers — use these instead of resetting keys by hand on a page.
# Each one leaves the OTHER concerns untouched (e.g. clearing chat does not
# wipe the last detection result). None of them reset session_id — a fresh
# session_id means the backend loses the ability to tie history together,
# so only rotate it on an explicit "start over completely" action.
# --------------------------------------------------------------------- #

def clear_chat() -> None:
    """Reset the local chat display only (e.g. 'New conversation' button).

    This does NOT clear the session on the backend — call
    chat_api.clear_chat_session(get_session_id()) too if you want that.
    """
    st.session_state.conversation_id = None
    st.session_state.chat_messages = []


def clear_detection() -> None:
    """Reset the last detection result + any pending image waiting to be processed."""
    st.session_state.last_detection = None
    clear_pending_image()


def new_session() -> str:
    """Rotate to a brand-new session_id (full 'start over', loses backend history linkage)."""
    st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id


def clear_all_session() -> None:
    """Full reset of every temporary/local value (keeps theme + lang + session_id)."""
    for key in _CHAT_KEYS + _DETECTION_KEYS + _MISC_KEYS:
        st.session_state[key] = [] if key == "chat_messages" else None