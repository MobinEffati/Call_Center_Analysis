import html
import inspect
import math
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


# ==================================================
# Page Configuration
# ==================================================

st.set_page_config(
    page_title="داشبورد تحلیل مرکز تماس",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# Design Tokens
# ==================================================

INK = "#1f2a44"
MUTED = "#6b7690"
LINE = "#e6eaf2"
FONT_STACK = "Vazirmatn, Tahoma, 'Segoe UI', sans-serif"

CAL_JALALI = "شمسی"
CAL_GREGORIAN = "میلادی"

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap');
:root { --ink:#1f2a44; --muted:#6b7690; --line:#e6eaf2; --card:#ffffff; --bg:#f4f6fb; --primary:#2563eb; }
html, body, .stApp, .stApp :is(p, span, div, label, button, input, textarea, li, a, h1, h2, h3, h4, h5, h6, th, td) { font-family: 'Vazirmatn', Tahoma, 'Segoe UI', sans-serif !important; }
.stApp span[data-testid="stIconMaterial"], .stApp .material-symbols-rounded { font-family: 'Material Symbols Rounded' !important; }
html, body { direction: rtl; }
.stApp { direction: rtl; text-align: right; background: var(--bg); color: var(--ink); }
[data-baseweb="popover"], [data-baseweb="popover"] *, [data-baseweb="menu"], [role="listbox"], [role="option"], [data-testid="stSelectboxVirtualDropdown"] { direction: rtl; text-align: right; }
[data-baseweb="select"] > div, [data-baseweb="input"] input, .stTextInput input, .stSelectbox div[data-baseweb="select"] { text-align: right; }
.stRadio [role="radiogroup"] { direction: rtl; }
.stMarkdown, .stCaption, [data-testid="stWidgetLabel"], [data-testid="stExpander"] summary { text-align: right; }
.block-container { padding: 1.2rem 2.2rem 3rem; max-width: 1400px; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: #ffffff; border-left: 1px solid var(--line); direction: rtl; }
[data-testid="stSidebar"] .block-container { padding-top: 1rem; }
[data-testid="stDateInput"] input { direction: rtl; text-align: right; font-size: .85rem; }
[data-testid="stSidebar"] [data-testid="stExpander"] input { direction: ltr; text-align: right; }
.side-label { font-size: .875rem; margin: 8px 0 -4px; color: var(--ink); }
[data-testid="stPlotlyChart"] { direction: ltr; background: #ffffff; border: 1px solid var(--line); border-radius: 16px; padding: 8px 6px; box-shadow: 0 2px 10px rgba(31,42,68,.05); }
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
[data-testid="stExpander"] { background: #ffffff; border: 1px solid var(--line); border-radius: 14px; }
[data-testid="stExpander"] summary { font-weight: 600; }
.stTabs [role="tablist"], .stTabs [data-baseweb="tab-list"] { gap: 6px; background: #e9eef8; padding: 5px; border-radius: 14px; border-bottom: none !important; box-shadow: none !important; }
.stTabs [role="tab"], .stTabs [data-baseweb="tab"] { height: 42px; border-radius: 10px; padding: 0 20px; font-weight: 600; color: var(--muted); border-bottom: none !important; }
.stTabs [role="tab"][aria-selected="true"], .stTabs [data-baseweb="tab"][aria-selected="true"] { background: #ffffff; color: var(--primary); box-shadow: 0 2px 8px rgba(31,42,68,.08); }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"], .stTabs [data-testid="stTabHighlight"], .stTabs [data-testid="stTabBorder"] { display: none !important; }
.stTabs [role="tablist"]::before, .stTabs [role="tablist"]::after, .stTabs [role="tab"]::before, .stTabs [role="tab"]::after { display: none !important; }
.stTabs [role="tablist"] { border: none !important; }
.stAppDeployButton, [data-testid="stAppDeployButton"] { display: none; }
[data-testid="stSidebar"][aria-expanded="true"] { min-width: 340px; max-width: 340px; }
.hero { position: relative; overflow: hidden; background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 55%, #38bdf8 100%); border-radius: 20px; padding: 26px 30px 22px; color: #ffffff; box-shadow: 0 10px 30px rgba(37,99,235,.25); margin-bottom: 18px; }
.hero::after { content: ""; position: absolute; left: -70px; top: -70px; width: 240px; height: 240px; border-radius: 50%; background: rgba(255,255,255,.08); }
.hero-title { font-size: 1.8rem; font-weight: 800; line-height: 1.5; color: #ffffff; }
.hero-sub { font-size: .95rem; color: rgba(255,255,255,.86); margin: 2px 0 14px; line-height: 1.9; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; position: relative; z-index: 1; }
.chip { background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.3); padding: 4px 14px; border-radius: 999px; font-size: .82rem; }
.section-title { display: flex; align-items: center; gap: 10px; font-size: 1.15rem; font-weight: 700; margin: 26px 0 12px; color: var(--ink); }
.section-title::before { content: ""; width: 5px; height: 22px; border-radius: 4px; background: var(--primary); }
.section-sub { font-size: .85rem; color: var(--muted); font-weight: 400; margin-right: 4px; }
.kpi { position: relative; overflow: hidden; background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 16px 20px 16px 18px; box-shadow: 0 2px 10px rgba(31,42,68,.05); min-height: 160px; }
.kpi::before { content: ""; position: absolute; right: 0; top: 0; bottom: 0; width: 5px; background: var(--accent); }
.kpi-top { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.kpi-icon { width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
.kpi-label { font-size: .9rem; color: var(--muted); font-weight: 500; }
.kpi-value { font-size: 1.95rem; font-weight: 800; color: var(--ink); line-height: 1.3; }
.kpi-sub { font-size: .78rem; color: var(--muted); margin-top: 2px; }
.kpi-bar { height: 6px; background: #eef1f7; border-radius: 6px; margin-top: 10px; overflow: hidden; }
.kpi-bar span { display: block; height: 100%; border-radius: 6px; }
.mini { background: #ffffff; border: 1px solid var(--line); border-radius: 14px; padding: 12px 16px; margin-bottom: 10px; border-right: 4px solid var(--accent, #2563eb); box-shadow: 0 2px 8px rgba(31,42,68,.04); }
.mini-label { font-size: .8rem; color: var(--muted); }
.mini-value { font-size: 1.25rem; font-weight: 700; color: var(--ink); line-height: 1.6; }
.mini-sub { font-size: .78rem; color: var(--muted); }
.note { background: #eef4ff; border: 1px solid #d6e4ff; color: #28407a; border-radius: 12px; padding: 10px 14px; font-size: .86rem; line-height: 1.9; margin: 4px 0 14px; }
.side-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 4px; }
.side-sub { font-size: .8rem; color: var(--muted); margin-bottom: 8px; }
.footer { text-align: center; color: var(--muted); font-size: .8rem; margin-top: 30px; padding-top: 14px; border-top: 1px solid var(--line); }
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ==================================================
# KPI Definitions
# ==================================================

KPI_OPTIONS = {
    "نرخ پاسخگویی": {
        "column": "answer_rate_pct",
        "unit": "درصد",
        "is_percentage": True,
        "kind": "percent",
        "color": "#16a34a",
    },
    "نرخ تماس‌های رهاشده": {
        "column": "abandon_rate_pct",
        "unit": "درصد",
        "is_percentage": True,
        "kind": "percent",
        "color": "#dc2626",
    },
    "میانگین زمان انتظار": {
        "column": "average_wait_time_seconds",
        "unit": "ثانیه",
        "is_percentage": False,
        "kind": "seconds",
        "color": "#f97316",
    },
    "میانگین زمان رسیدگی": {
        "column": "average_handle_time_seconds",
        "unit": "ثانیه",
        "is_percentage": False,
        "kind": "seconds",
        "color": "#7c3aed",
    },
    "میانگین رضایت مشتری": {
        "column": "average_csat_score",
        "unit": "امتیاز",
        "is_percentage": False,
        "kind": "score",
        "color": "#eab308",
    },
    "نرخ حل مشکل در تماس اول": {
        "column": "fcr_rate_pct",
        "unit": "درصد",
        "is_percentage": True,
        "kind": "percent",
        "color": "#0891b2",
    },
}


# ==================================================
# Persian Labels for API Values
# ==================================================

TEAM_FA = {
    "Billing": "صورتحساب",
    "Sales": "فروش",
    "Support": "پشتیبانی",
    "Unknown": "نامشخص",
}
SHIFT_FA = {
    "Morning": "صبح",
    "Evening": "عصر",
    "Night": "شب",
    "Unknown": "نامشخص",
}
SHIFT_ORDER = {"Morning": 0, "Evening": 1, "Night": 2}

GROUP_COLORS = {
    "صورتحساب": "#6366f1",
    "فروش": "#10b981",
    "پشتیبانی": "#f59e0b",
    "صبح": "#f59e0b",
    "عصر": "#8b5cf6",
    "شب": "#334155",
}
FALLBACK_COLORS = ["#2563eb", "#14b8a6", "#f97316", "#ec4899", "#84cc16"]

TABLE_LABELS = {
    "team": "تیم",
    "shift": "شیفت",
    "date": "تاریخ",
    "total_calls": "کل تماس‌ها",
    "answered_calls": "تماس‌های پاسخ‌داده‌شده",
    "abandoned_calls": "تماس‌های رهاشده",
    "transferred_calls": "تماس‌های منتقل‌شده",
    "handled_calls": "پاسخ‌داده‌شده یا منتقل‌شده",
    "answer_rate_pct": "نرخ پاسخگویی (٪)",
    "abandon_rate_pct": "نرخ رهاشدن (٪)",
    "average_wait_time_seconds": "میانگین انتظار (ثانیه)",
    "average_handle_time_seconds": "میانگین رسیدگی (ثانیه)",
    "average_csat_score": "میانگین رضایت مشتری",
    "fcr_eligible_calls": "تماس‌های واجد شرایط حل مشکل",
    "fcr_resolved_calls": "حل‌شده در تماس اول",
    "fcr_rate_pct": "نرخ حل مشکل در تماس اول (٪)",
}
COUNT_COLUMNS = [
    "total_calls",
    "answered_calls",
    "abandoned_calls",
    "transferred_calls",
    "handled_calls",
    "fcr_eligible_calls",
    "fcr_resolved_calls",
]
PERCENT_COLUMNS = ["answer_rate_pct", "abandon_rate_pct", "fcr_rate_pct"]
SECONDS_COLUMNS = ["average_wait_time_seconds", "average_handle_time_seconds"]
SCORE_COLUMNS = ["average_csat_score"]

JALALI_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]

_FA_TRANSLATION = str.maketrans("0123456789.,%", "۰۱۲۳۴۵۶۷۸۹٫٬٪")


# ==================================================
# Formatting Helpers (Persian digits, Jalali dates)
# ==================================================

def fa(text) -> str:
    """Convert Latin digits and separators in a numeric string to Persian."""

    return str(text).translate(_FA_TRANSLATION)


def fa_num(value, digits: int = 0) -> str:
    if value is None or pd.isna(value):
        return "—"
    return fa(f"{float(value):,.{digits}f}")


def fmt_number(value, digits: int = 0) -> str:
    return fa_num(value, digits)


def fmt_percent(value) -> str:
    if value is None or pd.isna(value):
        return "—"
    return fa(f"{float(value):.2f}") + "٪"


def fmt_seconds(value) -> str:
    if value is None or pd.isna(value):
        return "—"
    total_seconds = max(0, int(round(float(value))))
    minutes, seconds = divmod(total_seconds, 60)
    return fa(f"{minutes} دقیقه و {seconds} ثانیه")


def fmt_mmss(value) -> str:
    if value is None or pd.isna(value):
        return "—"
    total_seconds = max(0, int(round(float(value))))
    minutes, seconds = divmod(total_seconds, 60)
    return fa(f"{minutes}:{seconds:02d}")


def fmt_metric(metric: dict, value) -> str:
    kind = metric["kind"]
    if kind == "percent":
        return fmt_percent(value)
    if kind == "seconds":
        return f"{fa_num(value, 1)} ثانیه"
    return fa_num(value, 2)


def gregorian_to_jalali(gy: int, gm: int, gd: int) -> tuple[int, int, int]:
    """Convert a Gregorian date to the Jalali (Solar Hijri) calendar."""

    cumulative_days = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = (
        355666
        + (365 * gy)
        + ((gy2 + 3) // 4)
        - ((gy2 + 99) // 100)
        + ((gy2 + 399) // 400)
        + gd
        + cumulative_days[gm - 1]
    )
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd


def fmt_date(value, calendar: str = CAL_JALALI, short: bool = False) -> str:
    if value is None or pd.isna(value):
        return "—"
    stamp = pd.Timestamp(value)
    if calendar == CAL_JALALI:
        jy, jm, jd = gregorian_to_jalali(stamp.year, stamp.month, stamp.day)
        text = f"{jd} {JALALI_MONTHS[jm - 1]}"
        if not short:
            text += f" {jy}"
        return fa(text)
    return fa(stamp.strftime("%m/%d" if short else "%Y/%m/%d"))


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    value = hex_color.lstrip("#")
    r, g, b = (int(value[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


# ==================================================
# API Helpers
# ==================================================

@st.cache_data(ttl=30, show_spinner=False)
def api_get(base_url: str, endpoint: str, params: dict | None = None) -> dict:
    """Fetch JSON data from the existing FastAPI service."""

    response = requests.get(
        f"{base_url.rstrip('/')}{endpoint}",
        params=params or {},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def make_params(
    team: str | None = None,
    shift: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict:
    """Build query parameters, excluding unset filters."""

    params = {}
    if team is not None:
        params["team"] = team
    if shift is not None:
        params["shift"] = shift
    if start_date is not None:
        params["start_date"] = start_date.isoformat()
    if end_date is not None:
        params["end_date"] = end_date.isoformat()
    return params


# ==================================================
# HTML Components
# ==================================================

def hero_html(chips: list[str]) -> str:
    chips_html = "".join(f'<span class="chip">{html.escape(c)}</span>' for c in chips)
    return (
        '<div class="hero">'
        '<div class="hero-title">📞 داشبورد تحلیل مرکز تماس</div>'
        '<div class="hero-sub">نرخ پاسخگویی، نرخ رهاشدن، زمان انتظار، زمان رسیدگی، '
        "رضایت مشتری و حل مشکل در تماس اول؛ به تفکیک تیم، شیفت و روز</div>"
        f'<div class="chips">{chips_html}</div>'
        "</div>"
    )


def section_title(text: str, sub: str = "") -> None:
    sub_html = f'<span class="section-sub">{html.escape(sub)}</span>' if sub else ""
    st.markdown(
        f'<div class="section-title">{html.escape(text)}{sub_html}</div>',
        unsafe_allow_html=True,
    )


def note(text: str) -> None:
    st.markdown(f'<div class="note">ℹ️ {html.escape(text)}</div>', unsafe_allow_html=True)


def kpi_card(
    icon: str,
    label: str,
    value: str,
    sub: str = "",
    accent: str = "#2563eb",
    progress=None,
    help_text: str = "",
) -> str:
    bar_html = ""
    if progress is not None and not pd.isna(progress):
        width = max(0.0, min(100.0, float(progress)))
        bar_html = (
            f'<div class="kpi-bar"><span style="width:{width:.2f}%;background:{accent}"></span></div>'
        )
    sub_html = f'<div class="kpi-sub">{html.escape(sub)}</div>' if sub else ""
    return (
        f'<div class="kpi" style="--accent:{accent}" title="{html.escape(help_text)}">'
        '<div class="kpi-top">'
        f'<div class="kpi-icon" style="background:{hex_to_rgba(accent, 0.12)}">{icon}</div>'
        f'<div class="kpi-label">{html.escape(label)}</div>'
        "</div>"
        f'<div class="kpi-value">{html.escape(value)}</div>'
        f"{sub_html}{bar_html}"
        "</div>"
    )


def mini_card(label: str, value: str, sub: str = "", accent: str = "#2563eb") -> str:
    sub_html = f'<div class="mini-sub">{html.escape(sub)}</div>' if sub else ""
    return (
        f'<div class="mini" style="--accent:{accent}">'
        f'<div class="mini-label">{html.escape(label)}</div>'
        f'<div class="mini-value">{html.escape(value)}</div>'
        f"{sub_html}</div>"
    )


# ==================================================
# Chart Helpers
# ==================================================

PLOT_CONFIG = {"displayModeBar": False, "displaylogo": False}


def _stretch_kwargs(func) -> dict:
    """Use width='stretch' on new Streamlit versions, use_container_width on old ones."""

    if "width" in inspect.signature(func).parameters:
        return {"width": "stretch"}
    return {"use_container_width": True}


STRETCH_PLOT = _stretch_kwargs(st.plotly_chart)
STRETCH_TABLE = _stretch_kwargs(st.dataframe)


def nice_ticks(lo: float, hi: float, target: int = 5) -> tuple[list[float], float]:
    """Return readable axis ticks covering [lo, hi]."""

    if hi <= lo:
        hi = lo + 1
    raw = (hi - lo) / max(target - 1, 1)
    magnitude = 10 ** math.floor(math.log10(raw))
    step = magnitude
    for multiplier in (1, 2, 2.5, 5, 10):
        step = multiplier * magnitude
        if step >= raw:
            break
    first = math.floor(lo / step) * step
    last = math.ceil(hi / step) * step
    count = int(round((last - first) / step))
    return [round(first + i * step, 8) for i in range(count + 1)], step


def tick_texts(ticks: list[float], step: float, is_percentage: bool) -> list[str]:
    decimals = 0
    while abs(step * 10**decimals - round(step * 10**decimals)) > 1e-9 and decimals < 4:
        decimals += 1
    suffix = "٪" if is_percentage else ""
    return [fa_num(t, decimals) + suffix for t in ticks]


def apply_base_layout(fig: go.Figure, title: str, height: int = 430) -> None:
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            x=0.97,
            xanchor="right",
            y=0.95,
            font=dict(size=16, color=INK),
        ),
        font=dict(family=FONT_STACK, size=13, color=INK),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        height=height,
        margin=dict(t=75, r=72, b=45, l=24),
        hoverlabel=dict(
            font=dict(family=FONT_STACK, size=13, color=INK),
            bgcolor="#ffffff",
            bordercolor=LINE,
        ),
        showlegend=False,
        bargap=0.5,
    )
    # Right-to-left charts: categories/time run from right to left and the value axis sits on the right.
    fig.update_xaxes(
        showgrid=False,
        linecolor=LINE,
        tickfont=dict(size=13, color=INK),
        autorange="reversed",
    )
    fig.update_yaxes(
        gridcolor="#eef1f7",
        zeroline=False,
        tickfont=dict(size=12, color=MUTED),
        side="right",
        automargin=True,
    )
    fig.update_layout(hoverlabel=dict(align="right"))


def prepare_group_df(df: pd.DataFrame, group_column: str, metric_label: str):
    """Validate and prepare grouped KPI data; return None when nothing can be drawn."""

    value_column = KPI_OPTIONS[metric_label]["column"]

    if df.empty or group_column not in df.columns or value_column not in df.columns:
        st.info("برای این انتخاب‌ها داده‌ای جهت نمایش نمودار وجود ندارد.")
        return None

    plot_df = df.copy()
    plot_df[value_column] = pd.to_numeric(plot_df[value_column], errors="coerce")
    plot_df = plot_df.dropna(subset=[value_column])

    if plot_df.empty:
        st.info("برای این شاخص مقدار قابل‌نمایشی وجود ندارد.")
        return None

    labels = TEAM_FA if group_column == "team" else SHIFT_FA
    plot_df["label_fa"] = plot_df[group_column].map(lambda v: labels.get(v, v))
    if group_column == "shift":
        plot_df["_order"] = plot_df[group_column].map(lambda v: SHIFT_ORDER.get(v, 99))
        plot_df = plot_df.sort_values("_order")
    return plot_df.reset_index(drop=True)


def build_bar_figure(plot_df: pd.DataFrame, metric_label: str, title: str) -> go.Figure:
    metric = KPI_OPTIONS[metric_label]
    value_column = metric["column"]
    labels = plot_df["label_fa"].tolist()
    values = [float(v) for v in plot_df[value_column]]
    texts = [fmt_metric(metric, v) for v in values]
    colors = [
        GROUP_COLORS.get(label, FALLBACK_COLORS[i % len(FALLBACK_COLORS)])
        for i, label in enumerate(labels)
    ]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker=dict(color=colors),
            text=texts,
            textposition="outside",
            textfont=dict(size=14, color=INK),
            cliponaxis=False,
            customdata=texts,
            hovertemplate=f"<b>%{{x}}</b><br>{metric_label}: %{{customdata}}<extra></extra>",
        )
    )

    upper = 100 if metric["is_percentage"] else max(max(values) * 1.15, 1)
    ticks, step = nice_ticks(0, upper)
    fig.update_yaxes(
        tickvals=ticks,
        ticktext=tick_texts(ticks, step, metric["is_percentage"]),
        range=[0, ticks[-1] * 1.07],
    )
    apply_base_layout(fig, title)
    return fig


def prepare_daily_df(df: pd.DataFrame, metric_label: str):
    value_column = KPI_OPTIONS[metric_label]["column"]

    if df.empty or "date" not in df.columns or value_column not in df.columns:
        st.info("برای این انتخاب‌ها داده‌ی روزانه‌ای وجود ندارد.")
        return None

    plot_df = df.loc[df["date"].notna() & df["date"].ne("Unknown")].copy()
    plot_df["date"] = pd.to_datetime(plot_df["date"], errors="coerce")
    plot_df[value_column] = pd.to_numeric(plot_df[value_column], errors="coerce")
    plot_df = plot_df.dropna(subset=["date", value_column]).sort_values("date")

    if plot_df.empty:
        st.info("تاریخ یا مقدار معتبر برای این شاخص وجود ندارد.")
        return None
    return plot_df.reset_index(drop=True)


def build_line_figure(
    plot_df: pd.DataFrame, metric_label: str, calendar: str, title: str
) -> go.Figure:
    metric = KPI_OPTIONS[metric_label]
    accent = metric["color"]
    dates = [d.to_pydatetime() for d in plot_df["date"]]
    values = [float(v) for v in plot_df[metric["column"]]]
    span_days = (dates[-1] - dates[0]).days
    short_ticks = span_days < 300

    date_texts = [fmt_date(d, calendar) for d in dates]
    value_texts = [fmt_metric(metric, v) for v in values]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=values,
            mode="lines+markers",
            line=dict(color=accent, width=3),
            marker=dict(size=7, color="#ffffff", line=dict(color=accent, width=2)),
            fill="tozeroy",
            fillcolor=hex_to_rgba(accent, 0.08),
            customdata=list(zip(date_texts, value_texts)),
            hovertemplate=f"<b>%{{customdata[0]}}</b><br>{metric_label}: %{{customdata[1]}}<extra></extra>",
        )
    )

    if len(values) > 1:
        idx_max = values.index(max(values))
        idx_min = values.index(min(values))
        for idx, color in ((idx_max, "#1e3a8a"), (idx_min, "#94a3b8")):
            fig.add_trace(
                go.Scatter(
                    x=[dates[idx]],
                    y=[values[idx]],
                    mode="markers",
                    marker=dict(size=13, color=color, line=dict(color="#ffffff", width=2)),
                    hoverinfo="skip",
                )
            )

    lo, hi = min(values), max(values)
    pad = (hi - lo) * 0.15 or max(abs(hi) * 0.05, 1)
    lo, hi = lo - pad, hi + pad
    if lo < 0 <= min(values):
        lo = 0
    if metric["is_percentage"]:
        lo, hi = max(lo, 0), min(hi, 100)
    ticks, step = nice_ticks(lo, hi)
    if metric["is_percentage"]:
        ticks = [t for t in ticks if 0 <= t <= 100]
    fig.update_yaxes(
        tickvals=ticks,
        ticktext=tick_texts(ticks, step, metric["is_percentage"]),
        range=[ticks[0], ticks[-1]],
    )

    max_ticks = 8
    count = len(dates)
    if count <= max_ticks:
        positions = list(range(count))
    else:
        positions = sorted({round(i * (count - 1) / (max_ticks - 1)) for i in range(max_ticks)})
    fig.update_xaxes(
        tickmode="array",
        tickvals=[dates[i] for i in positions],
        ticktext=[fmt_date(dates[i], calendar, short=short_ticks) for i in positions],
    )

    apply_base_layout(fig, title)
    return fig


def render_table(
    df: pd.DataFrame, title: str, file_stub: str, calendar: str, table_key: str
) -> None:
    """Show a Persian table with Persian digits and a CSV download."""

    out = df.copy()
    if "team" in out.columns:
        out["team"] = out["team"].map(lambda v: TEAM_FA.get(v, v))
    if "shift" in out.columns:
        out["shift"] = out["shift"].map(lambda v: SHIFT_FA.get(v, v))
    if "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"], errors="coerce")
    for column in COUNT_COLUMNS + PERCENT_COLUMNS + SECONDS_COLUMNS + SCORE_COLUMNS:
        if column in out.columns:
            out[column] = pd.to_numeric(out[column], errors="coerce")

    formatters = {}
    for column in out.columns:
        label = TABLE_LABELS.get(column, column)
        if column in COUNT_COLUMNS:
            formatters[label] = lambda v: fa_num(v, 0)
        elif column in PERCENT_COLUMNS:
            formatters[label] = lambda v: fa_num(v, 2)
        elif column in SECONDS_COLUMNS:
            formatters[label] = lambda v: fa_num(v, 1)
        elif column in SCORE_COLUMNS:
            formatters[label] = lambda v: fa_num(v, 2)
        elif column == "date":
            formatters[label] = lambda v: fmt_date(v, calendar)

    out = out.rename(columns=TABLE_LABELS)

    with st.expander(title, expanded=False):
        try:
            shown = out.style.format(formatters, na_rep="—")
        except Exception:  # Styler needs jinja2; fall back to the plain table.
            shown = out
        st.dataframe(shown, hide_index=True, **STRETCH_TABLE)
        st.download_button(
            "⬇️ دانلود جدول (CSV)",
            data=out.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{file_stub}.csv",
            mime="text/csv",
            key=f"download_{table_key}",
        )


def render_group_tab(
    df: pd.DataFrame,
    group_column: str,
    tab_key: str,
    chart_prefix: str,
    note_text: str,
    empty_text: str,
    table_title: str,
    file_stub: str,
    calendar: str,
) -> None:
    note(note_text)

    if df.empty:
        st.info(empty_text)
        return

    metric_label = st.selectbox(
        "شاخص موردنظر برای نمودار",
        options=list(KPI_OPTIONS.keys()),
        key=f"{tab_key}_metric",
    )
    plot_df = prepare_group_df(df, group_column, metric_label)

    if plot_df is not None:
        metric = KPI_OPTIONS[metric_label]
        column = metric["column"]
        fig = build_bar_figure(plot_df, metric_label, f"{chart_prefix} {metric_label}")

        chart_col, side_col = st.columns([3, 1], gap="medium")
        with chart_col:
            st.plotly_chart(fig, config=PLOT_CONFIG, **STRETCH_PLOT)
        with side_col:
            top = plot_df.loc[plot_df[column].idxmax()]
            bottom = plot_df.loc[plot_df[column].idxmin()]
            st.markdown(
                mini_card("بیشترین مقدار", fmt_metric(metric, top[column]), top["label_fa"], "#1e3a8a"),
                unsafe_allow_html=True,
            )
            if len(plot_df) > 1:
                st.markdown(
                    mini_card("کمترین مقدار", fmt_metric(metric, bottom[column]), bottom["label_fa"], "#94a3b8"),
                    unsafe_allow_html=True,
                )
                gap = float(top[column]) - float(bottom[column])
                gap_text = (
                    f"{fa_num(gap, 2)} واحد درصد"
                    if metric["kind"] == "percent"
                    else fmt_metric(metric, gap)
                )
                st.markdown(
                    mini_card("اختلاف بیشترین و کمترین", gap_text, "", metric["color"]),
                    unsafe_allow_html=True,
                )

    render_table(df, table_title, file_stub, calendar, tab_key)


# ==================================================
# Header Placeholder (filled after filters are known)
# ==================================================

hero_slot = st.empty()
hero_slot.markdown(hero_html([]), unsafe_allow_html=True)


# ==================================================
# Sidebar Filters
# ==================================================

with st.sidebar:
    st.markdown('<div class="side-title">🎛️ فیلترهای داشبورد</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-sub">با تغییر هر فیلتر، شاخص‌ها دوباره محاسبه می‌شوند.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("🔌 اتصال به API", expanded=False):
        base_url = st.text_input(
            "آدرس API",
            value="http://127.0.0.1:8000",
            help="ابتدا FastAPI را اجرا کن: python -m uvicorn main:app --reload",
        ).strip().rstrip("/")

    selected_team = st.selectbox(
        "تیم",
        options=[None, "Billing", "Sales", "Support"],
        format_func=lambda v: "همه‌ی تیم‌ها" if v is None else TEAM_FA.get(v, v),
        help="روی خلاصه‌ی عملکرد، مقایسه‌ی شیفت‌ها و روند روزانه اعمال می‌شود.",
    )

    selected_shift = st.selectbox(
        "شیفت",
        options=[None, "Morning", "Evening", "Night"],
        format_func=lambda v: "همه‌ی شیفت‌ها" if v is None else SHIFT_FA.get(v, v),
        help="روی خلاصه‌ی عملکرد، مقایسه‌ی تیم‌ها و روند روزانه اعمال می‌شود.",
    )


# ==================================================
# Discover Date Range
# ==================================================

try:
    all_daily_response = api_get(base_url, "/api/kpis/daily")
except requests.RequestException as exc:
    st.error(
        "اتصال به API برقرار نشد. بررسی کن FastAPI فعال باشد و آدرس API درست باشد. "
        f"جزئیات خطا: {exc}"
    )
    st.code("python -m uvicorn main:app --reload", language="powershell")
    st.stop()
except (ValueError, TypeError) as exc:
    st.error(f"پاسخ API قابل‌خواندن نیست: {exc}")
    st.stop()

all_daily_df = pd.DataFrame(all_daily_response.get("data", []))
parsed_dates = pd.Series(dtype="datetime64[ns]")
if not all_daily_df.empty and "date" in all_daily_df.columns:
    raw_dates = all_daily_df.loc[
        all_daily_df["date"].notna() & all_daily_df["date"].ne("Unknown"),
        "date",
    ]
    parsed_dates = pd.to_datetime(raw_dates, errors="coerce").dropna()

if not parsed_dates.empty:
    min_data_date = parsed_dates.min().date()
    max_data_date = parsed_dates.max().date()
else:
    min_data_date = date.today()
    max_data_date = date.today()

with st.sidebar:
    st.markdown(
        '<div class="side-label">بازه‌ی زمانی (تقویم میلادی)</div>',
        unsafe_allow_html=True,
    )
    start_date = st.date_input(
        "از تاریخ",
        value=min_data_date,
        min_value=min_data_date,
        max_value=max_data_date,
        help="روز شروع و روز پایان هر دو در بازه محسوب می‌شوند.",
    )
    end_date = st.date_input(
        "تا تاریخ",
        value=max_data_date,
        min_value=min_data_date,
        max_value=max_data_date,
    )
    if start_date > end_date:
        st.error("تاریخ شروع نباید بعد از تاریخ پایان باشد.")
        st.stop()

    calendar = st.radio(
        "تقویم نمایش تاریخ‌ها",
        options=[CAL_JALALI, CAL_GREGORIAN],
        horizontal=True,
        help="فقط روی نمایش تاریخ در نمودارها و جدول‌ها اثر دارد.",
    )

# Fill the header now that all filters are known.
range_text = (
    f"{fmt_date(start_date, calendar)} تا {fmt_date(end_date, calendar)}"
    if start_date and end_date
    else "—"
)
hero_slot.markdown(
    hero_html(
        [
            "👥 تیم: "
            + "، ".join(
                TEAM_FA[t] for t in (["Billing", "Sales", "Support"] if selected_team is None else [selected_team])
            ),
            "🕒 شیفت: "
            + "، ".join(
                SHIFT_FA[s] for s in (["Morning", "Evening", "Night"] if selected_shift is None else [selected_shift])
            ),
            f"📅 بازه: {range_text}",
        ]
    ),
    unsafe_allow_html=True,
)


# ==================================================
# Fetch Data From API
# ==================================================

try:
    with st.spinner("در حال دریافت شاخص‌ها از API..."):
        summary_response = api_get(
            base_url,
            "/api/kpis/summary",
            make_params(
                team=selected_team,
                shift=selected_shift,
                start_date=start_date,
                end_date=end_date,
            ),
        )

        # Compare all teams; selected shift/date apply, selected team does not.
        teams_response = api_get(
            base_url,
            "/api/kpis/teams",
            make_params(
                shift=selected_shift,
                start_date=start_date,
                end_date=end_date,
            ),
        )

        # Compare all shifts; selected team/date apply, selected shift does not.
        shifts_response = api_get(
            base_url,
            "/api/kpis/shifts",
            make_params(
                team=selected_team,
                start_date=start_date,
                end_date=end_date,
            ),
        )

        # Daily data respects every selected filter.
        daily_response = api_get(
            base_url,
            "/api/kpis/daily",
            make_params(
                team=selected_team,
                shift=selected_shift,
                start_date=start_date,
                end_date=end_date,
            ),
        )
except requests.RequestException as exc:
    st.error(f"دریافت داده از API با خطا مواجه شد: {exc}")
    st.stop()
except (ValueError, TypeError) as exc:
    st.error(f"پارامتر یا پاسخ API معتبر نیست: {exc}")
    st.stop()

kpis = summary_response.get("kpis", {})
teams_df = pd.DataFrame(teams_response.get("data", []))
shifts_df = pd.DataFrame(shifts_response.get("data", []))
daily_df = pd.DataFrame(daily_response.get("data", []))


# ==================================================
# Overall KPI Cards
# ==================================================

section_title("خلاصه‌ی عملکرد", "بر اساس فیلترهای انتخاب‌شده")

answered = kpis.get("answered_calls")
abandoned = kpis.get("abandoned_calls")
awt = kpis.get("average_wait_time_seconds")
aht = kpis.get("average_handle_time_seconds")

row1 = st.columns(4, gap="medium")
row1[0].markdown(
    kpi_card(
        "📞",
        "کل تماس‌ها",
        fmt_number(kpis.get("total_calls")),
        "تعداد تماس‌های ثبت‌شده",
        "#4f46e5",
        help_text="تعداد کل تماس‌های ورودی در بازه و فیلترهای انتخاب‌شده",
    ),
    unsafe_allow_html=True,
)
row1[1].markdown(
    kpi_card(
        "✅",
        "نرخ پاسخگویی",
        fmt_percent(kpis.get("answer_rate_pct")),
        f"{fmt_number(answered)} تماس پاسخ داده شده" if answered is not None else "",
        "#16a34a",
        progress=kpis.get("answer_rate_pct"),
        help_text="درصد تماس‌هایی که پاسخ داده شده‌اند",
    ),
    unsafe_allow_html=True,
)
row1[2].markdown(
    kpi_card(
        "📵",
        "نرخ تماس‌های رهاشده",
        fmt_percent(kpis.get("abandon_rate_pct")),
        f"{fmt_number(abandoned)} تماس رهاشده" if abandoned is not None else "",
        "#dc2626",
        progress=kpis.get("abandon_rate_pct"),
        help_text="درصد تماس‌هایی که مشتری پیش از دریافت پاسخ قطع کرده است",
    ),
    unsafe_allow_html=True,
)
row1[3].markdown(
    kpi_card(
        "🎯",
        "حل مشکل در تماس اول",
        fmt_percent(kpis.get("fcr_rate_pct")),
        f"{fmt_number(kpis.get('fcr_resolved_calls'))} از {fmt_number(kpis.get('fcr_eligible_calls'))} تماس واجد شرایط",
        "#0891b2",
        progress=kpis.get("fcr_rate_pct"),
        help_text="درصد تماس‌هایی که مشکل مشتری در همان تماس اول حل شده است",
    ),
    unsafe_allow_html=True,
)

st.write("")
row2 = st.columns(3, gap="medium")
row2[0].markdown(
    kpi_card(
        "⏳",
        "میانگین زمان انتظار",
        fmt_mmss(awt),
        f"دقیقه:ثانیه · {fa_num(awt, 1)} ثانیه",
        "#f97316",
        help_text="میانگین مدت انتظار مشتری تا دریافت پاسخ",
    ),
    unsafe_allow_html=True,
)
row2[1].markdown(
    kpi_card(
        "⏱️",
        "میانگین زمان رسیدگی",
        fmt_mmss(aht),
        f"دقیقه:ثانیه · {fa_num(aht, 1)} ثانیه",
        "#7c3aed",
        help_text="میانگین مدت زمانی که برای رسیدگی به هر تماس صرف می‌شود",
    ),
    unsafe_allow_html=True,
)
row2[2].markdown(
    kpi_card(
        "⭐",
        "میانگین رضایت مشتری",
        fmt_number(kpis.get("average_csat_score"), 2),
        "میانگین امتیازهای ثبت‌شده",
        "#eab308",
        help_text="میانگین امتیاز رضایت مشتریان از تماس",
    ),
    unsafe_allow_html=True,
)

st.write("")
with st.expander("🔍 جزئیات محاسبه‌ی حل مشکل در تماس اول"):
    eligible = kpis.get("fcr_eligible_calls") or 0
    resolved = kpis.get("fcr_resolved_calls") or 0
    fcr_cols = st.columns(3, gap="medium")
    fcr_cols[0].markdown(mini_card("تماس‌های واجد شرایط", fmt_number(eligible), "", "#0891b2"), unsafe_allow_html=True)
    fcr_cols[1].markdown(mini_card("حل‌شده در تماس اول", fmt_number(resolved), "", "#16a34a"), unsafe_allow_html=True)
    fcr_cols[2].markdown(mini_card("حل‌نشده در تماس اول", fmt_number(eligible - resolved), "", "#dc2626"), unsafe_allow_html=True)


# ==================================================
# Team, Shift, and Daily Views
# ==================================================

section_title("تحلیل تفصیلی", "مقایسه‌ی تیم‌ها، شیفت‌ها و روند روزانه")

tab_teams, tab_shifts, tab_daily = st.tabs(
    ["👥 مقایسه‌ی تیم‌ها", "🕒 مقایسه‌ی شیفت‌ها", "📈 روند روزانه"]
)

with tab_teams:
    render_group_tab(
        teams_df,
        group_column="team",
        tab_key="team",
        chart_prefix="مقایسه‌ی تیم‌ها بر اساس",
        note_text=(
            "این بخش همه‌ی تیم‌ها را مقایسه می‌کند؛ فیلتر شیفت و تاریخ اعمال می‌شود، "
            "اما فیلتر تیم عمداً اعمال نمی‌شود تا مقایسه‌ی تیم‌ها حفظ شود."
        ),
        empty_text="برای فیلترهای انتخاب‌شده داده‌ای برای مقایسه‌ی تیم‌ها وجود ندارد.",
        table_title="📋 جدول کامل شاخص‌ها برای تمام تیم‌ها",
        file_stub="kpi_by_team",
        calendar=calendar,
    )

with tab_shifts:
    render_group_tab(
        shifts_df,
        group_column="shift",
        tab_key="shift",
        chart_prefix="مقایسه‌ی شیفت‌ها بر اساس",
        note_text=(
            "این بخش همه‌ی شیفت‌ها را مقایسه می‌کند؛ فیلتر تیم و تاریخ اعمال می‌شود، "
            "اما فیلتر شیفت عمداً اعمال نمی‌شود تا مقایسه‌ی شیفت‌ها حفظ شود."
        ),
        empty_text="برای فیلترهای انتخاب‌شده داده‌ای برای مقایسه‌ی شیفت‌ها وجود ندارد.",
        table_title="📋 جدول کامل شاخص‌ها برای تمام شیفت‌ها",
        file_stub="kpi_by_shift",
        calendar=calendar,
    )

with tab_daily:
    note(
        "روند روزانه بر اساس تمام فیلترهای انتخاب‌شده، شامل تیم، شیفت و بازه‌ی تاریخ، محاسبه می‌شود."
    )

    if daily_df.empty:
        st.info("برای فیلترهای انتخاب‌شده داده‌ی روزانه‌ای وجود ندارد.")
    else:
        daily_metric_label = st.selectbox(
            "شاخص موردنظر برای روند روزانه",
            options=list(KPI_OPTIONS.keys()),
            key="daily_metric",
        )
        daily_plot_df = prepare_daily_df(daily_df, daily_metric_label)

        if daily_plot_df is not None:
            metric = KPI_OPTIONS[daily_metric_label]
            column = metric["column"]
            fig = build_line_figure(
                daily_plot_df,
                daily_metric_label,
                calendar,
                f"روند روزانه‌ی {daily_metric_label}",
            )

            chart_col, side_col = st.columns([3, 1], gap="medium")
            with chart_col:
                st.plotly_chart(fig, config=PLOT_CONFIG, **STRETCH_PLOT)
            with side_col:
                top = daily_plot_df.loc[daily_plot_df[column].idxmax()]
                bottom = daily_plot_df.loc[daily_plot_df[column].idxmin()]
                last = daily_plot_df.iloc[-1]
                st.markdown(
                    mini_card(
                        "بیشترین مقدار",
                        fmt_metric(metric, top[column]),
                        fmt_date(top["date"], calendar),
                        "#1e3a8a",
                    ),
                    unsafe_allow_html=True,
                )
                if len(daily_plot_df) > 1:
                    st.markdown(
                        mini_card(
                            "کمترین مقدار",
                            fmt_metric(metric, bottom[column]),
                            fmt_date(bottom["date"], calendar),
                            "#94a3b8",
                        ),
                        unsafe_allow_html=True,
                    )
                st.markdown(
                    mini_card(
                        "آخرین روز",
                        fmt_metric(metric, last[column]),
                        fmt_date(last["date"], calendar),
                        metric["color"],
                    ),
                    unsafe_allow_html=True,
                )

        table_df = daily_df.loc[daily_df["date"].notna() & daily_df["date"].ne("Unknown")].copy()
        table_df["date"] = pd.to_datetime(table_df["date"], errors="coerce")
        table_df = table_df.dropna(subset=["date"]).sort_values("date")
        render_table(
            table_df,
            "📋 جدول کامل شاخص‌ها به تفکیک روز",
            "kpi_by_day",
            calendar,
            "daily",
        )


# ==================================================
# Footer
# ==================================================

st.markdown(
    '<div class="footer">داشبورد تحلیل مرکز تماس · شاخص‌ها به‌صورت زنده از سرویس داده دریافت می‌شوند</div>',
    unsafe_allow_html=True,
)