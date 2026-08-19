"""Shared navigation bar."""

import streamlit as st

from utils.theme import toggle_theme
from utils.i18n import t, toggle_lang

NAV_ITEMS = [
    ("nav_home", "app.py"),
    ("nav_detect", "pages/1_Detect.py"),
    ("nav_chat", "pages/4_Chat.py"),
    ("nav_features", "pages/5_Features.py"),
    ("nav_developers", "pages/6_Developers.py"),
    ("nav_history", "pages/10_History.py"),
    ("nav_about", "pages/9_About.py"),
]


def render_navbar(active: str = "nav_home") -> None:
    st.markdown('<span class="vv-navbar-marker"></span>', unsafe_allow_html=True)

    cols = st.columns([1.72] + [.84] * len(NAV_ITEMS) + [.50, .68, .72], gap="small")

    with cols[0]:
        st.markdown(
            f'<div class="vv-logo"><div class="vv-logo-icon">V</div>'
            f'<div class="vv-logo-title">{t("brand_name")} <span>{t("brand_suffix")}</span></div></div>',
            unsafe_allow_html=True,
        )

    for i, (key, page) in enumerate(NAV_ITEMS):
        with cols[i + 1]:
            st.page_link(
                page,
                label=t(key),
                use_container_width=True,
                disabled=(key == active),
            )

    with cols[-3]:
        dark = st.session_state.get("theme", "light") == "dark"
        if st.button("☀" if dark else "☾", key="nav_theme", use_container_width=True):
            toggle_theme()
            st.rerun()

    with cols[-2]:
        lang = st.session_state.get("lang", "en")
        if st.button("ع" if lang == "en" else "EN", key="nav_lang", use_container_width=True):
            toggle_lang()
            st.rerun()

    with cols[-1]:
        if st.button(t("login"), key="nav_login", use_container_width=True):
            st.session_state["login_requested"] = True

    if st.session_state.pop("login_requested", False):
        st.info(t("login_notice"))
