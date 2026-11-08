"""Look and layout for the Streamlit dashboard: palettes, scoped CSS, sidebar, top bar.

Nothing here touches the simulation, dataset, model or threshold code.
Rules used to keep the CSS from leaking onto unrelated widgets:
  * sidebar buttons are styled only under the sidebar container,
  * main-area buttons are styled only under the main container,
  * the top bar is styled only under its own keyed container.
"""

from datetime import datetime, timedelta, timezone
from html import escape

import pandas as pd
import streamlit as st

# Dubai is UTC+4 all year (no daylight saving), so a fixed offset is exact and needs no tz database.
DUBAI_TZ = timezone(timedelta(hours=4))
USER_INITIALS = "ZA"  # shown in the top-bar avatar; change to the project owner's initials

# Navigation groups: (group title, [page names]). Page names must match the branches in app.py.
NAV_GROUPS = [
    ("Overview", ["Study area", "Pipeline view"]),
    ("Data and models", ["Watering data", "Method comparison", "Live Diagnosis"]),
]
NAV_ICONS = {
    "Study area": "public",
    "Pipeline view": "account_tree",
    "Watering data": "water_drop",
    "Method comparison": "query_stats",
    "Live Diagnosis": "troubleshoot",
}

# Palette and layout adapted from the supplied irrigation-twin.css design system.
LIGHT = {
    "bg": "#f4f6fa", "surface": "#ffffff", "surface2": "#eef2f9", "border": "#e3e8f0",
    "border_strong": "#c9d2e0", "text": "#14213d", "muted": "#5b6678",
    "accent": "#1f4fbf", "accent_hover": "#1a43a3", "on_accent": "#ffffff",
    "accent_soft": "#e8effd", "accent2": "#0b7490", "control_bg": "#ffffff",
    "control_text": "#14213d", "control_border": "#e3e8f0", "control_hover": "#eef2f9",
    "side_bg": "#ffffff", "side_text": "#14213d", "side_muted": "#5b6678",
    "side_hover": "#eef2f9", "side_active": "#1f4fbf", "side_active_bg": "#e8effd",
    "side_active_text": "#1f4fbf", "side_border": "#e3e8f0",
    "leak": "#c23b4e", "clog": "#9a6a00", "ok": "#2f7a55",
    # matplotlib
    "plot_face": "#ffffff", "plot_text": "#14213d", "plot_muted": "#5b6678", "pipe": "#9aa9c0",
    "node": "#1f4fbf", "zone": "#0b7490", "source": "#5778bf", "fault": "#c23b4e",
    "ring": "#1f4fbf", "ring_fill": "#4cc3e0", "grid": "#e3e8f0",
    "chart_low": "#eef2f9", "chart_high": "#1f4fbf", "chart_cyan": "#0b7490",
}
DARK = {
    "bg": "#0f1626", "surface": "#172036", "surface2": "#1d2843", "border": "#27324d",
    "border_strong": "#38466a", "text": "#e8ecf5", "muted": "#9aa6bd",
    "accent": "#6b93ff", "accent_hover": "#86a6ff", "on_accent": "#0f1626",
    "accent_soft": "#1f2e57", "accent2": "#4cc3e0", "control_bg": "#172036",
    "control_text": "#e8ecf5", "control_border": "#38466a", "control_hover": "#1d2843",
    "side_bg": "#172036", "side_text": "#e8ecf5", "side_muted": "#9aa6bd",
    "side_hover": "#1d2843", "side_active": "#6b93ff", "side_active_bg": "#1f2e57",
    "side_active_text": "#e8ecf5", "side_border": "#27324d",
    "leak": "#ff7a8c", "clog": "#e5b04a", "ok": "#5fcf97",
    "plot_face": "#172036", "plot_text": "#e8ecf5", "plot_muted": "#9aa6bd", "pipe": "#455675",
    "node": "#6b93ff", "zone": "#4cc3e0", "source": "#9ab1ed", "fault": "#ff7a8c",
    "ring": "#6b93ff", "ring_fill": "#4cc3e0", "grid": "#27324d",
    "chart_low": "#1d2843", "chart_high": "#6b93ff", "chart_cyan": "#4cc3e0",
}


