import datetime
import textwrap

import streamlit as st

from utils.session import init_session, get_detection
from utils.theme import init_theme, load_css
from utils.i18n import init_lang, t
from components.navigation import render_navbar
from components.cards import confidence_badge
from api.vehicle_api import download_report
from api.client import APIError

st.set_page_config(
    page_title="PDF Report | Vehicle Vision AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session()
init_theme()
init_lang()
load_css("pdf_report")

render_navbar(active="nav_detect")

# =====================================================
# HEADER
# =====================================================

st.markdown(
    textwrap.dedent(f"""\
    <div>
        <div class="hero-badge">
            📄 AI Generated Report
        </div>
        <div class="hero-title">
            PDF <span>Report</span>
        </div>
        <div class="hero-description">
            {t("report_subtitle")}
        </div>
    </div>
    """),
    unsafe_allow_html=True,
)

result = get_detection()

if not result:

    st.info(
        t("report_no_detection")
    )

    if st.button(
        t("back_to_detect"),
        type="primary",
    ):
        st.switch_page(
            "pages/1_Detect.py"
        )

    st.stop()

st.write("")

# =====================================================
# REPORT CARD
# =====================================================

left, right = st.columns(
    [2, 1],
    gap="large",
)

with left:

    st.markdown(
        textwrap.dedent(f"""\
        <div class="vv-card">
            <h2>
                🚗
                {result.get("make","")}
                {result.get("model","")}
                {result.get("year","")}
            </h2>
        </div>
        """),
        unsafe_allow_html=True,
    )

    st.markdown(
        confidence_badge(
            result.get(
                "confidence",
                0,
            )
        ),
        unsafe_allow_html=True,
    )

    st.write("")

    info = [

        (
            t("report_field_id"),
            result.get(
                "detection_id",
                "-"
            ),
        ),

        (
            t("report_field_date"),
            result.get(
                "date",
                datetime.date.today().isoformat(),
            ),
        ),

        (
            t("report_field_vehicle"),
            f"{result.get('body_type','-')} • {result.get('color','-')}",
        ),

        (
            t("report_field_confidence"),
            f"{result.get('confidence',0):.1f}%",
        ),

    ]

    for label, value in info:

        st.markdown(
            textwrap.dedent(f"""\
            <div class="report-row">
                <strong>
                    {label}
                </strong>
                <span>
                    {value}
                </span>
            </div>
            """),
            unsafe_allow_html=True,
        )

with right:

    st.markdown(
        textwrap.dedent("""\
        <div class="vv-card report-download">
            <div class="report-icon">
                📄
            </div>
            <h3>
                Download Report
            </h3>
            <p class="vv-text-secondary">
                Generate a professional report
                containing the complete
                detection result.
            </p>
        </div>
        """),
        unsafe_allow_html=True,
    )

st.write("")

# =====================================================
# DOWNLOAD
# =====================================================

if st.button(
    t("report_generate"),
    type="primary",
    use_container_width=True,
):

    with st.spinner(
        t("report_generating")
    ):

        try:

            pdf_bytes = download_report(
                result.get(
                    "detection_id",
                    "",
                )
            )

            filename = (
                f"{result.get('detection_id','report')}.pdf"
            )

            mime = "application/pdf"

            st.success(
                t("report_ready")
            )

        except APIError:

            st.warning(
                t("report_demo_notice")
            )

            pdf_bytes = (
                f"""
Vehicle Vision AI

Detection Report

Vehicle :
{result.get("make")}
{result.get("model")}

Confidence :
{result.get("confidence"):.1f}%

"""
            ).encode()

            filename = "Demo_Report.txt"

            mime = "text/plain"

    st.download_button(

        label=t("download_report"),

        data=pdf_bytes,

        file_name=filename,

        mime=mime,

        use_container_width=True,

    )