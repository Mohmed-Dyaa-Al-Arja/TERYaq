import streamlit as st

from utils.session import init_session
from utils.theme import init_theme, load_css
from utils.i18n import init_lang, t
from components.navigation import render_navbar
from components.cards import stat_card

st.set_page_config(page_title="About | Vehicle Vision AI", layout="wide", initial_sidebar_state="collapsed")

init_session()
init_theme()
init_lang()
load_css("about")
render_navbar(active="nav_about")

left, right = st.columns([1.2, 1], gap="large")

with left:
    st.markdown(f'<span class="vv-badge vv-badge-primary">{t("about_badge")}</span>', unsafe_allow_html=True)
    st.markdown(f"## {t('about_title')}")
    st.markdown(f'<p class="vv-text-secondary">{t("about_desc")}</p>', unsafe_allow_html=True)

    st.markdown(f"**{t('about_mission_title')}**")
    st.markdown(f'<p class="vv-text-secondary">{t("about_mission_desc")}</p>', unsafe_allow_html=True)
    st.markdown(f"**{t('about_vision_title')}**")
    st.markdown(f'<p class="vv-text-secondary">{t("about_vision_desc")}</p>', unsafe_allow_html=True)

with right:
    st.image(
        "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=900&q=80",
        use_container_width=True,
    )

st.write("")
s1, s2, s3 = st.columns(3)
with s1:
    stat_card("2024", t("stat_founded"))
with s2:
    stat_card("10K+", t("stat_users"))
with s3:
    stat_card("50K+", t("stat_analyzed"))

st.markdown('<div class="vv-divider"></div>', unsafe_allow_html=True)
st.markdown(f"### {t('tech_stack_title')}")
st.markdown(
    '<p class="vv-text-secondary">Python &middot; Streamlit &middot; FastAPI &middot; OpenCV &middot; '
    "FAISS &middot; MongoDB &middot; Groq &middot; Web Scraping</p>",
    unsafe_allow_html=True,
)