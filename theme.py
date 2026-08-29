"""
Light/Dark theme module for MPGM.

Streamlit's built-in theme switcher (hamburger menu -> Settings -> Theme)
exists, but it cannot be read from Python at runtime in a version-stable way,
so it can't drive Plotly's color template. This module implements our own
explicit, session-controlled toggle instead: it drives (a) injected CSS that
recolors Streamlit's own chrome, and (b) the Plotly template used by every
chart in the app, so both stay in sync with a single source of truth
(`st.session_state["theme"]`).

Bug fixed in v1.1.1: the browser applies its own native dark styling to
form controls (dropdowns, etc.) based on the page's `color-scheme` CSS
property. Streamlit sets this from the OS/browser preference by default, so
on a system with dark mode enabled, native widget chrome (like the selectbox
pill) stayed dark even when our own CSS painted the page background light,
producing a mismatched, partially-broken look with washed-out text. Fixing
`color-scheme` explicitly on <html> keeps native controls in sync with the
chosen theme, not the OS.

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
html { color-scheme: dark; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
[data-testid="stMain"], [data-testid="stBottomBlockContainer"] {
    background-color: #0E1420 !important;
    color: #E8ECF4 !important;
}
[data-testid="stSidebar"] {
    background-color: #131A29 !important;
}
h1, h2, h3, h4, h5, h6, p, label, span, div, li, a {
    color: #E8ECF4;
}
[data-testid="stMetric"], [data-testid="stExpander"], .stDataFrame, .stTabs {
    background-color: #131A29 !important;
    border-radius: 8px;
}
[data-testid="stMetricValue"] { color: #6FD6C8 !important; }
[data-testid="stMetricLabel"] { color: #B7C0D1 !important; }
.stTabs [data-baseweb="tab"] { color: #B7C0D1; }
.stTabs [aria-selected="true"] { color: #6FD6C8 !important; }
[data-testid="stExpander"] summary { color: #E8ECF4 !important; }
hr { border-color: #24304A !important; }
code { background-color: #1B2436 !important; color: #6FD6C8 !important; }

/* Native form controls: selectbox, multiselect, sliders, radios */
[data-baseweb="select"] > div, [data-baseweb="base-input"] {
    background-color: #1B2436 !important;
    border-color: #2C3A56 !important;
    color: #E8ECF4 !important;
}
[data-baseweb="select"] span, [data-baseweb="select"] div { color: #E8ECF4 !important; }
[data-baseweb="popover"] { background-color: #1B2436 !important; }
[role="listbox"] { background-color: #1B2436 !important; color: #E8ECF4 !important; }
[role="option"] { color: #E8ECF4 !important; }

/* Dataframe / table cells */
[data-testid="stDataFrameResizable"], .glideDataEditor { background-color: #131A29 !important; }

/* Plotly chart container background so it matches the surrounding card */
.js-plotly-plot .plotly, [data-testid="stPlotlyChart"] { background-color: #131A29 !important; }
</style>
"""

_LIGHT_CSS = """
<style>
html { color-scheme: light; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
[data-testid="stMain"], [data-testid="stBottomBlockContainer"] {
    background-color: #FFFFFF !important;
    color: #1A1F2B !important;
}
[data-testid="stSidebar"] {
    background-color: #F5F7FA !important;
}
h1, h2, h3, h4, h5, h6, p, label, span, div, li, a {
    color: #1A1F2B;
}
[data-testid="stMetricValue"] { color: #0F6E56 !important; }
[data-testid="stMetricLabel"] { color: #52627A !important; }

/* Native form controls: keep them light even if the OS prefers dark */
[data-baseweb="select"] > div, [data-baseweb="base-input"] {
    background-color: #FFFFFF !important;
    border-color: #D5DAE3 !important;
    color: #1A1F2B !important;
}
[data-baseweb="select"] span, [data-baseweb="select"] div { color: #1A1F2B !important; }
[data-baseweb="popover"] { background-color: #FFFFFF !important; }
[role="listbox"] { background-color: #FFFFFF !important; color: #1A1F2B !important; }
[role="option"] { color: #1A1F2B !important; }

.js-plotly-plot .plotly, [data-testid="stPlotlyChart"] { background-color: #FFFFFF !important; }
</style>
"""


def init_theme():
    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"


def apply_theme(theme: str):
    st.markdown(_DARK_CSS if theme == "dark" else _LIGHT_CSS, unsafe_allow_html=True)


def plotly_template(theme: str) -> str:
    return PLOTLY_TEMPLATES.get(theme, "plotly_white")


THEME_LABELS = {
    "en": {"light": "☀️ Light", "dark": "🌙 Dark", "toggle_label": "Theme"},
    "tr": {"light": "☀️ Açık", "dark": "🌙 Koyu", "toggle_label": "Tema"},
}
