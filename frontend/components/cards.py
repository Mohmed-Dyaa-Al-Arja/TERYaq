"""Shared presentation cards."""

import html
import streamlit as st

ICON_SVG = {
    "scan": '<path d="M4 9V5a1 1 0 0 1 1-1h4M20 9V5a1 1 0 0 0-1-1h-4M4 15v4a1 1 0 0 0 1 1h4M20 15v4a1 1 0 0 1-1 1h-4"/><circle cx="12" cy="12" r="3"/>',
    "chip": '<rect x="7" y="7" width="10" height="10" rx="2"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
    "chart": '<path d="M4 19V5M4 19h17"/><path d="m7 15 3-4 3 2 5-7"/>',
    "shield": '<path d="M12 3 20 6v5c0 5-3.2 8.2-8 10-4.8-1.8-8-5-8-10V6z"/><path d="m8.5 12 2.2 2.2 4.8-5"/>',
    "headset": '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><path d="M4 14h3v5H5a1 1 0 0 1-1-1zM20 14h-3v5h2a1 1 0 0 0 1-1z"/><path d="M17 19c0 2-2 3-5 3"/>',
    "users": '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><path d="M16 5.5a3 3 0 0 1 0 5.8M18 14c2.3.8 3.8 2.8 4 5"/>',
    "image": '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8.5" cy="9" r="1.5"/><path d="m21 15-5-5-7 8"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3 2"/>',
}


def icon_svg(name: str) -> str:
    body = ICON_SVG.get(name, ICON_SVG["scan"])
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{body}</svg>'


def stat_card(value: str, label: str, icon: str = "users") -> None:
    st.markdown(
        f'<div class="vv-stat-card"><div class="vv-stat-icon">{icon_svg(icon)}</div>'
        f'<div class="vv-stat-content"><div class="vv-stat-value">{html.escape(value)}</div>'
        f'<div class="vv-stat-label">{html.escape(label)}</div></div></div>',
        unsafe_allow_html=True,
    )


def feature_card(title: str, description: str, icon: str = "scan") -> None:
    st.markdown(
        f'<div class="vv-feature-card"><div class="vv-feature-icon">{icon_svg(icon)}</div>'
        f'<h4>{html.escape(title)}</h4><p>{html.escape(description)}</p></div>',
        unsafe_allow_html=True,
    )


def confidence_badge(score: float) -> str:
    if score >= 60:
        cls = "vv-badge-success"
    elif score >= 30:
        cls = "vv-badge-warning"
    else:
        cls = "vv-badge-danger"
    return f'<span class="vv-badge {cls}">{score:.1f}% Confidence</span>'


def source_card(name: str, url: str, updated: str, reliability: str) -> None:
    st.markdown(
        f'<div class="vv-card-flat"><strong>{html.escape(name)}</strong>'
        f'<span>{html.escape(url)}</span><b>{html.escape(reliability)}</b>'
        f'<small>Updated {html.escape(updated)}</small></div>',
        unsafe_allow_html=True,
    )