def is_dark() -> bool:
    return bool(st.session_state.get("dark_mode", False))


def tokens() -> dict:
    return DARK if is_dark() else LIGHT


# ---------------------------------------------------------------- CSS

_STATIC_CSS = """
/* Figtree follows the supplied design system; local system fonts remain the fallback. */
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
  font-family: Figtree, "Segoe UI", Arial, sans-serif;
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
.stApp { background: var(--bg); color: var(--text); }
[data-testid="stHeader"] { background: transparent; pointer-events: none; }
/* The transparent Streamlit toolbar otherwise sits over the top half of our custom header controls. */
[data-testid="stHeader"] button { pointer-events: auto; }
[data-testid="stHeader"] button, [data-testid="stHeader"] svg { color: var(--text); }
/* Hide Deploy / menu / footer only; the sidebar expand button lives in the toolbar and must stay */
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stAppDeployButton"], [data-testid="stMainMenu"], [data-testid="stStatusWidget"] { display: none; }
[data-testid="stExpandSidebarButton"] { color: var(--text); }
[data-testid="stMainBlockContainer"] { padding: 0 0 3.5rem; max-width: none; }

/* Text */
[data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3,
[data-testid="stMain"] p, [data-testid="stMain"] label, [data-testid="stMain"] li,
[data-testid="stMain"] [data-testid="stWidgetLabel"] p { color: var(--text); }
[data-testid="stMain"] h1 { font-weight: 700; letter-spacing: -0.035em; font-size: clamp(2rem, 2.7vw, 2.85rem); line-height: 1.15; }
[data-testid="stMain"] h2, [data-testid="stMain"] h3 { font-weight: 650; letter-spacing: -0.02em; line-height: 1.25; }
[data-testid="stMain"] p, [data-testid="stMain"] li { line-height: 1.55; }
[data-testid="stMain"] [data-testid="stCaptionContainer"] { opacity: 1; }
[data-testid="stMain"] [data-testid="stCaptionContainer"] p { color: var(--muted); }
[data-testid="stMain"] code { background: var(--surface2); color: var(--text); }

/* Polished select controls and option list (the list is rendered in a portal). */
[data-testid="stMain"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
  min-height: 42px; background: var(--control_bg); border: 1px solid var(--control_border) !important;
  border-radius: 10px; box-shadow: none; transition: border-color .15s ease, box-shadow .15s ease;
}
[data-testid="stMain"] [data-testid="stSelectbox"] [data-baseweb="select"] > div:hover { border-color: var(--accent2) !important; }
[data-testid="stMain"] [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
  border-color: var(--accent2) !important; box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent2) 18%, transparent);
}
[data-testid="stMain"] [data-testid="stSelectbox"] input,
[data-testid="stMain"] [data-testid="stSelectbox"] [role="combobox"] { color: var(--control_text); -webkit-text-fill-color: var(--control_text); }
[data-testid="stMain"] [data-testid="stSelectbox"] svg { fill: var(--accent2); color: var(--accent2); }
[data-testid="stSelectboxVirtualDropdown"] {
  background: var(--control_bg); border: 1px solid var(--control_border); border-radius: 11px;
  padding: 5px; box-shadow: 0 12px 30px rgba(15, 25, 20, .16);
}
[data-testid="stSelectboxVirtualDropdown"] [role="option"] {
  color: var(--control_text); border-radius: 7px; min-height: 36px; margin: 2px 0; transition: background .12s ease;
}
[data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover,
[data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"] { background: var(--control_hover); }

/* Metrics and notices become cards */
[data-testid="stMain"] [data-testid="stMetric"] {
  background: var(--surface); border: 1px solid var(--border); border-radius: 13px; padding: .9rem 1.1rem;
  box-shadow: 0 5px 18px rgba(20, 35, 55, .045); transition: transform .18s ease, box-shadow .18s ease;
}
[data-testid="stMain"] [data-testid="stMetric"]:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(20, 35, 55, .09); }
[data-testid="stMain"] [data-testid="stMetricLabel"] p { color: var(--muted); font-weight: 600; }
[data-testid="stMain"] [data-testid="stMetricValue"] { color: var(--text); font-weight: 800; }
[data-testid="stMain"] [data-testid="stAlert"] {
  background: var(--surface); border: 1px solid var(--border); border-left: 4px solid var(--accent);
  border-radius: 10px; color: var(--text);
}
[data-testid="stMain"] [data-testid="stAlertContainer"] { background: transparent; }
[data-testid="stMain"] [data-testid="stAlert"] p, [data-testid="stMain"] [data-testid="stAlert"] svg { color: var(--text); fill: var(--text); }

/* Main-area action buttons only (Run Diagnosis, Download CSV); the sidebar is styled separately */
[data-testid="stMain"] [data-testid="stBaseButton-secondary"] {
  background: var(--accent); color: var(--on_accent); border: 0; border-radius: 9px; font-weight: 650;
  min-height: 40px; transition: transform .12s ease, filter .12s ease;
}
[data-testid="stMain"] [data-testid="stBaseButton-secondary"] p { color: var(--on_accent); }
[data-testid="stMain"] [data-testid="stBaseButton-secondary"]:hover { background: var(--accent_hover); filter: none; transform: translateY(-1px); }

/* Themed HTML tables (st.dataframe cannot follow a runtime dark-mode switch) */
.tbl-wrap { overflow: auto; border: 1px solid var(--border); border-radius: 12px; background: var(--surface); margin-bottom: .6rem; }
table.tbl { width: 100%; border-collapse: collapse; font-size: .85rem; color: var(--text); }
table.tbl th {
  position: sticky; top: 0; background: var(--surface2); color: var(--muted); text-align: left;
  font-weight: 700; padding: .5rem .75rem; border-bottom: 1px solid var(--border); white-space: nowrap;
}
table.tbl td { padding: .42rem .75rem; border-bottom: 1px solid var(--border); white-space: nowrap; }
table.tbl tr:last-child td { border-bottom: 0; }
table.tbl tbody tr:hover td { background: var(--surface2); }

/* Matplotlib figures sit on a card */
[data-testid="stMain"] [data-testid="stImage"] img { border-radius: 12px; border: 1px solid var(--border); }

/* ---------------- Sidebar ---------------- */
[data-testid="stSidebar"] { background: var(--side_bg); border-right: 1px solid var(--side_border); }
[data-testid="stSidebar"] { min-width: 300px !important; max-width: 300px !important; }
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
  height: 2.35rem !important; min-height: 2.35rem !important; padding: 0 .65rem !important;
  margin: 0 !important; background: transparent;
}
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button { height: 2rem; width: 2rem; }
[data-testid="stSidebarUserContent"] { padding-top: 0 !important; }
[data-testid="stSidebar"] button[kind="headerNoPadding"] svg, [data-testid="stSidebarCollapseButton"] svg { color: var(--side_muted); }
[data-testid="stSidebarContent"] { padding: 0 1.1rem 1.25rem !important; }
.brand { display: flex; gap: .85rem; align-items: center; padding: .4rem .3rem 1.1rem; margin-top: 0; }
.brand .mark {
  width: 44px; height: 44px; border-radius: 12px; background: var(--side_active);
  display: flex; align-items: center; justify-content: center; flex: 0 0 auto;
}
.brand .name { color: var(--side_text); font-weight: 700; font-size: 1.22rem; letter-spacing: -.01em; line-height: 1.15; }
.brand .sub { color: var(--side_muted); font-size: .84rem; }
.nav-group { color: var(--side_muted); font-size: .78rem; font-weight: 650; letter-spacing: .08em; text-transform: uppercase; padding: 1.05rem .4rem .4rem; }

/* Left-align the label inside every nav button (Streamlit centres its inner wrappers) */
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] > div,
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] > div,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] [data-testid="stMarkdownContainer"] {
  width: 100%; justify-content: flex-start; text-align: left;
}

/* Inactive navigation item */
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
  background: transparent; border: 0; border-left: 3px solid transparent; border-radius: 8px;
  justify-content: flex-start; padding: .7rem .85rem; width: 100%; min-height: 44px; box-shadow: none;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] p { color: var(--side_muted); font-weight: 500; text-align: left; }
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover { background: var(--side_hover); }
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover p { color: var(--side_text); }
/* Active navigation item */
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
  background: var(--side_active_bg); border: 0; border-left: 3px solid var(--side_active); border-radius: 8px;
  justify-content: flex-start; padding: .7rem .85rem; width: 100%; min-height: 44px; box-shadow: none;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] p { color: var(--side_active_text); font-weight: 700; text-align: left; }
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:focus-visible,
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:focus-visible { outline: 2px solid var(--side_active); outline-offset: 1px; }
[data-testid="stSidebar"] [data-testid="stButton"] { margin-bottom: -.35rem; }
.side-foot { color: var(--side_muted); font-size: .76rem; line-height: 1.45; padding: 1.4rem .4rem 0; }

/* ---------------- Top bar ---------------- */
.st-key-topbar {
  position: sticky; top: 0; z-index: 1000;
  width: 100%; max-width: none; margin: 0 0 1.35rem;
  background: var(--bg); border: 0; border-bottom: 1px solid var(--border); border-radius: 0;
  min-height: 80px; padding: 0 40px; box-shadow: none;
}
.st-key-topbar [data-testid="stHorizontalBlock"] {
  display: flex !important; flex-wrap: nowrap; width: 100%; min-height: 78px;
  align-items: center; gap: .7rem;
}
.st-key-topbar [data-testid="stColumn"] {
  min-width: 0 !important;
}
.st-key-topbar [data-testid="stColumn"]:nth-child(1) { flex: 1 1 0% !important; width: auto !important; }
.st-key-topbar [data-testid="stColumn"]:nth-child(2) { flex: 0 1 max-content !important; width: auto !important; }
.st-key-topbar [data-testid="stColumn"]:nth-child(3) { flex: 0 0 168px !important; width: 168px !important; }
.st-key-topbar [data-testid="stColumn"]:nth-child(4),
.st-key-topbar [data-testid="stColumn"]:nth-child(5) { flex: 0 0 44px !important; width: 44px !important; }
.st-key-topbar [data-testid="stColumn"] > div { min-width: 0; }
.st-key-topbar .breadcrumb { overflow: hidden; text-overflow: ellipsis; }
.st-key-topbar .clock { overflow: visible; }
.st-key-topbar [data-testid="stBaseButton-secondary"] {
  display: flex; box-sizing: border-box; width: 100%; min-width: 0; height: 40px; min-height: 40px;
  padding: 0 .85rem; align-items: center; justify-content: center; position: relative; z-index: 1;
  background: var(--surface) !important;
  color: var(--text) !important; border: 1px solid var(--border) !important; border-radius: 999px !important;
  box-shadow: none !important; font-size: .82rem; font-weight: 650; white-space: nowrap;
  transition: background .15s ease, border-color .15s ease;
}
.st-key-topbar [data-testid="stBaseButton-secondary"]:hover {
  background: var(--surface2) !important; border-color: var(--accent2) !important;
  transform: none !important; filter: none !important;
}
.st-key-topbar [data-testid="stBaseButton-secondary"] p { color: var(--text) !important; }
.st-key-topbar .st-key-notification_toggle [data-testid="stBaseButton-secondary"] {
  height: 40px; min-height: 40px; min-width: 42px; width: 42px; padding: 0 !important; margin-inline: auto;
  background: var(--surface) !important; color: var(--text) !important;
  border: 1px solid var(--border) !important; border-radius: 12px !important; position: relative;
}
.st-key-topbar .st-key-notification_toggle [data-testid="stBaseButton-secondary"] p {
  font-size: 0; margin: 0; width: 0; overflow: hidden;
}
.st-key-topbar .st-key-notification_toggle [data-testid="stBaseButton-secondary"] svg { color: var(--text); fill: none; }
.st-key-topbar .st-key-notification_toggle [data-testid="stBaseButton-secondary"]:hover {
  background: var(--surface2) !important; border-color: var(--accent2) !important;
}
.st-key-topbar .st-key-notification_toggle [data-testid="stBaseButton-secondary"][aria-label="New notifications"]::after {
  content: ""; position: absolute; top: 7px; right: 7px; width: 7px; height: 7px;
  border-radius: 50%; background: var(--accent2); box-shadow: 0 0 0 2px var(--surface);
}
.breadcrumb { color: var(--muted); font-size: .82rem; white-space: nowrap; }
.breadcrumb strong { color: var(--text); font-weight: 600; }
.clock { line-height: 1.2; text-align: right; white-space: nowrap; }
.clock .context { color: var(--accent2); font-size: .62rem; font-weight: 750; letter-spacing: .1em; text-transform: uppercase; margin-bottom: .28rem; }
.clock .context::before { content: ""; display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--accent2); margin: 0 .42rem .02rem 0; }
.clock .time { color: var(--muted); font-weight: 500; font-size: .78rem; }
.clock .d-short { display: none; }
.top-icons { display: flex; align-items: center; gap: .6rem; justify-content: flex-end; }
.icon-btn {
  width: 38px; height: 38px; border-radius: 11px; border: 1px solid var(--border); background: var(--surface2);
  display: flex; align-items: center; justify-content: center; color: var(--text); position: relative;
}
.avatar {
  width: 40px; height: 40px; border-radius: 50%; background: var(--accent); color: var(--on_accent);
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .8rem;
}
.notification-heading { color: var(--text); font-size: 1rem; font-weight: 700; margin: 0 0 .2rem; }
.notification-subtitle { color: var(--muted); font-size: .78rem; margin-bottom: .75rem; }
.notification-item {
  display: grid; grid-template-columns: 8px 1fr; gap: .65rem; padding: .7rem .65rem;
  margin: .4rem 0; background: var(--surface2); border: 1px solid var(--border); border-radius: 10px;
  animation: noticeIn .25s ease both;
}
.notification-dot { width: 7px; height: 7px; margin-top: .35rem; border-radius: 50%; background: var(--accent2); }
.notification-dot.alert { background: var(--leak); }
.notification-title { color: var(--text); font-size: .84rem; font-weight: 650; }
.notification-detail { color: var(--muted); font-size: .78rem; line-height: 1.45; margin-top: .15rem; }
.notification-time { color: var(--muted); font-size: .7rem; margin-top: .25rem; }
.st-key-notification-panel {
  padding: .9rem 1rem; margin: -.75rem 0 1rem; border: 1px solid var(--border); border-radius: 14px;
  background: var(--surface); box-shadow: 0 14px 32px rgba(15, 25, 40, .14); animation: noticeIn .2s ease both;
}
.st-key-notification-panel .notification-heading { padding-top: .4rem; }
.workspace-eyebrow { color: var(--accent2); text-transform: uppercase; letter-spacing: .13em; font-size: .7rem; font-weight: 750; margin: .25rem 0 .2rem; }
.st-key-results-panel, .st-key-diagnosis-results { animation: panelIn .38s ease both; }
.st-key-diagnosis-results [data-testid="stMetric"] { padding: .7rem .9rem; }
.st-key-diagnosis-results [data-testid="stMetricValue"] { font-size: 1.35rem; }
.st-key-diagnosis-results [data-testid="stMetricLabel"] p { font-size: .78rem; }
.st-key-rf-diagnosis-card, .st-key-threshold-diagnosis-card {
  padding: .85rem 1rem; border: 1px solid var(--border); border-radius: 15px;
  background: var(--surface); height: 100%;
}
.st-key-rf-diagnosis-card { border-top: 3px solid var(--chart_high); box-shadow: 0 8px 24px rgba(20, 45, 80, .08); }
.st-key-threshold-diagnosis-card { opacity: .88; }
.chart-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: .55rem; }
@keyframes panelIn { from { opacity: 0; transform: translateY(9px); } to { opacity: 1; transform: translateY(0); } }
@keyframes pageEnter { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes noticeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
[class*="st-key-page-content-"] {
  width: calc(100% - 80px); max-width: 1500px; margin-inline: auto;
  animation: pageEnter .28s cubic-bezier(.2,.7,.2,1) both;
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
}

@media (max-width: 640px) {
  [data-testid="stSidebar"] { min-width: min(300px, 86vw) !important; max-width: min(300px, 86vw) !important; }
  [data-testid="stMainBlockContainer"] { padding-left: 0; padding-right: 0; }
  .st-key-topbar { min-height: 64px; padding: 0 .75rem; }
  .st-key-topbar [data-testid="stHorizontalBlock"] { min-height: 62px; }
  [class*="st-key-page-content-"] { width: calc(100% - 2rem); }
  .st-key-topbar [data-testid="stHorizontalBlock"] {
    gap: .4rem;
  }
  .st-key-topbar [data-testid="stColumn"]:nth-child(2) { display: none; }
  .st-key-topbar [data-testid="stColumn"]:nth-child(3) { flex-basis: 138px !important; width: 138px !important; }
  .st-key-topbar [data-testid="stColumn"]:nth-child(4),
  .st-key-topbar [data-testid="stColumn"]:nth-child(5) { flex-basis: 40px !important; width: 40px !important; }
  .st-key-topbar [data-testid="stBaseButton-secondary"] { padding-inline: .45rem; font-size: .74rem; }
  [data-testid="stMain"] h1 { font-size: 1.5rem; }
}

@media (min-width: 641px) and (max-width: 900px) {
  [data-testid="stSidebar"] { min-width: 270px !important; max-width: 270px !important; }
  .st-key-topbar { min-height: 72px; padding-inline: 1rem; }
  .st-key-topbar [data-testid="stHorizontalBlock"] { min-height: 70px; }
  .st-key-topbar [data-testid="stHorizontalBlock"] { gap: .45rem; }
  .st-key-topbar [data-testid="stColumn"]:nth-child(2) { display: none; }
  .st-key-topbar [data-testid="stColumn"]:nth-child(3) { flex-basis: 148px !important; width: 148px !important; }
  .st-key-topbar [data-testid="stColumn"]:nth-child(4),
  .st-key-topbar [data-testid="stColumn"]:nth-child(5) { flex-basis: 42px !important; width: 42px !important; }
  .st-key-topbar [data-testid="stBaseButton-secondary"] { padding-inline: .55rem; font-size: .76rem; }
}
"""


