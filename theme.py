"""
Light/Dark theme module for MPGM.

Streamlit's built-in theme switcher (hamburger menu -> Settings -> Theme)
exists, but it cannot be read from Python at runtime in a version-stable way,
so it can't drive Plotly's color template. This module implements our own
explicit, session-controlled toggle instead: it drives (a) injected CSS that
recolors Streamlit's own chrome, and (b) the Plotly template used by every
chart in the app, so both stay in sync with a single source of truth
(`st.session_state["theme"]`).

Known trade-off: on first paint, before this CSS is injected, the browser
briefly shows Streamlit's default chrome color. This is a limitation of
overriding the theme at runtime from within the app rather than at server
config time (`.streamlit/config.toml`, which is static and can't offer a
user-facing toggle). It corrects itself within a frame and does not recur
on reruns within the same session.
"""

import streamlit as st

PLOTLY_TEMPLATES = {"light": "plotly_white", "dark": "plotly_dark"}

_DARK_CSS = """
<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #0E1420 !important;
    color: #E8ECF4 !important;
}
[data-testid="stSidebar"] {
    background-color: #131A29 !important;
}
h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: #E8ECF4;
}
[data-testid="stMetric"], [data-testid="stExpander"], .stDataFrame, .stTabs {
    background-color: #131A29 !important;
    border-radius: 8px;
}
[data-testid="stMetricValue"] { color: #6FD6C8 !important; }
.stTabs [data-baseweb="tab"] { color: #B7C0D1; }
.stTabs [aria-selected="true"] { color: #6FD6C8 !important; }
[data-testid="stExpander"] summary { color: #E8ECF4 !important; }
hr { border-color: #24304A !important; }
code { background-color: #1B2436 !important; color: #6FD6C8 !important; }
</style>
"""

_LIGHT_CSS = """
<style>
/* Explicit light overrides so the toggle is symmetric even if the browser
   is set to prefer dark mode at the OS level. */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #FFFFFF !important;
    color: #1A1F2B !important;
}
[data-testid="stSidebar"] {
    background-color: #F5F7FA !important;
}
</style>
"""


def init_theme():
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"


def apply_theme(theme: str):
    st.markdown(_DARK_CSS if theme == "dark" else _LIGHT_CSS, unsafe_allow_html=True)


def plotly_template(theme: str) -> str:
    return PLOTLY_TEMPLATES.get(theme, "plotly_white")


THEME_LABELS = {
    "en": {"light": "☀️ Light", "dark": "🌙 Dark", "toggle_label": "Theme"},
    "tr": {"light": "☀️ Açık", "dark": "🌙 Koyu", "toggle_label": "Tema"},
}
