import textwrap

import streamlit as st

from utils.session import init_session
from utils.theme import init_theme, load_css
from utils.i18n import init_lang, t
from utils.developers import DEVELOPERS
from components.navigation import render_navbar

st.set_page_config(
    page_title="Team Photo | Vehicle Vision AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session()
init_theme()
init_lang()
load_css("team_photo")

render_navbar(active="nav_developers")

# ======================================================
# HEADER
# ======================================================

st.markdown(
    textwrap.dedent(f"""\
    <div>
        <div class="hero-badge">
            📸 Our Amazing Team
        </div>
        <div class="hero-title">
            Team <span>Photo</span>
        </div>
        <div class="hero-description">
            {t("team_photo_subtitle")}
        </div>
    </div>
    """),
    unsafe_allow_html=True,
)

st.write("")

# ======================================================
# IMAGE
# ======================================================

st.markdown('<div class="hero-image">', unsafe_allow_html=True)

st.image(
    "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1600&q=90",
    use_container_width=True,
)

st.markdown("</div>", unsafe_allow_html=True)

st.caption(
    t("team_photo_caption")
)

st.write("")

# ======================================================
# MEMBERS
# ======================================================

st.markdown(
    "### 👨‍💻 Team Members"
)

cols = st.columns(4)

for i, dev in enumerate(DEVELOPERS):

    with cols[i % 4]:

        st.markdown(
            textwrap.dedent(f"""\
            <div class="vv-card profile-card">
                <div class="developer-avatar">
                    {dev["name"][0]}
                </div>
                <div class="developer-name">
                    {dev["name"]}
                </div>
                <div class="developer-role">
                    {dev["role"]}
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

st.write("")

# ======================================================
# BOTTOM
# ======================================================

st.markdown(
    textwrap.dedent(f"""\
    <div class="vv-card" style="display:flex;align-items:center;gap:20px;padding:24px;">
        <div style="font-size:38px;">
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

st.write("")

left, center, right = st.columns([1, 1.2, 1])

with center:

    if st.button(
        f"← {t('nav_developers')}",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/6_Developers.py"
        )