import textwrap
from pathlib import Path

import streamlit as st

from utils.session import init_session
from utils.theme import init_theme, load_css
from utils.i18n import init_lang, t
from utils.developers import DEVELOPERS
from components.navigation import render_navbar

st.set_page_config(
    page_title="Developer Profile | Vehicle Vision AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session()
init_theme()
init_lang()
load_css("developer_profile")

render_navbar(active="nav_developers")

idx = st.session_state.get("selected_developer")

dev = (
    DEVELOPERS[idx]
    if idx is not None and 0 <= idx < len(DEVELOPERS)
    else None
)

if dev is None:

    st.info(t("profile_not_found"))

    if st.button(
        t("profile_back"),
        type="primary",
    ):
        st.switch_page("pages/6_Developers.py")

    st.stop()

# =====================================================
# HEADER
# =====================================================

back, title = st.columns([1, 5])

with back:

    if st.button(
        f"← {t('profile_back')}",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/6_Developers.py"
        )

with title:

    st.markdown(
        textwrap.dedent(f"""\
        <div>
            <div class="hero-badge">
                👨‍💻 Developer
            </div>
            <div class="hero-title">
                {dev["name"]}
            </div>
            <div class="hero-description">
                {dev["role"]}
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )

st.write("")

# =====================================================
# CONTENT
# =====================================================

left, right = st.columns(
    [1, 2],
    gap="large",
)

with left:

    # ── Photo or avatar ───────────────────────────────
    # Photos are in frontend/pages/img/ (same folder as this file)
    _PAGES_DIR = Path(__file__).resolve().parent
    photo_file = _PAGES_DIR / "img" / Path(dev.get("photo", "")).name

    if dev.get("photo") and photo_file.exists():
        st.image(str(photo_file), use_container_width=True)
    else:
        st.markdown(
            textwrap.dedent(f"""\
            <div class="vv-card profile-card">
                <div class="developer-avatar profile-avatar">
                    {dev["name"][0]}
                </div>
                <h2>
                    {dev["name"]}
                </h2>
                <div class="developer-role">
                    {dev["role"]}
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

with right:

    st.markdown(
        textwrap.dedent(f"""\
        <div class="vv-card">
            <h3>
                About
            </h3>
            <p class="vv-text-secondary">
                {dev["bio"]}
            </p>
        </div>
        """),
        unsafe_allow_html=True,
    )

    st.write("")

    st.markdown(
        textwrap.dedent(f"""\
        <div class="vv-card">
            <h3>
                {t("profile_contact")}
            </h3>
            <p>
                📱 {dev["phone"]}
            </p>
            <p>
                🐙 <a href="{dev["github"]}" target="_blank">{dev["github"]}</a>
            </p>
            <p>
                💼 <a href="{dev["linkedin"]}" target="_blank">{dev["linkedin"]}</a>
            </p>
        </div>
        """),
        unsafe_allow_html=True,
    )

    st.write("")

    st.markdown(
        f"### {t('profile_skills')}"
    )

    cols = st.columns(4)

    for i, skill in enumerate(dev["skills"]):

        with cols[i % 4]:

            st.markdown(
                f'<span class="vv-badge vv-badge-primary">{skill}</span>',
                unsafe_allow_html=True,
            )