import textwrap

import streamlit as st

from utils.session import init_session
from utils.theme import init_theme, load_css
from utils.i18n import init_lang, t
from components.navigation import render_navbar
from components.cards import feature_card, stat_card

st.set_page_config(
    page_title="Features | Vehicle Vision AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session()
init_theme()
init_lang()
load_css("features")
render_navbar(active="nav_features")

# ── Hero ──────────────────────────────────────────────────────────────────
hero_left, hero_right = st.columns([0.95, 1.05], gap="medium")

with hero_left:
    st.markdown(
        textwrap.dedent("""\
        <div class="hero-badge">✨ AI Powered</div>
        <div class="hero-title">Powerful <br><span>Features</span></div>
        """),
        unsafe_allow_html=True,
    )
    st.markdown(
        textwrap.dedent(f"""\
        <div class="hero-description">{t("features_subtitle")}</div>
        """),
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚗 " + t("start_detection"), type="primary", use_container_width=True):
            st.switch_page("pages/1_Detect.py")
    with c2:
        if st.button("👥 " + t("nav_developers"), use_container_width=True):
            st.switch_page("pages/6_Developers.py")

with hero_right:
    st.markdown('<div class="hero-image">', unsafe_allow_html=True)
    # ✅ page_2.png — the new hero image
    st.image("img/page_2.png", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Features grid ─────────────────────────────────────────────────────────
FEATURES = [
    ("f_detect_t", "f_detect_d"),
    ("f_instant_t", "f_instant_d"),
    ("f_specs_t", "f_specs_d"),
    ("f_assistant_t", "f_assistant_d"),
    ("f_market_t", "f_market_d"),
    ("f_sources_t", "f_sources_d"),
    ("f_export_t", "f_export_d"),
    ("f_secure_t", "f_secure_d"),
]

for row_start in range(0, len(FEATURES), 4):
    cols = st.columns(4)
    for col, (title_key, desc_key) in zip(cols, FEATURES[row_start:row_start + 4]):
        with col:
            feature_card(t(title_key), t(desc_key))
    st.write("")

# ── Stats ─────────────────────────────────────────────────────────────────
st.markdown('<div class="vv-divider"></div>', unsafe_allow_html=True)
s1, s2, s3, s4 = st.columns(4)
with s1:
    stat_card("98%+", t("stat_accuracy"))
with s2:
    stat_card("50K+", t("stat_images"))
with s3:
    stat_card("100%", t("stat_ai_powered"))
with s4:
    stat_card("24/7", t("stat_support"))