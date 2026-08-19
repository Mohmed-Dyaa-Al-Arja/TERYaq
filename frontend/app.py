import base64
from pathlib import Path

import streamlit as st

from utils.session import init_session
from utils.theme import init_theme, load_css
from utils.i18n import init_lang, t
from components.navigation import render_navbar
from components.cards import stat_card, feature_card

st.set_page_config(
    page_title="Vehicle Vision AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session()
init_theme()
init_lang()
load_css("home")
render_navbar(active="nav_home")

APP_DIR = Path(__file__).resolve().parent
IMG_DIR = APP_DIR / "img"

theme = st.session_state.get("theme", "light")
lang = st.session_state.get("lang", "en")


@st.cache_data(show_spinner=False)
def _img_data_uri(path_str: str) -> str:
    """Cache image encoding so theme/language reruns do not reread the image."""
    path = Path(path_str)
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


car_path = IMG_DIR / (
    "car_light_page1.png" if theme == "light" else "car_dark_page1.png"
)
robot_path = IMG_DIR / (
    "robot_light_page1.png" if theme == "light" else "robot_dark_page1.png"
)

car_uri = _img_data_uri(str(car_path))
robot_uri = _img_data_uri(str(robot_path))


def render_hero_text() -> None:
    st.markdown(
        f"""
        <div class="vv-hero-copy">
            <div class="hero-badge">✦ {t("hero_badge")}</div>
            <h1 class="hero-title">
                {t("hero_title_1")}<br><span>{t("hero_title_2")}</span>
            </h1>
            <div class="hero-description">{t("hero_subtitle")}</div>
            <div class="hero-users">
                <div class="hero-avatar-stack">
                    <span>👩🏻</span><span>👨🏻</span><span>🧑🏻</span><span>👨🏽</span>
                </div>
                <div class="hero-users-number">
                    <strong>10+</strong>
                    <span>{t("stat_users")}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Buttons are rendered INSIDE the same Streamlit column as the text.
    # This prevents them from drifting beside the vehicle image.
    btn1, btn2 = st.columns(2, gap="medium")

    with btn1:
        if st.button(
            "✦ " + t("start_detection") + " →",
            type="primary",
            use_container_width=True,
            key="home_detect",
        ):
            st.switch_page("pages/1_Detect.py")

    with btn2:
        if st.button(
            t("learn_more") + " ▷",
            use_container_width=True,
            key="home_features",
        ):
            st.switch_page("pages/5_Features.py")


def render_hero_car() -> None:
    st.markdown(
        f"""
        <div class="vv-car-stage">
            <div class="vv-car-glow"></div>
            <div class="vv-orbit orbit1"></div>
            <div class="vv-orbit orbit2"></div>
            <div class="vv-orbit orbit3"></div>
            <span class="vv-particle p1"></span>
            <span class="vv-particle p2"></span>
            <span class="vv-particle p3"></span>
            <span class="vv-particle p4"></span>
            <span class="vv-particle p5"></span>
            <span class="vv-particle p6"></span>
            <img class="vv-car-art" src="{car_uri}" alt="Vehicle">
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HERO
# EN: text + buttons LEFT, car RIGHT
# AR: car LEFT, text + buttons RIGHT
# ============================================================
st.markdown('<span class="vv-home-hero-marker"></span>', unsafe_allow_html=True)

hero_left, hero_right = st.columns([1, 1], gap="large")

if lang == "ar":
    with hero_left:
        render_hero_car()
    with hero_right:
        render_hero_text()
else:
    with hero_left:
        render_hero_text()
    with hero_right:
        render_hero_car()


# ============================================================
# SIX FEATURE CARDS
# ============================================================
st.markdown('<div class="vv-features-gap"></div>', unsafe_allow_html=True)

feature_data = [
    ("scan", "feat_detect_title", "feat_detect_desc"),
    ("chip", "feat_process_title", "feat_process_desc"),
    ("search", "feat_extract_title", "feat_extract_desc"),
    ("chart", "feat_results_title", "feat_results_desc"),
    ("shield", "secure_title", "secure_desc"),
    ("headset", "support_title", "support_desc"),
]

feature_cols = st.columns(6, gap="medium")
for col, (icon, title, desc) in zip(feature_cols, feature_data):
    with col:
        feature_card(t(title), t(desc), icon=icon)


# ============================================================
# STATS + AI ASSISTANT
# ============================================================
st.markdown('<div class="vv-bottom-gap"></div>', unsafe_allow_html=True)

stats_col, assistant_col = st.columns([2.15, 1], gap="medium")

stats = [
    ("accuracy", "98%+", t("stat_accuracy")),
    ("image", "500K+", t("stat_images")),
    ("chip", "100%", t("stat_ai_powered")),
    ("clock", "24/7", t("stat_support")),
]

with stats_col:
    stat_cols = st.columns(4, gap="medium")
    for col, (icon, value, label) in zip(stat_cols, stats):
        with col:
            stat_card(value, label, icon=icon)

with assistant_col:
    st.markdown(
        f"""
        <div class="vv-assistant-card">
            <div class="vv-assistant-copy">
                <h3>{t("chat_about_title")}</h3>
                <p>{t("chat_about_desc")}</p>
            </div>
            <div class="vv-assistant-robot">
                <img src="{robot_uri}" alt="AI Assistant">
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Marker makes the native Streamlit button targetable without overlap.
    st.markdown('<span class="vv-assistant-button-marker"></span>', unsafe_allow_html=True)

    if st.button(
        t("chat_title") + " →",
        key="home_chat",
        use_container_width=False,
    ):
        st.switch_page("pages/4_Chat.py")