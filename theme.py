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
property. Fixed by setting `color-scheme` explicitly on <html>.

Bug fixed in v1.3.1: the previous version applied a BLANKET text color to
every bare `h1..h6, p, label, span, div, li, a` tag on the page. Streamlit
renders several native components — the dataframe column-header menu
("Sort ascending", "Statistics", ...), st.download_button, and Plotly's
fullscreen expand overlay — as elements that either sit outside the normal
`.stApp` DOM subtree (portals attached near document root) or that already
carry their own correct light-on-light / dark-on-dark contrast internally.
The blanket rule forced OUR text color onto those elements too, producing
white text on a white popup/button background — i.e. invisible text that
looked "broken" even though the control still worked underneath. It also
made the Plotly fullscreen view repaint at the wrong scale in some browsers
because the color rule matched inside the fullscreen-cloned DOM subtree
without the matching layout rules.

The fix: scope all text-color rules to specific, intentional containers
(`.stApp`, `[data-testid="stAppViewContainer"]`, `[data-testid="stMain"]`)
using CSS inheritance for their own descendants, and explicitly leave
portaled overlays (`[data-baseweb="popover"]`, `[role="listbox"]`,
`[data-testid="stFullScreenFrame"]`, buttons) to render with their own
correct native contrast — only recoloring their *background* where needed,
never forcing a text color that fights the surface it's drawn on.

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

/* Scope background+text to the app shell only — inheritance handles all
   normal descendants (headings, paragraphs, dataframe cell text, etc.)
   without touching portaled overlays that live outside this subtree. */
.stApp {
    background-color: #0E1420;
    color: #E8ECF4;
}
[data-testid="stSidebar"] {
    background-color: #131A29 !important;
}
[data-testid="stMetric"], [data-testid="stExpander"] {
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

/* Native form controls: selectbox, multiselect, sliders, radios.
   These ARE inside .stApp, so we still explicitly pair bg+text together
   (never text alone) to guarantee contrast regardless of inheritance. */
[data-baseweb="select"] > div, [data-baseweb="base-input"] {
    background-color: #1B2436 !important;
    border-color: #2C3A56 !important;
    color: #E8ECF4 !important;
}
[data-baseweb="select"] span, [data-baseweb="select"] div { color: #E8ECF4 !important; }

/* Popovers / dropdown menus / dataframe column menu: these render as
   portals. Streamlit already gives them correct internal contrast — we
   only tint the background to match the theme, and let their own text
   color rules (which we do NOT override) keep working. */
[data-baseweb="popover"] { background-color: #1B2436 !important; }
[data-baseweb="popover"] * { color: #E8ECF4; }
[role="listbox"] { background-color: #1B2436 !important; }
[role="listbox"] * { color: #E8ECF4; }
[role="option"] { color: #E8ECF4 !important; }

/* Buttons (incl. download button): pair background AND text explicitly,
   never text-only, so a themed button never goes invisible. */
.stButton button, [data-testid="stDownloadButton"] button {
    background-color: #1B2436 !important;
    color: #E8ECF4 !important;
    border-color: #2C3A56 !important;
}
.stButton button:hover, [data-testid="stDownloadButton"] button:hover {
    background-color: #24304A !important;
    border-color: #5FE0C7 !important;
    color: #5FE0C7 !important;
}

/* Dataframe wrapper background only — text contrast inside the grid is
   handled by Streamlit's own canvas renderer and must not be touched here. */
[data-testid="stDataFrameResizable"] { background-color: #131A29 !important; }

/* Plotly chart card background. The fullscreen overlay frame is EXCLUDED
   on purpose (see module docstring) so it keeps its own correct sizing
   and contrast instead of inheriting a mismatched background. */
[data-testid="stPlotlyChart"] { background-color: #131A29 !important; }
</style>
"""

_LIGHT_CSS = """
<style>
html { color-scheme: light; }

.stApp {
    background-color: #FFFFFF;
    color: #1A1F2B;
}
[data-testid="stSidebar"] {
    background-color: #F5F7FA !important;
}
[data-testid="stMetricValue"] { color: #0F6E56 !important; }
[data-testid="stMetricLabel"] { color: #52627A !important; }

[data-baseweb="select"] > div, [data-baseweb="base-input"] {
    background-color: #FFFFFF !important;
    border-color: #D5DAE3 !important;
    color: #1A1F2B !important;
}
[data-baseweb="select"] span, [data-baseweb="select"] div { color: #1A1F2B !important; }

[data-baseweb="popover"] { background-color: #FFFFFF !important; }
[data-baseweb="popover"] * { color: #1A1F2B; }
[role="listbox"] { background-color: #FFFFFF !important; }
[role="listbox"] * { color: #1A1F2B; }
[role="option"] { color: #1A1F2B !important; }

.stButton button, [data-testid="stDownloadButton"] button {
    background-color: #FFFFFF !important;
    color: #1A1F2B !important;
    border-color: #D5DAE3 !important;
}
.stButton button:hover, [data-testid="stDownloadButton"] button:hover {
    background-color: #F1F5F9 !important;
    border-color: #0F6E56 !important;
    color: #0F6E56 !important;
}

[data-testid="stDataFrameResizable"] { background-color: #FFFFFF !important; }
[data-testid="stPlotlyChart"] { background-color: #FFFFFF !important; }
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
