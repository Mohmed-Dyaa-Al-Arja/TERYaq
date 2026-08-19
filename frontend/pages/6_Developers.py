import textwrap

import streamlit as st

from utils.session import init_session
from utils.theme import init_theme, load_css
from utils.i18n import init_lang, t
from utils.developers import DEVELOPERS
from components.navigation import render_navbar

st.set_page_config(
    page_title="Developers | Vehicle Vision AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session()
init_theme()
init_lang()
load_css("developers")

render_navbar(active="nav_developers")

# ==========================================================
# HEADER
# ==========================================================

st.markdown(
    textwrap.dedent(f"""\
    <div style="margin-bottom:30px;">
        <h1 class="hero-title" style="font-size:2.6rem;margin-bottom:8px;">
            Our <span>Developers</span>
        </h1>
        <p class="hero-description" style="max-width:700px;margin-bottom:0;">
            {t("developers_subtitle")}
        </p>
    </div>
    """),
    unsafe_allow_html=True,
)

# ==========================================================
# DEVELOPERS
# ==========================================================

cols = st.columns(4)

for i, (col, dev) in enumerate(zip(cols, DEVELOPERS)):

    with col:

        avatar = dev["name"][0].upper()

        skills_html = "".join(
            f'<span class="vv-badge vv-badge-primary">{skill}</span>'
            for skill in dev["skills"]
        )

        st.markdown(
            textwrap.dedent(f"""\
            <div class="vv-card developer-card">
                <div class="developer-avatar">
                    {avatar}
                </div>
                <div class="developer-name">
                    {dev["name"]}
                </div>
                <div class="developer-role">
                    {dev["role"]}
                </div>
                <div class="developer-bio">
                    {dev["bio"]}
                </div>
                <div class="developer-skills">
                    {skills_html}
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

        if st.button(
            f"👤 {t('view_profile')}",
            key=f"developer_{i}",
            use_container_width=True,
        ):
            st.session_state.selected_developer = i
            st.switch_page("pages/7_Developer_Profile.py")

# ==========================================================
# TEAM PHOTO
# ==========================================================

st.write("")

center1, center2, center3 = st.columns([1, 1.2, 1])

with center2:

    if st.button(
        f"📷 {t('view_team_photo')}",
        use_container_width=True,
    ):
        st.switch_page("pages/8_Team_Photo.py")

# ==========================================================
# BOTTOM BANNER
# ==========================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    textwrap.dedent(f"""\
    <div class="vv-card" style="display:flex;align-items:center;gap:20px;padding:28px;">
        <div style="font-size:40px;">
            🚀
        </div>
        <div>
            <h3 style="margin:0;">
                {t("team_tagline_title")}
            </h3>
            <p class="vv-text-secondary" style="margin-top:6px;margin-bottom:0;">
                {t("team_tagline_desc")}
            </p>
        </div>
    </div>
    """),
    unsafe_allow_html=True,
)