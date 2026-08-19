import streamlit as st

from utils.session import init_session, get_detection, set_detection, get_pending_image, clear_pending_image
from utils.theme import init_theme, load_css
from utils.i18n import init_lang, t
from components.navigation import render_navbar
from components.cards import confidence_badge

st.set_page_config(page_title="Result | Vehicle Vision AI", layout="wide", initial_sidebar_state="collapsed")

init_session()
init_theme()
init_lang()
load_css("result")
render_navbar(active="nav_detect")

st.markdown(f"## {t('result_title')}")

result = get_detection()

if not result:
    st.info(t("no_result_yet"))
    if st.button(t("back_to_detect"), type="primary"):
        st.switch_page("pages/1_Detect.py")
    st.stop()

image_bytes, _, _ = get_pending_image()

# ── Build display values from normalised result ───────────────────────────
make       = result.get("make", "")
model      = result.get("model", "")
year       = result.get("year", "")
body_type  = result.get("body_type", "-")
color      = result.get("color", "-")
confidence = result.get("confidence") or 0.0
if not isinstance(confidence, (int, float)):
    confidence = 0.0

# Fallback: if make/model still empty, try splitting vehicle_name
if not make and result.get("vehicle_name"):
    vn = result["vehicle_name"].replace("_", " ").split()
    year_candidates = [p for p in vn if p.isdigit() and len(p) == 4]
    year = year_candidates[0] if year_candidates else year
    rest = [p for p in vn if p not in year_candidates]
    make  = rest[0] if rest else ""
    model = " ".join(rest[1:]) if len(rest) > 1 else ""

title_parts = [make, model, str(year)]
title = " ".join(p for p in title_parts if p)

# ── Layout ────────────────────────────────────────────────────────────────
img_col, info_col = st.columns([1, 1.4], gap="large")

with img_col:
    if image_bytes:
        st.image(image_bytes, use_container_width=True)

with info_col:
    st.markdown(confidence_badge(confidence), unsafe_allow_html=True)
    st.markdown(f"## {title or 'Vehicle Identified'}")

    specs = st.columns(2)
    with specs[0]:
        st.markdown(f"**{t('spec_make')}**  \n{make or '-'}")
        st.markdown(f"**{t('spec_body_type')}**  \n{body_type}")
    with specs[1]:
        st.markdown(f"**{t('spec_model')}**  \n{model or '-'}")
        st.markdown(f"**{t('spec_color')}**  \n{color}")

    # ── Show the full AI-generated description ────────────────────────────
    answer = result.get("answer", "")
    if answer:
        with st.expander("📋 Full AI Analysis", expanded=False):
            st.markdown(answer)

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button(t("ask_ai"), type="primary", use_container_width=True):
            st.switch_page("pages/4_Chat.py")
    with b2:
        if st.button(t("download_report"), use_container_width=True):
            st.switch_page("pages/11_PDF_Report.py")
    with b3:
        if st.button(t("analyze_another"), use_container_width=True):
            set_detection(None)
            clear_pending_image()
            st.switch_page("pages/1_Detect.py")