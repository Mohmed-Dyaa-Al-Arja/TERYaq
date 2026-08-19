import textwrap

import streamlit as st

from utils.session import init_session, set_pending_image, set_detection
from utils.theme import init_theme, load_css
from utils.i18n import init_lang, t
from components.navigation import render_navbar
from components.upload_zone import render_upload_zone

st.set_page_config(page_title="Detect Vehicle | Vehicle Vision AI", layout="wide", initial_sidebar_state="collapsed")

init_session()
init_theme()
init_lang()
load_css("detect")
render_navbar(active="nav_detect")

st.markdown(f"## {t('detect_title')}")
st.markdown(f'<p class="vv-text-secondary">{t("detect_subtitle")}</p>', unsafe_allow_html=True)

col_upload, col_tips = st.columns([2, 1], gap="large")

with col_upload:
    uploaded = render_upload_zone()

    st.write("")
    btn_col, notice_col = st.columns([1, 1.7], gap="medium")
    with btn_col:
        start_clicked = st.button(
            f"✨ {t('start_detection')}  →",
            type="primary",
            use_container_width=True,
        )
    with notice_col:
        # NOTE: textwrap.dedent() strips the common leading whitespace that
        # this block's `with`/`if` indentation adds to the triple-quoted
        # string. Without it, Markdown treats the indented lines as an
        # indented code block and renders the raw "<div ...>" tags as text
        # instead of parsing them as HTML.
        st.markdown(
            textwrap.dedent(f"""\
            <div class="vv-secure-notice">
                <div class="vv-secure-icon">🛡️</div>
                <div>
                    <strong>{t('secure_title')}</strong>
                    <span class="vv-secure-desc">{t('secure_desc')}</span>
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    if start_clicked:
        if uploaded is None:
            st.warning(t("please_upload_first"))
        else:
            set_pending_image(uploaded.getvalue(), uploaded.name, uploaded.type or "image/jpeg")
            set_detection(None)  # clear any previous result
            st.switch_page("pages/2_Loading.py")

with col_tips:
    TIPS = [("HD", "tip_1"), ("🚗", "tip_2"), ("☀️", "tip_3"), ("📷", "tip_4")]
    rows_html = "".join(
        f'<div class="vv-tip-row"><div class="vv-tip-icon">{icon}</div><span>{t(key)}</span></div>'
        for icon, key in TIPS
    )
    st.markdown(
        textwrap.dedent(f"""\
        <div class="vv-card-flat">
            <strong>✨ {t('tips_title')}</strong>
            <div style="margin-top:10px;">{rows_html}</div>
        </div>
        """),
        unsafe_allow_html=True,
    )