def inject_css() -> None:
    t = tokens()
    variables = ";".join(f"--{k}:{v}" for k, v in t.items() if not k.startswith("plot_"))
    st.markdown(
        '<style>@import url("https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&display=swap");'
        f":root{{{variables}}}{_STATIC_CSS}</style>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------- Components

_DROP_ICON = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"><path d="M12 3s6 6.2 6 10.5a6 6 0 0 1-12 0C6 9.2 12 3 12 3z"/></svg>'
)
def sidebar_nav(default: str) -> str:
    """Brand + grouped navigation in the sidebar. Returns the selected page name."""
    st.session_state.setdefault("page", default)

    def go(page: str) -> None:
        st.session_state["page"] = page

    with st.sidebar:
        st.markdown(
            f'<div class="brand"><div class="mark">{_DROP_ICON.format(c=tokens()["on_accent"])}</div>'
            '<div><div class="name">Irrigation Twin</div><div class="sub">Fault diagnosis prototype</div></div></div>',
            unsafe_allow_html=True,
        )
        for group, pages in NAV_GROUPS:
            st.markdown(f'<div class="nav-group">{escape(group)}</div>', unsafe_allow_html=True)
            for page in pages:
                active = st.session_state["page"] == page
                st.button(
                    f":material/{NAV_ICONS.get(page, 'circle')}: {page}", key=f"nav_{page}", type="primary" if active else "secondary",
                    use_container_width=True, on_click=go, args=(page,),
                )
        st.markdown(
            '<div class="side-foot">Simulation prototype. All networks and readings are synthetic.</div>',
            unsafe_allow_html=True,
        )
    return st.session_state["page"]


