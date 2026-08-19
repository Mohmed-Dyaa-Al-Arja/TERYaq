import textwrap

import streamlit as st

from api.chat_api import ask_question
from api.client import APIError
from components.navigation import render_navbar
from utils.i18n import init_lang, t
from utils.session import get_detection, init_session
from utils.theme import init_theme, load_css


st.set_page_config(
    page_title="AI Assistant | Vehicle Vision AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session()
init_theme()
init_lang()
load_css("chat")
render_navbar(active="nav_chat")

# ── Session state defaults ────────────────────────────────────────────────
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "session_id" not in st.session_state or not st.session_state.session_id:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())


def render_message(role: str, content: str):
    """Render a single chat bubble — no html.escape so markdown renders correctly."""
    is_user  = role == "user"
    avatar   = "U" if is_user else "AI"
    label    = "You" if is_user else "AI Assistant"
    role_class = " vv-chat-message-user" if is_user else ""
    tools    = "" if is_user else '<div class="vv-chat-tools">⧉ ♡ ⋯</div>'

    # User content is plain text typed into the chat box — safe to inject directly.
    # AI content comes from the backend (trusted, not user-controlled HTML).
    # We convert newlines to <br> so multi-line answers render properly.
    safe_content = str(content).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

    st.markdown(
        textwrap.dedent(f"""\
        <div class="vv-chat-message{role_class}">
            <div class="vv-chat-avatar">{avatar}</div>
            <div class="vv-chat-message-body">
                <div class="vv-chat-message-label">{label}</div>
                <div class="vv-chat-bubble">{safe_content}</div>
                {tools}
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )


# ── Detection context ─────────────────────────────────────────────────────
detection = get_detection()

vehicle_context: str | None = None
if detection:
    parts = [
        detection.get("make", ""),
        detection.get("model", ""),
        str(detection.get("year", "")),
    ]
    vc = " ".join(p for p in parts if p).strip()
    if not vc and detection.get("vehicle_name"):
        vc = detection["vehicle_name"].replace("_", " ")
    vehicle_context = vc or None

# ── Layout ────────────────────────────────────────────────────────────────
side, main = st.columns([1, 2.55], gap="large")

with side:
    st.markdown(
        textwrap.dedent(f"""\
        <section class="vv-chat-card">
            <div class="vv-chat-card-title">💬 {t("chat_about_title")}</div>
            <p class="vv-chat-card-desc">{t("chat_about_desc")}</p>
        </section>
        """),
        unsafe_allow_html=True,
    )

    if detection:
        vehicle_label = vehicle_context or "-"
        conf = detection.get("confidence", 0)
        st.markdown(
            textwrap.dedent(f"""\
            <section class="vv-chat-card">
                <div class="vv-chat-card-title">🚗 {t("chat_detected_vehicle")}</div>
                <p class="vv-chat-card-desc">
                    <strong>{vehicle_label}</strong><br>
                    {t("chat_confidence")} : {conf:.1f}%
                </p>
            </section>
            """),
            unsafe_allow_html=True,
        )

    st.markdown(
        textwrap.dedent(f"""\
        <section class="vv-chat-card">
            <p class="vv-chat-suggest-label">⚡ {t("chat_suggested")}</p>
        </section>
        """),
        unsafe_allow_html=True,
    )

    for key in ["sugg_fuel", "sugg_hp", "sugg_maintenance", "sugg_reliability", "sugg_price", "sugg_alternatives"]:
        label = t(key)
        if st.button(label, key=f"chat_{key}", use_container_width=True):
            st.session_state["_pending_prompt"] = label
            st.rerun()

    st.markdown(
        textwrap.dedent("""\
        <section class="vv-chat-card vv-chat-info">
            <div class="vv-chat-card-title">🤖 AI Assistant</div>
            <p class="vv-chat-card-desc">
                Powered by advanced AI models and real-time vehicle knowledge.
            </p>
            <ul class="vv-chat-perks">
                <li>Real-time Information</li>
                <li>Accurate Answers</li>
                <li>Always Updated</li>
            </ul>
        </section>
        """),
        unsafe_allow_html=True,
    )

with main:
    title_col, clear_col = st.columns([4.3, 1], vertical_alignment="center")

    with title_col:
        st.markdown(
            textwrap.dedent(f"""\
            <div class="vv-chat-header">
                <div class="vv-chat-bot-icon">🤖</div>
                <div>
                    <h2>{t("chat_title")}</h2>
                    <p>{t("chat_about_desc")}</p>
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with clear_col:
        if st.button("🗑 Clear Chat", key="clear_chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

    st.markdown('<div class="vv-chat-shell">', unsafe_allow_html=True)

    chat_container = st.container(height=500)

    with chat_container:
        if not st.session_state.chat_messages:
            st.markdown(
                textwrap.dedent(f"""\
                <div class="vv-chat-empty">
                    <div>
                        <strong>👋 Welcome!</strong>
                        {t("chat_hello")}
                    </div>
                </div>
                """),
                unsafe_allow_html=True,
            )
        else:
            for message in st.session_state.chat_messages:
                render_message(message["role"], message["content"])

    st.markdown("</div>", unsafe_allow_html=True)

    prompt = st.chat_input(t("chat_placeholder"))

    st.markdown(
        '<p class="vv-chat-input-note">AI responses may contain mistakes. Please verify important information.</p>',
        unsafe_allow_html=True,
    )

    pending      = st.session_state.pop("_pending_prompt", None)
    final_prompt = prompt or pending

    if final_prompt:
        st.session_state.chat_messages.append({"role": "user", "content": final_prompt})

        try:
            response = ask_question(
                question=final_prompt,
                session_id=st.session_state.session_id,
                vehicle_context=vehicle_context,
            )

            # Backend returns {"answer": "...", "vehicle_name": ..., "confidence": ...}
            reply = (
                response.get("answer")
                or response.get("reply")
                or response.get("response")
                or response.get("message")
                or str(response)
            )

        except APIError as exc:
            reply = f"{t('chat_demo_notice')} ({exc})"

        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()