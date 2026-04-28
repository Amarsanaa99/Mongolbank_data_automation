import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(
    page_title="СЭЗИС — Багшийн хөгжлийн KPI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: #0a0f1e;
    color: #c8d8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080d1a 0%, #0a1228 100%);
    border-right: 1px solid #162040;
}
[data-testid="stSidebar"] * { color: #8aaad8 !important; }

/* Dept buttons in sidebar */
div[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    text-align: left !important;
    background: #0d1830 !important;
    color: #7090c0 !important;
    border: 1px solid #1a2e5a !important;
    border-radius: 8px !important;
    padding: 8px 14px !important;
    font-size: 13px !important;
    margin-bottom: 4px !important;
    transition: all 0.15s !important;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: #1a3060 !important;
    color: #fff !important;
    border-color: #3a6adc !important;
}

/* Active dept button */
.dept-active > div > button {
    background: linear-gradient(135deg, #1a3a7a, #2a4d9a) !important;
    color: #ffffff !important;
    border-color: #4a7acc !important;
    font-weight: 600 !important;
}

/* KPI metric cards */
.kpi-card {
    background: linear-gradient(135deg, #0d1f4a 0%, #112240 100%);
    border: 1px solid #1a3060;
    border-radius: 14px;
    padding: 18px 16px 14px;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.2s;
}
.kpi-card:hover { border-color: #3a6adc; transform: translateY(-2px); }
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.kpi-blue::before { background: linear-gradient(90deg, #00c8ff, #0080ff); }
.kpi-green::before { background: linear-gradient(90deg, #00e676, #00b248); }
.kpi-purple::before { background: linear-gradient(90deg, #b388ff, #7c4dff); }
.kpi-orange::before { background: linear-gradient(90deg, #ffab40, #ff6d00); }
.kpi-pink::before { background: linear-gradient(90deg, #ff80ab, #f50057); }
.kpi-teal::before { background: linear-gradient(90deg, #64ffda, #00bfa5); }

.kpi-icon { font-size: 20px; margin-bottom: 6px; }
.kpi-num { font-size: 34px; font-weight: 700; line-height: 1; margin-bottom: 4px; }
.kpi-num-blue { color: #00d4ff; }
.kpi-num-green { color: #00e676; }
.kpi-num-purple { color: #b388ff; }
.kpi-num-orange { color: #ffab40; }
.kpi-num-pink { color: #ff80ab; }
.kpi-num-teal { color: #64ffda; }
.kpi-label { color: #6080a8; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }

/* Section divider */
.section-title {
    color: #4a8aff;
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    border-bottom: 1px solid #1a3060;
    padding-bottom: 8px;
    margin: 24px 0 12px 0;
}

/* Percent badge */
.pct-badge {
    display: inline-block;
    background: #0d1f4a;
    border: 1px solid #1a3060;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 4px;
    text-align: center;
    min-width: 140px;
}
.pct-val { font-size: 22px; font-weight: 700; }
.pct-lbl { font-size: 10px; color: #5070a0; margin-top: 2px; }

/* Year badge */
.year-badge {
    background: #0d1830;
    border: 1px solid #1a3060;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 12px;
    color: #5080b0;
    display: inline-block;
    margin-bottom: 8px;
}

/* Chart container */
.chart-wrap {
    background: #080e1c;
    border: 1px solid #142040;
    border-radius: 12px;
    padding: 4px;
    margin-bottom: 12px;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #080d1a; }
::-webkit-scrollbar-thumb { background: #1a3060; border-radius: 3px; }

.stSelectbox > div > div {
    background: #0d1830 !important;
    border-color: #1a3060 !important;
    color: #8aaad8 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "..", "data", "Taech_dev_cl.xlsx")
    df = pd.read_excel(DATA_PATH, sheet_name="Sheet1", header=None)
    df.columns = ["Ангилал", "Үзүүлэлт", "Он", "БУТ", "МКТ", "МСМТ", "НББТ",
                  "ОУАЖССИ", "ОУНББСМИ", "ОУС", "СДСТ", "СУТ", "СШУТ", "ЭкТ", "ЭнТИнс", "ЭЗТ", "Нийт"]
    df = df[df["Он"].notna()]
    df = df[df["Он"] != "Он"]
    df["Он"] = pd.to_numeric(df["Он"], errors="coerce").astype("Int64")
    df = df[df["Он"].notna()]
    DEPTS = ["БУТ", "МКТ", "МСМТ", "НББТ", "ОУАЖССИ", "ОУНББСМИ", "ОУС", "СДСТ", "СУТ", "СШУТ", "ЭкТ", "ЭнТИнс", "ЭЗТ"]
    for c in DEPTS + ["Нийт"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # Fix category trailing space
    df["Ангилал"] = df["Ангилал"].str.strip()
    return df, DEPTS

df, DEPTS = load_data()
CURRENT_YEAR = 2026
ALL_YEARS = sorted(df["Он"].dropna().unique())

# ============================================================
# HELPERS
# ============================================================
C = {
    "bg":     "#080e1c",
    "grid":   "#162040",
    "text":   "#8aaad8",
    "blue":   "#00d4ff",
    "green":  "#00e676",
    "purple": "#b388ff",
    "orange": "#ffab40",
    "pink":   "#ff80ab",
    "teal":   "#64ffda",
    "target": "#ff4da6",
    "white":  "#e0ecff",
}
DEPT_COLORS = ["#00d4ff","#00e676","#b388ff","#ffab40","#ff80ab","#64ffda",
               "#3a8aff","#ff9800","#f06292","#4fc3f7","#aed581","#ce93d8","#ffb74d"]

def theme(h=300):
    return dict(
        plot_bgcolor=C["bg"], paper_bgcolor=C["bg"],
        font=dict(color=C["text"], size=11),
        height=h, margin=dict(l=40, r=20, t=36, b=36),
        xaxis=dict(gridcolor=C["grid"], zerolinecolor=C["grid"]),
        yaxis=dict(gridcolor=C["grid"], zerolinecolor=C["grid"]),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["text"], size=10),
                    orientation="h", y=-0.18),
    )

def gv(cat, metric, year, dept):
    r = df[(df["Ангилал"]==cat)&(df["Үзүүлэлт"]==metric)&(df["Он"]==year)]
    return r.iloc[0][dept] if not r.empty else None

def gseries(cat, metric, dept):
    s = df[(df["Ангилал"]==cat)&(df["Үзүүлэлт"]==metric)].sort_values("Он")
    return list(s["Он"]), list(s[dept])

def fmt(v, pct=False):
    if v is None: return "—"
    if pct: return f"{v*100:.1f}%"
    return str(int(v))

def line_fig(title, yrs, vals, h=280, target_color=C["target"]):
    """Line chart: solid to CURRENT_YEAR, dotted after"""
    fig = go.Figure()
    hx = [y for y,v in zip(yrs,vals) if y<=CURRENT_YEAR and v is not None]
    hy = [v for y,v in zip(yrs,vals) if y<=CURRENT_YEAR and v is not None]
    fx = [y for y,v in zip(yrs,vals) if y>CURRENT_YEAR and v is not None]
    fy = [v for y,v in zip(yrs,vals) if y>CURRENT_YEAR and v is not None]

    fig.add_trace(go.Scatter(x=hx, y=hy, mode="lines+markers", name="Бодит",
        line=dict(color=C["blue"], width=2.5), marker=dict(size=7, color=C["blue"])))
    if fx and hx:
        fig.add_trace(go.Scatter(x=[hx[-1]]+fx, y=[hy[-1]]+fy, mode="lines+markers",
            name="Зорилт", line=dict(color=target_color, width=2, dash="dot"),
            marker=dict(size=7, color=target_color, symbol="diamond")))
    if CURRENT_YEAR in yrs:
        fig.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="rgba(255,255,255,0.2)",
                      annotation_text="2026", annotation_font_color="rgba(255,255,255,0.4)",
                      annotation_font_size=10)
    t = dict(**theme(h))
    t["title"] = dict(text=title, font=dict(color=C["white"], size=12))
    fig.update_layout(**t)
    return fig

def pct_line_fig(title, yrs, vals, h=260):
    fig = line_fig(title, yrs, [v for v in vals], h)
    fig.update_layout(yaxis=dict(tickformat=".0%", gridcolor=C["grid"]))
    return fig

def donut_fig(labels, values, title, h=300):
    clrs = DEPT_COLORS[:len(labels)]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=clrs, line=dict(color=C["bg"], width=2)),
        textinfo="label+percent", textfont=dict(color=C["text"], size=10),
        insidetextorientation="radial",
    ))
    t = dict(**theme(h))
    t["title"] = dict(text=title, font=dict(color=C["white"], size=12))
    t["showlegend"] = False
    fig.update_layout(**t)
    return fig

def bar_dept_fig(title, cat, metric, year, dept_col, h=280):
    vals = []
    for d in DEPTS:
        v = gv(cat, metric, year, d)
        vals.append(v if v is not None else 0)
    fig = go.Figure(go.Bar(
        x=DEPTS, y=vals,
        marker=dict(color=dept_col if isinstance(dept_col, list) else DEPT_COLORS,
                    line=dict(color=C["bg"], width=0.5)),
        text=[int(v) for v in vals], textposition="outside",
        textfont=dict(color=C["text"], size=10),
    ))
    t = dict(**theme(h))
    t["title"] = dict(text=title, font=dict(color=C["white"], size=12))
    t["xaxis"]["tickfont"] = dict(size=10)
    fig.update_layout(**t)
    return fig

def stacked_bar_fig(title, cat, metrics, labels, colors, year, h=300):
    fig = go.Figure()
    for m, lbl, clr in zip(metrics, labels, colors):
        row = df[(df["Ангилал"]==cat)&(df["Үзүүлэлт"]==m)&(df["Он"]==year)]
        vals = [row.iloc[0][d] if not row.empty else 0 for d in DEPTS]
        fig.add_trace(go.Bar(x=DEPTS, y=vals, name=lbl, marker_color=clr))
    t = dict(**theme(h))
    t["title"] = dict(text=title, font=dict(color=C["white"], size=12))
    t["barmode"] = "stack"
    t["xaxis"]["tickfont"] = dict(size=10)
    fig.update_layout(**t)
    return fig

def multi_line_fig(title, series_list, h=300):
    """series_list = [(label, yrs, vals, color), ...]"""
    fig = go.Figure()
    for lbl, yrs, vals, clr in series_list:
        hx = [y for y,v in zip(yrs,vals) if y<=CURRENT_YEAR and v is not None]
        hy = [v for y,v in zip(yrs,vals) if y<=CURRENT_YEAR and v is not None]
        fx = [y for y,v in zip(yrs,vals) if y>CURRENT_YEAR and v is not None]
        fy = [v for y,v in zip(yrs,vals) if y>CURRENT_YEAR and v is not None]
        fig.add_trace(go.Scatter(x=hx, y=hy, name=lbl, mode="lines+markers",
            line=dict(color=clr, width=2), marker=dict(size=5)))
        if fx and hx:
            fig.add_trace(go.Scatter(x=[hx[-1]]+fx, y=[hy[-1]]+fy, showlegend=False,
                mode="lines", line=dict(color=clr, dash="dot", width=1.5)))
    if CURRENT_YEAR in (yrs if series_list else []):
        fig.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="rgba(255,255,255,0.15)")
    t = dict(**theme(h))
    t["title"] = dict(text=title, font=dict(color=C["white"], size=12))
    fig.update_layout(**t)
    return fig

# ============================================================
# SIDEBAR — Department buttons
# ============================================================
with st.sidebar:
    st.markdown("### 🎓 СЭЗИС")
    st.markdown("---")
    st.markdown("<div style='color:#4a7acc;font-size:11px;font-weight:600;letter-spacing:1px;margin-bottom:8px;'>ТЭНХИМ СОНГОХ</div>", unsafe_allow_html=True)

    if "dept" not in st.session_state:
        st.session_state.dept = "Нийт"

    all_depts = ["Нийт"] + DEPTS
    dept_labels = {
        "Нийт": "🏛️ Нийт (бүх тэнхим)",
        "БУТ": "📐 БУТ", "МКТ": "💻 МКТ", "МСМТ": "📊 МСМТ",
        "НББТ": "💰 НББТ", "ОУАЖССИ": "🌐 ОУАЖССИ", "ОУНББСМИ": "🏦 ОУНББСМИ",
        "ОУС": "📚 ОУС", "СДСТ": "🔬 СДСТ", "СУТ": "⚙️ СУТ",
        "СШУТ": "🧮 СШУТ", "ЭкТ": "📈 ЭкТ", "ЭнТИнс": "🏢 ЭнТИнс", "ЭЗТ": "💹 ЭЗТ",
    }
    for d in all_depts:
        is_active = st.session_state.dept == d
        label = dept_labels.get(d, d)
        btn_style = "dept-active" if is_active else ""
        with st.container():
            if is_active:
                st.markdown(f"""<style>div[data-testid="stSidebar"] div:has(> div > button[kind="secondary"]:last-of-type) .stButton > button {{ background: linear-gradient(135deg,#1a3a7a,#2a4d9a) !important; color:#fff !important; border-color:#4a7acc !important; font-weight:600 !important; }}</style>""", unsafe_allow_html=True)
            if st.button(label, key=f"dept_{d}"):
                st.session_state.dept = d
                st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style='font-size:11px;color:#3a5a90;line-height:1.8;'>
    📌 <b style='color:#4a7acc'>2026</b> = Одоогийн жил<br>
    <span style='color:#ff4da6'>●</span> Тасархай = Зорилт<br>
    <span style='color:#00d4ff'>●</span> Суцлсан = Бодит утга
    </div>
    """, unsafe_allow_html=True)

D = st.session_state.dept  # selected dept

# ============================================================
# HEADER
# ============================================================
st.markdown(f"""
<div style='background:linear-gradient(90deg,#0d1f4a,#1a2d6b,#0d1f4a);
border:1px solid #1e3a8a;border-radius:14px;padding:16px 24px;margin-bottom:20px;'>
<span style='color:#fff;font-size:20px;font-weight:700;'>🎓 СЭЗИС — Багшийн хөгжлийн KPI Хяналтын Самбар</span><br>
<span style='color:#5a80b8;font-size:13px;'>Тэнхим: <b style='color:#00d4ff'>{dept_labels.get(D,D)}</b> &nbsp;|&nbsp; Одоогийн жил: <b style='color:#00d4ff'>2026</b></span>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SECTION 2 — ХУВИЙН KPI ҮЗҮҮЛЭЛТҮҮД (2026 он)
# ============================================================
st.markdown("<div class='section-title'>📈 2026 оны хувийн KPI үзүүлэлтүүд</div>", unsafe_allow_html=True)

pct_kpis = [
    ("Хувь", "Доктор зэрэгтэй багшийн эзлэх хувь",                     "🔬 Доктор %",          C["teal"]),
    ("Хувь", "Гадаад багшийн эзлэх хувь",                               "🌍 Гадаад %",           C["blue"]),
    ("Хувь", "Оюутны сэтгэл ханамжийн үнэлгээний дундаж хувь",         "😊 Оюутны сэтгэл ханамж", C["green"]),
    ("Хувь", "Багшийн сэтгэл ханамжийн үнэлгээний дундаж хувь",        "👩‍🏫 Багшийн сэтгэл ханамж", C["orange"]),
    ("Хувь", "Гадаад хэлээр заах чадвартай багшийн эзлэх хувь",        "🗣️ Гадаад хэл %",      C["purple"]),
    ("Хувь", "Солилцооны хөтөлбөрт хамрагдсан багшийн эзлэх хувь",    "🔄 Солилцоо %",         C["pink"]),
    ("Хувь", "Төсөл удирдсан багшийн эзлэх хувь",                      "📁 Төсөл %",            C["orange"]),
    ("Хувь", "Хамтарсан судалгаа, төсөлд оролцсон багшийн эзлэх хувь","🤝 Хамтарсан %",         C["teal"]),
    ("Хувь", "h-индекстэй багшийн эзлэх хувь",                         "📊 h-индекс %",         C["blue"]),
    ("Хувь", "WOS, Scopus-д өгүүлэл хэвлүүлсэн багшийн эзлэх хувь",  "📰 WOS/Scopus %",       C["purple"]),
]

pct_cols = st.columns(5)
for i, (cat, met, lbl, clr) in enumerate(pct_kpis):
    v = gv(cat, met, CURRENT_YEAR, D)
    pct_str = f"{v*100:.1f}%" if v is not None else "—"
    pct_cols[i % 5].markdown(f"""
    <div style='background:#0a1428;border:1px solid #162040;border-radius:10px;
    padding:12px 10px;text-align:center;margin-bottom:8px;
    border-top:2px solid {clr};'>
        <div style='color:{clr};font-size:20px;font-weight:700;'>{pct_str}</div>
        <div style='color:#4a6a98;font-size:10px;margin-top:3px;'>{lbl}</div>
    </div>""", unsafe_allow_html=True)

# ============================================================
# SECTION 3 — KPI ТРЕНДИЙН ГРАФИКУУД
# ============================================================
st.markdown("<div class='section-title'>📉 KPI Трендийн графикууд — Бодит ба Зорилт</div>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    # Нийт багшийн тоо trend
    yrs, vals = gseries("Багшийн тоо", "Нийт багшийн тоо", D)
    with st.container(border=True):
        st.plotly_chart(line_fig("Нийт багшийн тооны өөрчлөлт", yrs, vals), use_container_width=True)

    # Доктор хувь trend
    yrs2, vals2 = gseries("Хувь", "Доктор зэрэгтэй багшийн эзлэх хувь", D)
    fig2 = pct_line_fig("Доктор зэрэгтэй багшийн хувь", yrs2, vals2)
    with st.container(border=True):
        st.plotly_chart(fig2, use_container_width=True)

    # Сэтгэл ханамж
    yrs3, v3 = gseries("Хувь", "Оюутны сэтгэл ханамжийн үнэлгээний дундаж хувь", D)
    yrs4, v4 = gseries("Хувь", "Багшийн сэтгэл ханамжийн үнэлгээний дундаж хувь", D)
    fig3 = go.Figure()
    for lbl2, ylist, vlist, clr2 in [("Оюутны сэтгэл ханамж", yrs3, v3, C["green"]),
                                       ("Багшийн сэтгэл ханамж", yrs4, v4, C["orange"])]:
        hx = [y for y,v in zip(ylist,vlist) if y<=CURRENT_YEAR]
        hy = [v for y,v in zip(ylist,vlist) if y<=CURRENT_YEAR]
        fx = [y for y,v in zip(ylist,vlist) if y>CURRENT_YEAR]
        fy = [v for y,v in zip(ylist,vlist) if y>CURRENT_YEAR]
        fig3.add_trace(go.Scatter(x=hx, y=hy, name=lbl2, mode="lines+markers",
            line=dict(color=clr2, width=2), marker=dict(size=6)))
        if fx and hx:
            fig3.add_trace(go.Scatter(x=[hx[-1]]+fx, y=[hy[-1]]+fy, showlegend=False,
                mode="lines", line=dict(color=clr2, dash="dot", width=1.5)))
    t3 = dict(**theme(280))
    t3["title"] = dict(text="Сэтгэл ханамжийн үнэлгээ", font=dict(color=C["white"], size=12))
    t3["yaxis"]["tickformat"] = ".0%"
    fig3.update_layout(**t3)
    if CURRENT_YEAR in yrs3:
        fig3.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    with st.container(border=True):
        st.plotly_chart(fig3, use_container_width=True)

with col_b:
    # Боловсролын түвшин trend
    fig_edu = go.Figure()
    edu_items = [("Бакалавр", C["blue"]), ("Магистр", C["purple"]), ("Доктор", C["teal"])]
    for m, clr in edu_items:
        yrs_e, vals_e = gseries("Боловсролын түвшин", m, D)
        hx = [y for y,v in zip(yrs_e,vals_e) if y<=CURRENT_YEAR]
        hy = [v for y,v in zip(yrs_e,vals_e) if y<=CURRENT_YEAR]
        fx = [y for y,v in zip(yrs_e,vals_e) if y>CURRENT_YEAR]
        fy = [v for y,v in zip(yrs_e,vals_e) if y>CURRENT_YEAR]
        fig_edu.add_trace(go.Scatter(x=hx, y=hy, name=m, mode="lines+markers",
            line=dict(color=clr, width=2), marker=dict(size=6)))
        if fx and hx:
            fig_edu.add_trace(go.Scatter(x=[hx[-1]]+fx, y=[hy[-1]]+fy, showlegend=False,
                mode="lines", line=dict(color=clr, dash="dot", width=1.5)))
    t_edu = dict(**theme(260))
    t_edu["title"] = dict(text="Багшийн боловсролын түвшин", font=dict(color=C["white"], size=12))
    if CURRENT_YEAR in yrs_e:
        fig_edu.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig_edu.update_layout(**t_edu)
    with st.container(border=True):
        st.plotly_chart(fig_edu, use_container_width=True)

    # Зэрэглэл trend
    rank_trend = [
        ("Профессор",        C["orange"]),
        ("Дэд профессор",    C["purple"]),
        ("Ахлах багш",       C["blue"]),
        ("Багш",             C["green"]),
        ("Дадлагажигч багш", C["teal"]),
    ]
    fig_rk = go.Figure()
    for m, clr in rank_trend:
        yrs_r, vals_r = gseries("Зэрэглэл", m, D)
        hx = [y for y,v in zip(yrs_r,vals_r) if y<=CURRENT_YEAR]
        hy = [v for y,v in zip(yrs_r,vals_r) if y<=CURRENT_YEAR]
        fx = [y for y,v in zip(yrs_r,vals_r) if y>CURRENT_YEAR]
        fy = [v for y,v in zip(yrs_r,vals_r) if y>CURRENT_YEAR]
        fig_rk.add_trace(go.Scatter(x=hx, y=hy, name=m, mode="lines+markers",
            line=dict(color=clr, width=2), marker=dict(size=5)))
        if fx and hx:
            fig_rk.add_trace(go.Scatter(x=[hx[-1]]+fx, y=[hy[-1]]+fy, showlegend=False,
                mode="lines", line=dict(color=clr, dash="dot", width=1.5)))
    t_rk = dict(**theme(260))
    t_rk["title"] = dict(text="Багшийн зэрэглэл", font=dict(color=C["white"], size=12))
    if CURRENT_YEAR in yrs_r:
        fig_rk.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig_rk.update_layout(**t_rk)
    with st.container(border=True):
        st.plotly_chart(fig_rk, use_container_width=True)

    # Гадаад хэл / Солилцоо / Төсөл хувь trend
    pct_trends = [
        ("Гадаад хэлээр заах чадвартай багшийн эзлэх хувь", "Гадаад хэл", C["blue"]),
        ("Солилцооны хөтөлбөрт хамрагдсан багшийн эзлэх хувь", "Солилцооны хөтөлбөрт хамрагдсан", C["purple"]),
        ("Төсөл удирдсан багшийн эзлэх хувь", "Төсөл удирдсан багш", C["orange"]),
    ]
    fig_pt = go.Figure()
    for m, lbl, clr in pct_trends:
        yrs_pt, vals_pt = gseries("Хувь", m, D)
        hx = [y for y,v in zip(yrs_pt,vals_pt) if y<=CURRENT_YEAR]
        hy = [v for y,v in zip(yrs_pt,vals_pt) if y<=CURRENT_YEAR]
        fx = [y for y,v in zip(yrs_pt,vals_pt) if y>CURRENT_YEAR]
        fy = [v for y,v in zip(yrs_pt,vals_pt) if y>CURRENT_YEAR]
        fig_pt.add_trace(go.Scatter(x=hx, y=hy, name=lbl, mode="lines+markers",
            line=dict(color=clr, width=2), marker=dict(size=6)))
        if fx and hx:
            fig_pt.add_trace(go.Scatter(x=[hx[-1]]+fx, y=[hy[-1]]+fy, showlegend=False,
                mode="lines", line=dict(color=clr, dash="dot", width=1.5)))
    t_pt = dict(**theme(260))
    t_pt["title"] = dict(text="Гадаад хэл / Солилцоо / Төсөл (%)", font=dict(color=C["white"], size=12))
    t_pt["yaxis"]["tickformat"] = ".0%"
    if CURRENT_YEAR in yrs_pt:
        fig_pt.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig_pt.update_layout(**t_pt)
    with st.container(border=True):
        st.plotly_chart(fig_pt, use_container_width=True)
# ============================================================
# SECTION 4 — ТЭНХИМИЙН ХАРЬЦУУЛСАН ГРАФИКУУД
# ============================================================
st.markdown("<div class='section-title'>🏛️ Тэнхимийн харьцуулсан үзүүлэлтүүд (2026)</div>", unsafe_allow_html=True)

# Selectbox for which metric to show by dept
metric_options = {
    "Нийт багшийн тоо": ("Багшийн тоо", "Нийт багшийн тоо"),
    "Үндсэн багшийн тоо": ("Багшийн тоо", "Нийт үндсэн багшийн тоо"),
    "Гэрээт багшийн тоо": ("Багшийн тоо", "Нийт гэрээт багшийн тоо"),
    "Эмэгтэй багшийн тоо": ("Багшийн тоо", "Үндсэн эмэгтэй багшийн тоо"),
    "Доктор зэрэгтэй": ("Боловсролын түвшин", "Доктор"),
    "Магистр": ("Боловсролын түвшин", "Магистр"),
    "Профессор": ("Зэрэглэл", "Профессор"),
    "Ахлах багш": ("Зэрэглэл", "Ахлах багш"),
}

sel_metric = st.selectbox("Тэнхимээр харьцуулах үзүүлэлт сонгох:", list(metric_options.keys()))
sel_cat, sel_met = metric_options[sel_metric]
fig_dept_bar = bar_dept_fig(
    f"Тэнхим тус бүрийн {sel_metric} (2026)",
    sel_cat, sel_met, CURRENT_YEAR, DEPT_COLORS, h=320
)
st.plotly_chart(fig_dept_bar, use_container_width=True)

# ============================================================
# SECTION 5 — ДУГУЙ ДИАГРАМ (БҮРЭЛДЭХҮҮН)
# ============================================================
st.markdown("<div class='section-title'>🔵 Нийт бүрэлдэхүүний харьцаа (2026)</div>", unsafe_allow_html=True)

d_col1, d_col2, d_col3 = st.columns(3)

with d_col1:
    # Боловсролын түвшин donut
    edu_labels = ["Бакалавр", "Магистр", "Доктор"]
    edu_vals = [gv("Боловсролын түвшин", lv, CURRENT_YEAR, D) or 0 for lv in edu_labels]
    st.plotly_chart(donut_fig(edu_labels, edu_vals, "Боловсролын түвшин"), use_container_width=True)

with d_col2:
    # Зэрэглэл donut
    rank_labels = ["Дадлагажигч багш", "Багш", "Ахлах багш", "Дэд профессор", "Профессор"]
    rank_vals = [gv("Зэрэглэл", lv, CURRENT_YEAR, D) or 0 for lv in rank_labels]
    st.plotly_chart(donut_fig(rank_labels, rank_vals, "Зэрэглэлийн бүрэлдэхүүн"), use_container_width=True)

with d_col3:
    # Үндсэн vs Гэрээт
    comp_labels = ["Үндсэн багш", "Гэрээт багш"]
    comp_vals = [
        gv("Багшийн тоо", "Нийт үндсэн багшийн тоо", CURRENT_YEAR, D) or 0,
        gv("Багшийн тоо", "Нийт гэрээт багшийн тоо", CURRENT_YEAR, D) or 0,
    ]
    st.plotly_chart(donut_fig(comp_labels, comp_vals, "Үндсэн ба Гэрээт багш"), use_container_width=True)

# ============================================================
# SECTION 6 — НАСНЫ БҮЛЭГ & АЖИЛЛАСАН ЖИЛ
# ============================================================
st.markdown("<div class='section-title'>👥 Насны бүлэг ба Ажилласан жил (2026)</div>", unsafe_allow_html=True)

age_col, exp_col = st.columns(2)

with age_col:
    age_groups = ["25 хүртэл", "26-35", "36-45", "46-55", "56 ба түүнээс дээш"]
    age_vals = [gv("Насны бүлэг", ag, CURRENT_YEAR, D) or 0 for ag in age_groups]
    fig_age = go.Figure(go.Bar(
        x=age_vals, y=age_groups, orientation="h",
        marker=dict(color=DEPT_COLORS[:5]),
        text=age_vals, textposition="outside",
        textfont=dict(color=C["text"], size=10),
    ))
    t_age = dict(**theme(260))
    t_age["title"] = dict(text="Насны бүлгийн бүрэлдэхүүн", font=dict(color=C["white"], size=12))
    t_age["xaxis"]["title"] = "Тоо"
    t_age["margin"]["l"] = 120
    fig_age.update_layout(**t_age)
    st.plotly_chart(fig_age, use_container_width=True)

with exp_col:
    exp_groups = ["3 жил хүртэл", "4-6 жил", "Ажилласан жил - 7-9 жил", "10-15 жил", "16-20 жил", "21 ба түүнээс дээш"]
    exp_labels = ["≤3 жил", "4-6 жил", "7-9 жил", "10-15 жил", "16-20 жил", "21+ жил"]
    exp_vals = [gv("Ажилласан жил", eg, CURRENT_YEAR, D) or 0 for eg in exp_groups]
    fig_exp = go.Figure(go.Bar(
        x=exp_vals, y=exp_labels, orientation="h",
        marker=dict(color=DEPT_COLORS[2:8]),
        text=exp_vals, textposition="outside",
        textfont=dict(color=C["text"], size=10),
    ))
    t_exp = dict(**theme(260))
    t_exp["title"] = dict(text="Ажилласан жилийн бүрэлдэхүүн", font=dict(color=C["white"], size=12))
    t_exp["xaxis"]["title"] = "Тоо"
    t_exp["margin"]["l"] = 100
    fig_exp.update_layout(**t_exp)
    st.plotly_chart(fig_exp, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#162040;font-size:11px;padding:8px 0'>
СЭЗИС — Стратегийн KPI Хяналтын Систем | Багшийн хөгжил | 2026
</div>""", unsafe_allow_html=True)
