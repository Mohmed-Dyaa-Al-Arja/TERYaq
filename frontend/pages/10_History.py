import textwrap

import streamlit as st

from utils.session import (
    init_session,
    set_detection,
    clear_pending_image,
)
from utils.theme import init_theme, load_css
from utils.i18n import init_lang, t
from components.navigation import render_navbar
from components.cards import confidence_badge
from api.vehicle_api import (
    get_detection_history,
    delete_detection,
)
from api.client import APIError

st.set_page_config(
    page_title="History | Vehicle Vision AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session()
init_theme()
init_lang()
load_css("history")

render_navbar(active="nav_history")

# =====================================================
# HEADER
# =====================================================

left, right = st.columns([2.3, 2])

with left:

    st.markdown(
        textwrap.dedent(f"""\
        <div>
            <div class="hero-badge">
                📋 Detection Records
            </div>
            <div class="hero-title">
                Detection <span>History</span>
            </div>
            <div class="hero-description">
                {t("history_subtitle")}
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )

DEMO_HISTORY = [

    {
        "detection_id": "VVA-DEMO-0001",
        "make": "BMW",
        "model": "M4 Competition",
        "year": 2022,
        "body_type": "Coupe",
        "color": "Blue",
        "confidence": 96.4,
        "date": "2026-07-28"
    },

    {
        "detection_id": "VVA-DEMO-0002",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2021,
        "body_type": "Sedan",
        "color": "White",
        "confidence": 92.1,
        "date": "2026-07-20"
    },

    {
        "detection_id": "VVA-DEMO-0003",
        "make": "Tesla",
        "model": "Model 3",
        "year": 2023,
        "body_type": "Sedan",
        "color": "Red",
        "confidence": 98.7,
        "date": "2026-07-11"
    },

]

if st.session_state.history_cache is None:

    try:

        st.session_state.history_cache = (
            get_detection_history()
            .get("items", [])
        )

    except APIError:

        st.session_state.history_cache = DEMO_HISTORY

items = st.session_state.history_cache or []

with right:

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.markdown(
            textwrap.dedent(f"""\
            <div class="vv-card vv-stat-card">
                <div class="vv-stat-value">
                    {len(items)}
                </div>
                <div class="vv-stat-label">
                    Total
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with s2:
        st.markdown(
            textwrap.dedent("""\
            <div class="vv-card vv-stat-card">
                <div class="vv-stat-value">
                    98%
                </div>
                <div class="vv-stat-label">
                    Accuracy
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with s3:
        st.markdown(
            textwrap.dedent("""\
            <div class="vv-card vv-stat-card">
                <div class="vv-stat-value">
                    AI
                </div>
                <div class="vv-stat-label">
                    Powered
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with s4:
        st.markdown(
            textwrap.dedent("""\
            <div class="vv-card vv-stat-card">
                <div class="vv-stat-value">
                    PDF
                </div>
                <div class="vv-stat-label">
                    Reports
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

st.write("")

query = st.text_input(
    "",
    placeholder=t("history_search"),
)

if query:

    q = query.lower()

    items = [

        item

        for item in items

        if q in (
            f"{item.get('make','')} "
            f"{item.get('model','')}"
        ).lower()

    ]

if not items:

    st.info(t("history_empty"))

    if st.button(
        t("start_detection"),
        type="primary",
    ):

        st.switch_page("pages/1_Detect.py")

    st.stop()

st.markdown(
    '<div class="vv-divider"></div>',
    unsafe_allow_html=True,
)

for item in items:

    st.markdown(
        '<div class="vv-card history-card">',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(
        [3.2, 1.1, 1.5, 2.1]
    )

    with col1:

        st.markdown(
            textwrap.dedent(f"""\
            <div class="history-title">
                🚗
                <strong>
                    {item.get('make','')}
                    {item.get('model','')}
                </strong>
            </div>
            <div class="history-subtitle">
                {item.get("year","-")}
                •
                {item.get("body_type","-")}
                •
                {item.get("color","-")}
            </div>
            <div class="history-id">
                {item.get("detection_id","-")}
            </div>
            """),
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            confidence_badge(
                item.get(
                    "confidence",
                    0,
                )
            ),
            unsafe_allow_html=True,
        )

        st.progress(
            item.get(
                "confidence",
                0,
            )
            / 100
        )

    with col3:

        st.markdown(
            textwrap.dedent(f"""\
            <div class="history-date">
                📅
                {item.get("date","-")}
            </div>
            """),
            unsafe_allow_html=True,
        )

    with col4:

        b1, b2, b3 = st.columns(3)

        with b1:

            if st.button(
                "👁 View",
                key=f"view_{item['detection_id']}",
                use_container_width=True,
            ):

                set_detection(item)

                clear_pending_image()

                st.switch_page(
                    "pages/3_Result.py"
                )

        with b2:

            if st.button(
                "📄 PDF",
                key=f"pdf_{item['detection_id']}",
                use_container_width=True,
            ):

                set_detection(item)

                st.switch_page(
                    "pages/11_PDF_Report.py"
                )

        with b3:

            if st.button(
                "🗑",
                key=f"delete_{item['detection_id']}",
                use_container_width=True,
            ):

                try:

                    delete_detection(
                        item["detection_id"]
                    )

                except APIError:

                    pass

                st.session_state.history_cache = [

                    i

                    for i in st.session_state.history_cache

                    if i["detection_id"]
                    != item["detection_id"]

                ]

                st.toast(
                    t("history_deleted")
                )

                st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.write("")