def add_notification(title: str, detail: str, kind: str = "info") -> None:
    """Add a real in-app notification to the current Streamlit session."""
    items = list(st.session_state.get("notifications", []))
    items.insert(
        0,
        {
            "title": title,
            "detail": detail,
            "kind": "alert" if kind == "alert" else "info",
            "time": datetime.now(DUBAI_TZ).strftime("%H:%M GST"),
        },
    )
    st.session_state["notifications"] = items[:6]


def top_bar(page: str = "Overview") -> None:
    """Workspace breadcrumb, Dubai timestamp, theme action, notifications and initials."""
    now = datetime.now(DUBAI_TZ)
    st.session_state.setdefault("notifications_open", False)
    with st.container(key="topbar"):
        breadcrumb, clock, theme_column, alert_column, avatar_column = st.columns([4.6, 2.4, 1.65, .65, .48], gap="small")
        breadcrumb.markdown(
            f'<div class="breadcrumb">Workspace&nbsp; / &nbsp;<strong>{escape(page)}</strong></div>',
            unsafe_allow_html=True,
        )
        clock.markdown(
            f'<div class="clock"><div class="context">Simulated network · 3 zones</div>'
            f'<div class="time">{now:%A} {now.day} {now:%b}, {now:%H:%M} · Dubai</div></div>',
            unsafe_allow_html=True,
        )
        is_currently_dark = is_dark()
        mode_label = "Light mode" if is_currently_dark else "Dark mode"
        mode_icon = "light_mode" if is_currently_dark else "dark_mode"
        if theme_column.button(
            f":material/{mode_icon}: {mode_label}",
            key="theme_action_button",
            type="secondary",
            use_container_width=True,
        ):
            st.session_state["dark_mode"] = not is_currently_dark
            st.rerun()
        items = st.session_state.get("notifications", [])
        alert_label = "New notifications" if items else "Notifications"
        if alert_column.button(
            alert_label, key="notification_toggle", type="secondary",
            icon=":material/notifications:", help="Show recent diagnosis notifications",
            use_container_width=True,
        ):
            st.session_state["notifications_open"] = not st.session_state["notifications_open"]
            st.rerun()
        avatar_column.markdown(
            f'<div class="avatar" role="img" aria-label="Project initials">{escape(USER_INITIALS)}</div>',
            unsafe_allow_html=True,
        )

    if st.session_state["notifications_open"]:
        left, panel_column = st.columns([4.4, 2.6], gap="small")
        with panel_column:
            with st.container(key="notification-panel"):
                items = st.session_state.get("notifications", [])
                panel_title, close_column = st.columns([4, 1])
                panel_title.markdown('<div class="notification-heading">Notifications</div>', unsafe_allow_html=True)
                if close_column.button("Close", key="close_notifications", type="secondary", help="Close notifications"):
                    st.session_state["notifications_open"] = False
                    st.rerun()
                st.markdown('<div class="notification-subtitle">Recent activity in this session</div>', unsafe_allow_html=True)
                if not items:
                    st.caption("No diagnosis alerts yet. Run a scenario to see updates here.")
                else:
                    for item in items:
                        kind = "alert" if item.get("kind") == "alert" else ""
                        st.markdown(
                            '<div class="notification-item">'
                            f'<span class="notification-dot {kind}"></span><div>'
                            f'<div class="notification-title">{escape(item.get("title", "Update"))}</div>'
                            f'<div class="notification-detail">{escape(item.get("detail", ""))}</div>'
                            f'<div class="notification-time">{escape(item.get("time", ""))}</div></div></div>',
                            unsafe_allow_html=True,
                        )
                    if st.button("Clear notifications", key="clear_notifications", type="secondary", use_container_width=True):
                        st.session_state["notifications"] = []
                        st.rerun()


def show_table(df: pd.DataFrame, use_container_width: bool = True, hide_index: bool = False, height: int | None = None) -> None:
    """Theme-aware replacement for st.dataframe (same arguments the app already used)."""
    html = df.to_html(index=not hide_index, classes="tbl", border=0, escape=True)
    style = f' style="max-height:{height}px"' if height else ""
    st.markdown(f'<div class="tbl-wrap"{style}>{html}</div>', unsafe_allow_html=True)
