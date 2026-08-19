"""Styled drag-and-drop upload zone.

st.file_uploader() renders as a real, independent widget (its own
element-container), so it can't be nested inside a hand-written <div> the
way a single mockup box suggests — see the long comment at the top of
components/navigation.py for why that never actually nests in Streamlit.

Instead we render two adjacent pieces and style them from the outside so
they *read* as one seamless box:
  1. `.vv-upload-zone-top` — our own markup: icon, title, subtitle.
  2. the real file_uploader dropzone right below it, restyled via the
     `.vv-upload-zone-marker` + adjacent-sibling CSS trick (same pattern
     the navbar uses in components/navigation.py) so its border continues
     the one above it and Streamlit's own "Drag and drop file here" copy
     is hidden (we already say that above) in favor of a real "Browse
     Files" button styled to match.
"""

import streamlit as st
from utils.i18n import t


def render_upload_zone():
    st.markdown(
        f"""
        <div class="vv-upload-zone-top">
            <div class="vv-upload-icon">⬆️</div>
            <p class="vv-upload-title">{t('upload_title')}</p>
            <p class="vv-text-secondary vv-upload-subtitle">{t('upload_subtitle')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # This marker must sit immediately before file_uploader() — nothing
    # else in between — so the CSS sibling selector targets only this
    # uploader's dropzone (see assets/css/theme.css).
    st.markdown('<span class="vv-upload-zone-marker"></span>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        label="Upload vehicle image",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )

    st.markdown(
        f"""
        <div class="vv-upload-legend">
            <span>⬆ <strong>{t('upload_label')}</strong> &middot; {t('upload_legend_formats')}</span>
            <span>{t('upload_legend_max_size')}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return uploaded