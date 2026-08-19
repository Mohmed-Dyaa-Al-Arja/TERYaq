"""
Theme utilities.

Handles loading the shared CSS file and switching between light and dark
mode by writing a `data-theme` attribute onto the real page <html> element.

IMPORTANT: `st.markdown(..., unsafe_allow_html=True)` renders through
`innerHTML`, and browsers never execute <script> tags inserted that way.
So any JS that needs to actually *run* (theme attribute, RTL direction,
navbar scroll behaviour) must go through `st.components.v1.html`, which
renders in a real (same-origin) iframe whose scripts do execute and which
can safely reach up to `window.parent.document`.
"""

from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

CSS_DIR = Path(__file__).resolve().parent.parent / "assets" / "css"
GLOBAL_CSS_PATH = CSS_DIR / "global.css"


def init_theme() -> None:
    """Make sure `theme` exists in session_state. Call once at app start."""
    if "theme" not in st.session_state:
        st.session_state.theme = "light"


def toggle_theme() -> None:
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"


def load_css(page_css: str | None = None) -> None:
    """Load shared CSS plus the stylesheet for the current page. Page styles are intentionally loaded after global styles so the original cascade is preserved."""
    css_parts = [GLOBAL_CSS_PATH.read_text(encoding="utf-8")]

    if page_css:
        page_path = CSS_DIR / f"{page_css}.css"
        if page_path.exists():
            css_parts.append(page_path.read_text(encoding="utf-8"))

    css = "\n\n".join(css_parts)
    theme = st.session_state.get("theme", "light")
    lang = st.session_state.get("lang", "en")
    direction = "rtl" if lang == "ar" else "ltr"

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    # Marker element that theme.css's RTL "safe patch" rules key off of
    # (`.stApp:has(.vv-rtl-marker) ...`). Without this, those RTL-specific
    # overrides (hero layout, assistant card layout, etc.) never match, and
    # the browser's own automatic flex-direction reversal under dir="rtl"
    # ends up flipping the already-swapped Python columns a second time.
    if lang == "ar":
        st.markdown('<span class="vv-rtl-marker"></span>', unsafe_allow_html=True)

    # This tiny iframe's script is what actually executes in the browser.
    components.html(
        f"""
        <script>
            (function() {{
                const doc = window.parent.document;
                doc.documentElement.setAttribute('data-theme', '{theme}');
                doc.documentElement.setAttribute('dir', '{direction}');
                doc.documentElement.setAttribute('lang', '{lang}');
                doc.body.setAttribute('data-theme', '{theme}');
                doc.body.setAttribute('dir', '{direction}');
            }})();
        </script>
        """,
        height=0,
        width=0,
    )