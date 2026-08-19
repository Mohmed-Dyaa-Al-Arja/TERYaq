import re
import time
import streamlit as st

from utils.session import init_session, set_detection, get_pending_image
from utils.theme import init_theme, load_css
from utils.i18n import init_lang, t
from components.navigation import render_navbar
from api.vehicle_api import detect_vehicle
from api.client import APIError

st.set_page_config(page_title="Analyzing | Vehicle Vision AI", layout="wide", initial_sidebar_state="collapsed")

init_session()
init_theme()
init_lang()
load_css("loading")
render_navbar(active="nav_detect")

st.markdown(f"## {t('loading_title')}")
st.markdown(f'<p class="vv-text-secondary">{t("loading_subtitle")}</p>', unsafe_allow_html=True)

image_bytes, image_name, image_type = get_pending_image()

if image_bytes is None:
    st.info(t("no_pending_image"))
    if st.button(t("back_to_detect"), type="primary"):
        st.switch_page("pages/1_Detect.py")
    st.stop()

PROCESSING_STEPS = [
    "step_upload",
    "step_preprocess",
    "step_extract",
    "step_vector_db",
    "step_kb",
    "step_prices",
    "step_generate",
    "step_finalize",
]

status_box = st.empty()
progress = st.progress(0)

for i, step_key in enumerate(PROCESSING_STEPS):
    status_box.markdown(
        f'<div class="vv-step-row active"><div class="vv-step-icon active">-</div>{t(step_key)}...</div>',
        unsafe_allow_html=True,
    )
    time.sleep(0.15)
    progress.progress(int((i + 1) / len(PROCESSING_STEPS) * 100))


def _parse_vehicle_name(vehicle_name: str) -> dict:
    """
    Parse "FIAT_500_Abarth_2012" -> {"make": "FIAT", "model": "500 Abarth", "year": "2012"}
    The backend returns vehicle_name in Stanford Cars format: MAKE_MODEL_YEAR
    where the last token is always the 4-digit year.
    """
    if not vehicle_name:
        return {"make": "", "model": "", "year": ""}
    parts = vehicle_name.split("_")
    year = parts[-1] if (len(parts[-1]) == 4 and parts[-1].isdigit()) else ""
    rest = parts[:-1] if year else parts
    make = rest[0].capitalize() if rest else ""
    model = " ".join(rest[1:]) if len(rest) > 1 else ""
    return {"make": make, "model": model, "year": year}


def _extract_specs_from_answer(answer: str) -> dict:
    """
    Try to pull Body Type and Color out of the long answer text the backend returns.
    These are mentioned as "* **Body Type:** Hatchback" etc.
    Returns empty strings if not found — the Result page handles missing gracefully.
    """
    specs = {"body_type": "", "color": ""}
    body_match = re.search(
        r"\*{0,2}body\s*type\*{0,2}[:\-]\s*([A-Za-z\s\-]+)",
        answer, re.IGNORECASE
    )
    if body_match:
        specs["body_type"] = body_match.group(1).strip().rstrip("*").strip()

    color_match = re.search(
        r"\*{0,2}color\*{0,2}[:\-]\s*([A-Za-z\s\-]+)",
        answer, re.IGNORECASE
    )
    if color_match:
        specs["color"] = color_match.group(1).strip().rstrip("*").strip()

    return specs


try:
    result = detect_vehicle(
        image_bytes=image_bytes,
        filename=image_name or "upload.jpg",
        content_type=image_type or "image/jpeg",
    )

    # ── Normalise the backend response ───────────────────────────────────
    # Backend returns: {"answer": "...", "vehicle_name": "FIAT_500_Abarth_2012",
    #                   "confidence": 1, "classification_confidence": 0.87, ...}
    # The Result page expects: make, model, year, body_type, color, confidence.
    if "vehicle_name" in result and "make" not in result:
        parsed = _parse_vehicle_name(result["vehicle_name"])
        result.update(parsed)

    if "answer" in result and (not result.get("body_type") or not result.get("color")):
        specs = _extract_specs_from_answer(result["answer"])
        if not result.get("body_type"):
            result["body_type"] = specs["body_type"]
        if not result.get("color"):
            result["color"] = specs["color"]

    # Normalise confidence to a 0–100 percentage.
    # Backend can return: 1 (sentinel for "use classification_confidence"),
    # a fraction like 0.87, or already a percentage like 87.0.
    raw_conf = result.get("confidence")
    class_conf = result.get("classification_confidence")

    if raw_conf is None:
        # No confidence at all → use classification_confidence if available
        result["confidence"] = round((class_conf or 0.0) * 100, 1)
    elif raw_conf == 1 and class_conf is not None:
        # Sentinel value — real confidence is in classification_confidence
        result["confidence"] = round(class_conf * 100, 1)
    elif isinstance(raw_conf, (int, float)) and raw_conf <= 1.0:
        # Fraction (0.0–1.0) → convert to percentage
        result["confidence"] = round(raw_conf * 100, 1)
    # else: already a percentage (e.g. 87.0) — leave as-is

except APIError as exc:
    st.warning(f"{t('backend_unavailable')} ({exc})")
    result = {
        "confidence": None,
        "make": "-",
        "model": "-",
        "year": "-",
        "body_type": "-",
        "color": "-",
        "answer": "",
        "vehicle_name": "-",
    }

set_detection(result)
status_box.empty()
progress.empty()
st.switch_page("pages/3_Result.py")