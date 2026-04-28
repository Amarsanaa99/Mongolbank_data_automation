import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(
    page_title="СЭЗИС — Стратегийн KPI",
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
.stApp { background: #0a0f1e; color: #c8d8f0; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080d1a 0%, #0a1228 100%);
    border-right: 1px solid #162040;
}
[data-testid="stSidebar"] * { color: #8aaad8 !important; }

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
.kpi-blue::before   { background: linear-gradient(90deg, #00c8ff, #0080ff); }
.kpi-green::before  { background: linear-gradient(90deg, #00e676, #00b248); }
.kpi-purple::before { background: linear-gradient(90deg, #b388ff, #7c4dff); }
.kpi-orange::before { background: linear-gradient(90deg, #ffab40, #ff6d00); }
.kpi-pink::before   { background: linear-gradient(90deg, #ff80ab, #f50057); }
.kpi-teal::before   { background: linear-gradient(90deg, #64ffda, #00bfa5); }

.kpi-icon { font-size: 20px; margin-bottom: 6px; }
.kpi-num  { font-size: 34px; font-weight: 700; line-height: 1; margin-bottom: 4px; }
.kpi-num-blue   { color: #00d4ff; }
.kpi-num-green  { color: #00e676; }
.kpi-num-purple { color: #b388ff; }
.kpi-num-orange { color: #ffab40; }
.kpi-num-pink   { color: #ff80ab; }
.kpi-num-teal   { color: #64ffda; }
.kpi-label { color: #6080a8; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }

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
# DATA LOADING — Багшийн хөгжил
# ============================================================
@st.cache_data
def load_teacher_data():
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
    df["Ангилал"] = df["Ангилал"].ffill()
    df["Үзүүлэлт"] = df["Үзүүлэлт"].ffill()
    df["Ангилал"] = df["Ангилал"].str.strip()
    return df, DEPTS

# ============================================================
# DATA LOADING — Хөтөлбөр хөгжил
# ============================================================
@st.cache_data
def load_prog_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "..", "data", "sub_dev_cl.xlsx")
    df = pd.read_excel(DATA_PATH, sheet_name="Sheet1", header=None)
    df.columns = ["Ангилал", "Үзүүлэлт", "Он", "БУТ", "МКТ", "МСМТ", "НББТ",
                  "ОУАЖССИ", "ОУНББСМИ", "ОУС", "СДСТ", "СУТ", "СШУТ", "ЭкТ", "ЭнТИнс", "ЭЗТ", "Нийт"]
    df = df[df["Он"].notna()]
    df = df[df["Он"] != "Он"]
    df["Ангилал"] = df["Ангилал"].ffill()
    df["Үзүүлэлт"] = df["Үзүүлэлт"].ffill()
    df["Он"] = pd.to_numeric(df["Он"], errors="coerce").astype("Int64")
    df = df[df["Он"].notna()]
    DEPTS = ["БУТ", "МКТ", "МСМТ", "НББТ", "ОУАЖССИ", "ОУНББСМИ", "ОУС", "СДСТ", "СУТ", "СШУТ", "ЭкТ", "ЭнТИнс", "ЭЗТ"]
    for c in DEPTS + ["Нийт"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["Ангилал"] = df["Ангилал"].str.strip()
    return df, DEPTS

# ============================================================
# DATA LOADING — Суралцагч хөгжил
# ============================================================
@st.cache_data
def load_stud_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "..", "data", "stud_dev_cl.xlsx")
    df = pd.read_excel(DATA_PATH, sheet_name="Sheet1", header=None)
    df.columns = ["Ангилал", "Үзүүлэлт", "Он", "БУТ", "МКТ", "МСМТ", "НББТ",
                  "ОУАЖССИ", "ОУНББСМИ", "ОУС", "СДСТ", "СУТ", "СШУТ", "ЭкТ", "ЭнТИнс", "ЭЗТ", "Нийт"]
    df = df[df["Он"].notna()]
    df = df[df["Он"] != "Он"]
    df["Ангилал"] = df["Ангилал"].ffill()
    df["Үзүүлэлт"] = df["Үзүүлэлт"].ffill()
    df["Он"] = pd.to_numeric(df["Он"], errors="coerce").astype("Int64")
    df = df[df["Он"].notna()]
    DEPTS = ["БУТ", "МКТ", "МСМТ", "НББТ", "ОУАЖССИ", "ОУНББСМИ", "ОУС", "СДСТ", "СУТ", "СШУТ", "ЭкТ", "ЭнТИнс", "ЭЗТ"]
    for c in DEPTS + ["Нийт"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["Ангилал"] = df["Ангилал"].str.strip()
    df["Үзүүлэлт"] = df["Үзүүлэлт"].str.strip()
    return df, DEPTS

df, DEPTS       = load_teacher_data()
dfp, DEPTS_P    = load_prog_data()
dfs, DEPTS_S    = load_stud_data()

CURRENT_YEAR = 2026

# ============================================================
# HELPERS
# ============================================================
C = {
    "bg": "#080e1c", "grid": "#162040", "text": "#8aaad8",
    "blue": "#00d4ff", "green": "#00e676", "purple": "#b388ff",
    "orange": "#ffab40", "pink": "#ff80ab", "teal": "#64ffda",
    "target": "#ff4da6", "white": "#e0ecff",
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

def gv(cat, metric, year, dept, src="teacher"):
    d = df if src == "teacher" else dfp
    r = d[(d["Ангилал"]==cat)&(d["Үзүүлэлт"]==metric)&(d["Он"]==year)]
    return r.iloc[0][dept] if not r.empty else None

def gseries(cat, metric, dept, src="teacher"):
    d = df if src == "teacher" else dfp
    s = d[(d["Ангилал"]==cat)&(d["Үзүүлэлт"]==metric)].sort_values("Он")
    return list(s["Он"]), list(s[dept])

def sv(metric, year, dept):
    """Get value from stud data"""
    r = dfs[(dfs["Үзүүлэлт"]==metric)&(dfs["Он"]==year)]
    return r.iloc[0][dept] if not r.empty else None

def sseries(metric, dept):
    """Get series from stud data"""
    s = dfs[dfs["Үзүүлэлт"]==metric].sort_values("Он")
    return list(s["Он"]), list(s[dept])

def line_fig(title, yrs, vals, h=280, target_color=C["target"]):
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

def pct_line_fig(title, yrs, vals, h=280):
    fig = line_fig(title, yrs, vals, h)
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

def stacked_bar_fig(title, cat, metrics, labels, colors, year, h=300, src="teacher"):
    d = df if src == "teacher" else dfp
    fig = go.Figure()
    for m, lbl, clr in zip(metrics, labels, colors):
        row = d[(d["Ангилал"]==cat)&(d["Үзүүлэлт"]==m)&(d["Он"]==year)]
        vals = [row.iloc[0][dep] if not row.empty else 0 for dep in DEPTS]
        fig.add_trace(go.Bar(x=DEPTS, y=vals, name=lbl, marker_color=clr))
    t = dict(**theme(h))
    t["title"] = dict(text=title, font=dict(color=C["white"], size=12))
    t["barmode"] = "stack"
    t["xaxis"]["tickfont"] = dict(size=10)
    fig.update_layout(**t)
    return fig

# ============================================================
# SESSION STATE
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "teacher"
if "dept" not in st.session_state:
    st.session_state.dept = "Нийт"

# ============================================================
# SIDEBAR
# ============================================================
dept_labels = {
    "Нийт": "🏛️ UFE",
    "БУТ": "📐 БУТ", "МКТ": "💻 МКТ", "МСМТ": "📊 МСМТ",
    "НББТ": "💰 НББТ", "ОУАЖССИ": "🌐 ОУАЖССИ", "ОУНББСМИ": "🏦 ОУНББСМИ",
    "ОУС": "📚 ОУС", "СДСТ": "🔬 СДСТ", "СУТ": "⚙️ СУТ",
    "СШУТ": "🧮 СШУТ", "ЭкТ": "📈 ЭкТ", "ЭнТИнс": "🏢 ЭнТИнс", "ЭЗТ": "💹 ЭЗТ",
}

with st.sidebar:
    st.markdown("""
<div style='color:#fff;font-size:15px;font-weight:700;margin:0 0 4px 0;'>🎓 СЭЗИС</div>
<div style='border-bottom:1px solid #1a3060;margin-bottom:6px;'></div>
<div style='color:#4a7acc;font-size:11px;font-weight:600;letter-spacing:1px;margin-bottom:6px;'>ТЭНХИМ СОНГОХ</div>
""", unsafe_allow_html=True)

    all_depts = ["Нийт"] + DEPTS
    for d in all_depts:
        label = dept_labels.get(d, d)
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

D = st.session_state.dept

# ============================================================
# HEADER — page navigation tabs
# ============================================================
col_h1, col_h2, col_h3, col_h4 = st.columns([3, 1, 1, 1])
with col_h1:
    st.markdown(f"""
<div style='background:linear-gradient(90deg,#0d1f4a,#1a2d6b,#0d1f4a);
border:1px solid #1e3a8a;border-radius:14px;padding:12px 20px;'>
<span style='color:#fff;font-size:17px;font-weight:700;'>🎓 СЭЗИС — Стратегийн KPI Хяналтын Самбар</span><br>
<span style='color:#5a80b8;font-size:12px;'>Тэнхим: <b style='color:#00d4ff'>{dept_labels.get(D,D)}</b> &nbsp;|&nbsp; Одоогийн жил: <b style='color:#00d4ff'>2026</b></span>
</div>
""", unsafe_allow_html=True)

with col_h2:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    is_teacher = st.session_state.page == "teacher"
    if st.button("👩‍🏫 Багшийн хөгжил",
                 key="nav_teacher",
                 type="primary" if is_teacher else "secondary"):
        st.session_state.page = "teacher"
        st.rerun()

with col_h3:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    is_prog = st.session_state.page == "prog"
    if st.button("📚 Хөтөлбөр хөгжил",
                 key="nav_prog",
                 type="primary" if is_prog else "secondary"):
        st.session_state.page = "prog"
        st.rerun()

with col_h4:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    is_stud = st.session_state.page == "stud"
    if st.button("🎓 Хичээл, Сургалт",
                 key="nav_stud",
                 type="primary" if is_stud else "secondary"):
        st.session_state.page = "stud"
        st.rerun()

st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

# ============================================================
# PAGE 1 — БАГШИЙН ХӨГЖИЛ
# ============================================================
if st.session_state.page == "teacher":

    st.markdown("<div class='section-title'>📈 2026 оны хувийн KPI үзүүлэлтүүд</div>", unsafe_allow_html=True)
    pct_kpis = [
        ("Хувь", "Доктор зэрэгтэй багшийн эзлэх хувь",                     "🔬 Доктор %",             C["teal"]),
        ("Хувь", "Гадаад багшийн эзлэх хувь",                               "🌍 Гадаад %",              C["blue"]),
        ("Хувь", "Оюутны сэтгэл ханамжийн үнэлгээний дундаж хувь",         "😊 Оюутны сэтгэл ханамж",  C["green"]),
        ("Хувь", "Багшийн сэтгэл ханамжийн үнэлгээний дундаж хувь",        "👩‍🏫 Багшийн сэтгэл ханамж", C["orange"]),
        ("Хувь", "Гадаад хэлээр заах чадвартай багшийн эзлэх хувь",        "🗣️ Гадаад хэл %",         C["purple"]),
        ("Хувь", "Солилцооны хөтөлбөрт хамрагдсан багшийн эзлэх хувь",    "🔄 Солилцоо %",            C["pink"]),
        ("Хувь", "Төсөл удирдсан багшийн эзлэх хувь",                      "📁 Төсөл %",               C["orange"]),
        ("Хувь", "Хамтарсан судалгаа, төсөлд оролцсон багшийн эзлэх хувь","🤝 Хамтарсан %",            C["teal"]),
        ("Хувь", "h-индекстэй багшийн эзлэх хувь",                         "📊 h-индекс %",            C["blue"]),
        ("Хувь", "WOS, Scopus-д өгүүлэл хэвлүүлсэн багшийн эзлэх хувь",  "📰 WOS/Scopus %",          C["purple"]),
    ]
    pct_cols = st.columns(5)
    for i, (cat, met, lbl, clr) in enumerate(pct_kpis):
        v = gv(cat, met, CURRENT_YEAR, D)
        pct_str = f"{v*100:.1f}%" if v is not None else "—"
        pct_cols[i % 5].markdown(f"""
<div style='background:#0a1428;border:1px solid #162040;border-radius:10px;
padding:12px 10px;text-align:center;margin-bottom:8px;border-top:2px solid {clr};'>
    <div style='color:{clr};font-size:20px;font-weight:700;'>{pct_str}</div>
    <div style='color:#4a6a98;font-size:10px;margin-top:3px;'>{lbl}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>📉 KPI Трендийн графикууд — Бодит ба Зорилт</div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        yrs, vals = gseries("Багшийн тоо", "Нийт багшийн тоо", D)
        with st.container(border=True):
            st.plotly_chart(line_fig("Нийт багшийн тооны өөрчлөлт", yrs, vals, h=280), use_container_width=True)

        yrs2, vals2 = gseries("Хувь", "Доктор зэрэгтэй багшийн эзлэх хувь", D)
        with st.container(border=True):
            st.plotly_chart(pct_line_fig("Доктор зэрэгтэй багшийн хувь", yrs2, vals2, h=280), use_container_width=True)

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
        fig_edu = go.Figure()
        for m, clr in [("Бакалавр", C["blue"]), ("Магистр", C["purple"]), ("Доктор", C["teal"])]:
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
        t_edu = dict(**theme(280))
        t_edu["title"] = dict(text="Багшийн боловсролын түвшин", font=dict(color=C["white"], size=12))
        if CURRENT_YEAR in yrs_e:
            fig_edu.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="rgba(255,255,255,0.2)")
        fig_edu.update_layout(**t_edu)
        with st.container(border=True):
            st.plotly_chart(fig_edu, use_container_width=True)

        fig_rk = go.Figure()
        for m, clr in [("Профессор",C["orange"]),("Дэд профессор",C["purple"]),
                       ("Ахлах багш",C["blue"]),("Багш",C["green"]),("Дадлагажигч багш",C["teal"])]:
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
        t_rk = dict(**theme(280))
        t_rk["title"] = dict(text="Багшийн зэрэглэл", font=dict(color=C["white"], size=12))
        if CURRENT_YEAR in yrs_r:
            fig_rk.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="rgba(255,255,255,0.2)")
        fig_rk.update_layout(**t_rk)
        with st.container(border=True):
            st.plotly_chart(fig_rk, use_container_width=True)

        fig_pt = go.Figure()
        for m, lbl, clr in [
            ("Гадаад хэлээр заах чадвартай багшийн эзлэх хувь", "Гадаад хэл", C["blue"]),
            ("Солилцооны хөтөлбөрт хамрагдсан багшийн эзлэх хувь", "Солилцооны хөтөлбөрт хамрагдсан", C["purple"]),
            ("Төсөл удирдсан багшийн эзлэх хувь", "Төсөл удирдсан багш", C["orange"]),
        ]:
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
        t_pt = dict(**theme(280))
        t_pt["title"] = dict(text="Гадаад хэл / Солилцоо / Төсөл (%)", font=dict(color=C["white"], size=12))
        t_pt["yaxis"]["tickformat"] = ".0%"
        if CURRENT_YEAR in yrs_pt:
            fig_pt.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="rgba(255,255,255,0.2)")
        fig_pt.update_layout(**t_pt)
        with st.container(border=True):
            st.plotly_chart(fig_pt, use_container_width=True)

    st.markdown("<div class='section-title'>🏛️ Тэнхимийн харьцуулсан үзүүлэлтүүд (2026)</div>", unsafe_allow_html=True)
    metric_options = {
        "Доктор зэрэгтэй багшийн хувь":  ("Хувь", "Доктор зэрэгтэй багшийн эзлэх хувь", True),
        "Гадаад багшийн хувь":            ("Хувь", "Гадаад багшийн эзлэх хувь", True),
        "Оюутны сэтгэл ханамж":           ("Хувь", "Оюутны сэтгэл ханамжийн үнэлгээний дундаж хувь", True),
        "Багшийн сэтгэл ханамж":          ("Хувь", "Багшийн сэтгэл ханамжийн үнэлгээний дундаж хувь", True),
        "Гадаад хэлээр заах чадвар":      ("Хувь", "Гадаад хэлээр заах чадвартай багшийн эзлэх хувь", True),
        "Солилцооны хөтөлбөр":            ("Хувь", "Солилцооны хөтөлбөрт хамрагдсан багшийн эзлэх хувь", True),
        "Төсөл удирдсан багшийн хувь":    ("Хувь", "Төсөл удирдсан багшийн эзлэх хувь", True),
        "Хамтарсан судалгааны хувь":      ("Хувь", "Хамтарсан судалгаа, төсөлд оролцсон багшийн эзлэх хувь", True),
        "h-индекстэй багшийн хувь":       ("Хувь", "h-индекстэй багшийн эзлэх хувь", True),
        "WOS/Scopus өгүүлэл":             ("Хувь", "WOS, Scopus-д өгүүлэл хэвлүүлсэн багшийн эзлэх хувь", True),
    }
    sel_metric = st.selectbox("Тэнхимээр харьцуулах үзүүлэлт сонгох:", list(metric_options.keys()))
    sel_cat, sel_met, is_pct = metric_options[sel_metric]
    vals_dept = []
    for d in DEPTS:
        v = gv(sel_cat, sel_met, CURRENT_YEAR, d)
        vals_dept.append(round(v * 100, 1) if v is not None and is_pct else (v if v is not None else 0))
    text_vals = [f"{v}%" if is_pct else str(int(v)) for v in vals_dept]
    fig_dept_bar = go.Figure(go.Bar(
        x=DEPTS, y=vals_dept,
        marker=dict(color=DEPT_COLORS, line=dict(color=C["bg"], width=0.5)),
        text=text_vals, textposition="outside", textfont=dict(color=C["text"], size=10),
    ))
    t_bar = dict(**theme(340))
    t_bar["title"] = dict(text=f"Тэнхим тус бүрийн {sel_metric} (2026){' (%)' if is_pct else ''}",
                          font=dict(color=C["white"], size=12))
    t_bar["xaxis"]["tickfont"] = dict(size=10)
    if is_pct:
        t_bar["yaxis"]["ticksuffix"] = "%"
    fig_dept_bar.update_layout(**t_bar)
    avg_val = round(sum(v for v in vals_dept if v > 0) / max(len([v for v in vals_dept if v > 0]), 1), 1)
    fig_dept_bar.add_hline(y=avg_val, line_dash="dash", line_color="#ff4d4d", line_width=1.5,
        annotation_text=f"Дундаж: {avg_val}{'%' if is_pct else ''}",
        annotation_position="top right", annotation_font=dict(color="#ff4d4d", size=11))
    with st.container(border=True):
        st.plotly_chart(fig_dept_bar, use_container_width=True)

    st.markdown("<div class='section-title'>🔵 Нийт бүрэлдэхүүний харьцаа (2026)</div>", unsafe_allow_html=True)
    d_col1, d_col2, d_col3 = st.columns(3)
    with d_col1:
        edu_labels = ["Бакалавр", "Магистр", "Доктор"]
        edu_vals = [gv("Боловсролын түвшин", lv, CURRENT_YEAR, D) or 0 for lv in edu_labels]
        st.plotly_chart(donut_fig(edu_labels, edu_vals, "Боловсролын түвшин"), use_container_width=True)
    with d_col2:
        rank_labels = ["Дадлагажигч багш", "Багш", "Ахлах багш", "Дэд профессор", "Профессор"]
        rank_vals = [gv("Зэрэглэл", lv, CURRENT_YEAR, D) or 0 for lv in rank_labels]
        st.plotly_chart(donut_fig(rank_labels, rank_vals, "Зэрэглэлийн бүрэлдэхүүн"), use_container_width=True)
    with d_col3:
        comp_labels = ["Үндсэн багш", "Гэрээт багш"]
        comp_vals = [
            gv("Багшийн тоо", "Нийт үндсэн багшийн тоо", CURRENT_YEAR, D) or 0,
            gv("Багшийн тоо", "Нийт гэрээт багшийн тоо", CURRENT_YEAR, D) or 0,
        ]
        st.plotly_chart(donut_fig(comp_labels, comp_vals, "Үндсэн ба Гэрээт багш"), use_container_width=True)

    st.markdown("<div class='section-title'>👥 Насны бүлэг ба Ажилласан жил (2026)</div>", unsafe_allow_html=True)
    age_col, exp_col = st.columns(2)
    with age_col:
        age_groups = ["25 хүртэл", "26-35", "36-45", "46-55", "56 ба түүнээс дээш"]
        age_vals = [gv("Насны бүлэг", ag, CURRENT_YEAR, D) or 0 for ag in age_groups]
        fig_age = go.Figure(go.Bar(x=age_vals, y=age_groups, orientation="h",
            marker=dict(color=DEPT_COLORS[:5]), text=age_vals, textposition="outside",
            textfont=dict(color=C["text"], size=10)))
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
        fig_exp = go.Figure(go.Bar(x=exp_vals, y=exp_labels, orientation="h",
            marker=dict(color=DEPT_COLORS[2:8]), text=exp_vals, textposition="outside",
            textfont=dict(color=C["text"], size=10)))
        t_exp = dict(**theme(260))
        t_exp["title"] = dict(text="Ажилласан жилийн бүрэлдэхүүн", font=dict(color=C["white"], size=12))
        t_exp["xaxis"]["title"] = "Тоо"
        t_exp["margin"]["l"] = 100
        fig_exp.update_layout(**t_exp)
        st.plotly_chart(fig_exp, use_container_width=True)

# ============================================================
# PAGE 2 — ХӨТӨЛБӨР ХӨГЖИЛ
# ============================================================
elif st.session_state.page == "prog":

    def pgv(metric, year, dept):
        r = dfp[(dfp["Үзүүлэлт"]==metric)&(dfp["Он"]==year)]
        return r.iloc[0][dept] if not r.empty else None

    def pgseries(metric, dept):
        s = dfp[dfp["Үзүүлэлт"]==metric].sort_values("Он")
        return list(s["Он"]), list(s[dept])

    st.markdown("<div class='section-title'>📊 2026 оны үндсэн үзүүлэлтүүд</div>", unsafe_allow_html=True)

    count_kpis = [
        ("Хэрэгжүүлж буй үндсэн хөтөлбөрийн тоо",          "📋 Үндсэн хөтөлбөр",       C["blue"]),
        ("Цахимаар хэрэгжиж буй хөтөлбөрийн тоо",           "💻 Цахим хөтөлбөр",         C["teal"]),
        ("Цагийн хөтөлбөрийн тоо",                           "⏱ Цагийн хөтөлбөр",         C["purple"]),
        ("Гадаад хэлээр явуулах хөтөлбөрийн тоо",           "🌐 Гадаад хэлний хөтөлбөр", C["green"]),
        ("Хамтарсан хөтөлбөрийн тоо",                        "🤝 Хамтарсан хөтөлбөр",     C["orange"]),
        ("ОУ дипломтой хөтөлбөрийн тоо",                    "🎓 ОУ диплом",               C["pink"]),
        ("Интерактив хөтөлбөрийн тоо",                       "🔬 Интерактив",              C["teal"]),
        ("Ажлын байранд суурилсан хөтөлбөрийн тоо",         "🏭 Ажлын байранд суурилсан", C["blue"]),
        ("Хамтын ажиллагааны гэрээтэй байгууллагын тоо",    "📝 Гэрээт байгуулага",       C["purple"]),
        ("Хүлээн зөвшөөрөгдсөн ОУ мэргэжлийн байгууллагын тоо", "✅ ОУ мэргэжлийн байгуулага", C["green"]),
    ]
    kpi_cols = st.columns(5)
    for i, (met, lbl, clr) in enumerate(count_kpis):
        v = pgv(met, CURRENT_YEAR, D)
        val_str = str(int(v)) if v is not None else "—"
        kpi_cols[i % 5].markdown(f"""
<div style='background:#0a1428;border:1px solid #162040;border-radius:10px;
padding:12px 10px;text-align:center;margin-bottom:8px;border-top:2px solid {clr};'>
    <div style='color:{clr};font-size:24px;font-weight:700;'>{val_str}</div>
    <div style='color:#4a6a98;font-size:10px;margin-top:3px;'>{lbl}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>📈 2026 оны хувийн KPI үзүүлэлтүүд</div>", unsafe_allow_html=True)

    pct_kpis_p = [
        ("ОУ-д магадлан итгэмжлэгдсэн хөтөлбөрийн хувь",                    "🌍 ОУ магадлан %",      C["blue"]),
        ("Үндэсний хэмжээнд магадлан итгэмжлэгдсэн хөтөлбөрийн хувь",       "🏛️ Үндэсний магадлан %", C["teal"]),
        ("Цахимаар хэрэгжиж буй хөтөлбөрийн нийт хөтөлбөрт эзлэх хувь",    "💻 Цахим %",             C["purple"]),
        ("СҮД хурлаас гарсан санал хүсэлтийн шийдвэрлэлтийн хувь",          "✅ СҮД шийдвэрлэлт %",   C["green"]),
    ]
    pct_p_cols = st.columns(4)
    for i, (met, lbl, clr) in enumerate(pct_kpis_p):
        v = pgv(met, CURRENT_YEAR, D)
        val_str = f"{v*100:.1f}%" if v is not None else "—"
        pct_p_cols[i].markdown(f"""
<div style='background:#0a1428;border:1px solid #162040;border-radius:10px;
padding:14px 12px;text-align:center;margin-bottom:8px;border-top:2px solid {clr};'>
    <div style='color:{clr};font-size:22px;font-weight:700;'>{val_str}</div>
    <div style='color:#4a6a98;font-size:10px;margin-top:3px;'>{lbl}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>📉 Хувийн KPI трендийн графикууд — Бодит ба Зорилт</div>", unsafe_allow_html=True)

    pct_trend_metrics = [
        ("ОУ-д магадлан итгэмжлэгдсэн хөтөлбөрийн хувь",                 "ОУ магадлан итгэмжлэлт %",    C["blue"]),
        ("Үндэсний хэмжээнд магадлан итгэмжлэгдсэн хөтөлбөрийн хувь",    "Үндэсний магадлан итгэмжлэлт %", C["teal"]),
        ("Цахимаар хэрэгжиж буй хөтөлбөрийн нийт хөтөлбөрт эзлэх хувь", "Цахим хөтөлбөрийн %",         C["purple"]),
        ("СҮД хурлаас гарсан санал хүсэлтийн шийдвэрлэлтийн хувь",       "СҮД шийдвэрлэлт %",           C["green"]),
    ]

    pc1, pc2 = st.columns(2)
    cols_cycle = [pc1, pc2, pc1, pc2]
    for i, (met, lbl, clr) in enumerate(pct_trend_metrics):
        yrs_p, vals_p = pgseries(met, D)
        fig_p = go.Figure()
        hx = [y for y,v in zip(yrs_p,vals_p) if y<=CURRENT_YEAR and v is not None]
        hy = [v for y,v in zip(yrs_p,vals_p) if y<=CURRENT_YEAR and v is not None]
        fx = [y for y,v in zip(yrs_p,vals_p) if y>CURRENT_YEAR and v is not None]
        fy = [v for y,v in zip(yrs_p,vals_p) if y>CURRENT_YEAR and v is not None]
        fig_p.add_trace(go.Scatter(x=hx, y=hy, mode="lines+markers", name="Бодит",
            line=dict(color=clr, width=2.5), marker=dict(size=7, color=clr)))
        if fx and hx:
            fig_p.add_trace(go.Scatter(x=[hx[-1]]+fx, y=[hy[-1]]+fy, mode="lines+markers",
                name="Зорилт", line=dict(color=C["target"], width=2, dash="dot"),
                marker=dict(size=7, color=C["target"], symbol="diamond")))
        if CURRENT_YEAR in yrs_p:
            fig_p.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="rgba(255,255,255,0.2)",
                annotation_text="2026", annotation_font_color="rgba(255,255,255,0.4)", annotation_font_size=10)
        tp = dict(**theme(280))
        tp["title"] = dict(text=lbl, font=dict(color=C["white"], size=12))
        tp["yaxis"]["tickformat"] = ".0%"
        fig_p.update_layout(**tp)
        with cols_cycle[i]:
            with st.container(border=True):
                st.plotly_chart(fig_p, use_container_width=True)

    st.markdown("<div class='section-title'>🏛️ Тэнхимийн харьцуулсан үзүүлэлтүүд (2026)</div>", unsafe_allow_html=True)

    prog_dept_opts = {
        "Үндсэн хөтөлбөрийн тоо":         "Хэрэгжүүлж буй үндсэн хөтөлбөрийн тоо",
        "Цахим хөтөлбөрийн тоо":           "Цахимаар хэрэгжиж буй хөтөлбөрийн тоо",
        "Цагийн хөтөлбөрийн тоо":          "Цагийн хөтөлбөрийн тоо",
        "Гадаад хэлний хөтөлбөр":          "Гадаад хэлээр явуулах хөтөлбөрийн тоо",
        "Хамтарсан хөтөлбөр":              "Хамтарсан хөтөлбөрийн тоо",
        "ОУ дипломтой хөтөлбөр":           "ОУ дипломтой хөтөлбөрийн тоо",
        "Интерактив хөтөлбөр":             "Интерактив хөтөлбөрийн тоо",
        "Ажлын байранд суурилсан хөтөлбөр":"Ажлын байранд суурилсан хөтөлбөрийн тоо",
        "Гэрээт байгуулага":               "Хамтын ажиллагааны гэрээтэй байгууллагын тоо",
        "Ажиглалтад хамрагдсан хичээл":    "Ажиглалтад хамрагдсан хичээлийн тоо",
        "СҮД хэлэлцүүлсэн хичээл":        "Хичээлийн СҮД хурлаар хэлэлцүүлсэн хичээлийн тоо",
    }

    sel_p = st.selectbox("Тэнхимээр харьцуулах үзүүлэлт:", list(prog_dept_opts.keys()), key="prog_dept_sel")
    sel_met_p = prog_dept_opts[sel_p]

    vals_dp = []
    for d in DEPTS:
        v = pgv(sel_met_p, CURRENT_YEAR, d)
        vals_dp.append(int(v) if v is not None else 0)

    avg_dp = round(sum(vals_dp) / max(len([v for v in vals_dp if v > 0]), 1), 1)
    fig_dp = go.Figure(go.Bar(
        x=DEPTS, y=vals_dp,
        marker=dict(color=DEPT_COLORS, line=dict(color=C["bg"], width=0.5)),
        text=[str(v) for v in vals_dp], textposition="outside",
        textfont=dict(color=C["text"], size=10),
    ))
    t_dp = dict(**theme(340))
    t_dp["title"] = dict(text=f"Тэнхим тус бүрийн {sel_p} (2026)", font=dict(color=C["white"], size=12))
    t_dp["xaxis"]["tickfont"] = dict(size=10)
    fig_dp.update_layout(**t_dp)
    fig_dp.add_hline(y=avg_dp, line_dash="dash", line_color="#ff4d4d", line_width=1.5,
        annotation_text=f"Дундаж: {avg_dp}",
        annotation_position="top right", annotation_font=dict(color="#ff4d4d", size=11))
    with st.container(border=True):
        st.plotly_chart(fig_dp, use_container_width=True)

    st.markdown("<div class='section-title'>📊 Тоон үзүүлэлтүүдийн өөрчлөлт</div>", unsafe_allow_html=True)

    count_trend_groups = [
        [
            ("Хэрэгжүүлж буй үндсэн хөтөлбөрийн тоо",    "Үндсэн хөтөлбөр",    C["blue"]),
            ("Цахимаар хэрэгжиж буй хөтөлбөрийн тоо",    "Цахим хөтөлбөр",     C["teal"]),
            ("Цагийн хөтөлбөрийн тоо",                    "Цагийн хөтөлбөр",    C["purple"]),
        ],
        [
            ("Гадаад хэлээр явуулах хөтөлбөрийн тоо",    "Гадаад хэлний",       C["green"]),
            ("Хамтарсан хөтөлбөрийн тоо",                "Хамтарсан хөтөлбөр", C["orange"]),
            ("ОУ дипломтой хөтөлбөрийн тоо",             "ОУ диплом",           C["pink"]),
        ],
        [
            ("Ажиглалтад хамрагдсан хичээлийн тоо",       "Ажиглалтад хамрагдсан", C["blue"]),
            ("Хичээлийн СҮД хурлаар хэлэлцүүлсэн хичээлийн тоо", "СҮД хэлэлцүүлсэн", C["orange"]),
            ("СҮД хурлаас гарсан санал, хүсэлтийн тоо",  "СҮД санал хүсэлт",   C["teal"]),
        ],
        [
            ("Хамтын ажиллагааны гэрээтэй байгууллагын тоо",       "Гэрээт байгуулага",     C["purple"]),
            ("Хамтарсан хөтөлбөр хэрэгжүүлэгч сургуулийн тоо",   "Хамтарсан сургууль",    C["green"]),
            ("Солилцооны хөтөлбөр хэрэгжүүлэгч институтийн тоо", "Солилцооны институт",   C["pink"]),
        ],
    ]

    for row_grp in count_trend_groups:
        cols_t = st.columns(len(row_grp))
        for ci, (met, lbl, clr) in enumerate(row_grp):
            yrs_t, vals_t = pgseries(met, D)
            fig_t = go.Figure()
            hx = [y for y,v in zip(yrs_t,vals_t) if y<=CURRENT_YEAR and v is not None]
            hy = [v for y,v in zip(yrs_t,vals_t) if y<=CURRENT_YEAR and v is not None]
            fx = [y for y,v in zip(yrs_t,vals_t) if y>CURRENT_YEAR and v is not None]
            fy = [v for y,v in zip(yrs_t,vals_t) if y>CURRENT_YEAR and v is not None]
            fig_t.add_trace(go.Scatter(x=hx, y=hy, mode="lines+markers", name="Бодит",
                line=dict(color=clr, width=2.5), marker=dict(size=7)))
            if fx and hx:
                fig_t.add_trace(go.Scatter(x=[hx[-1]]+fx, y=[hy[-1]]+fy, mode="lines+markers",
                    name="Зорилт", line=dict(color=C["target"], width=2, dash="dot"),
                    marker=dict(size=6, symbol="diamond", color=C["target"])))
            if CURRENT_YEAR in yrs_t:
                fig_t.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="rgba(255,255,255,0.2)",
                    annotation_text="2026", annotation_font_color="rgba(255,255,255,0.4)", annotation_font_size=9)
            tt = dict(**theme(240))
            tt["title"] = dict(text=lbl, font=dict(color=C["white"], size=11))
            fig_t.update_layout(**tt)
            with cols_t[ci]:
                with st.container(border=True):
                    st.plotly_chart(fig_t, use_container_width=True)

# ============================================================
# PAGE 3 — СУРАЛЦАГЧ ХӨГЖИЛ
# ============================================================
elif st.session_state.page == "stud":

    # ── SECTION A: Хувийн KPI cards — 2026 оны хувийн үзүүлэлтүүд ──
    st.markdown("<div class='section-title'>📈 2026 оны хувийн KPI үзүүлэлтүүд</div>", unsafe_allow_html=True)

    pct_kpis_s = [
        ("Виртуал цахимаар хэрэгжиж буй хичээлийн хувь",        "💻 Цахим хичээл %",         C["blue"]),
        ("AI суурилсан хичээлийн сэтгэл ханамжийн хувь",        "🤖 AI сэтгэл ханамж %",     C["purple"]),
        ("Шинэ технологи нэвтрүүлэлтийн үр дүн, үр нөлөө",      "⚡ Технологи нэвтрүүлэлт %", C["teal"]),
        ("Нийт зэргийн бус сургалтын сэтгэл ханамж",            "😊 Зэргийн бус сэтгэл ханамж %", C["green"]),
    ]

    pct_s_cols = st.columns(4)
    for i, (met, lbl, clr) in enumerate(pct_kpis_s):
        v = sv(met, CURRENT_YEAR, D)
        val_str = f"{v*100:.1f}%" if v is not None else "—"
        pct_s_cols[i].markdown(f"""
<div style='background:#0a1428;border:1px solid #162040;border-radius:10px;
padding:14px 12px;text-align:center;margin-bottom:8px;border-top:2px solid {clr};'>
    <div style='color:{clr};font-size:24px;font-weight:700;'>{val_str}</div>
    <div style='color:#4a6a98;font-size:10px;margin-top:3px;'>{lbl}</div>
</div>""", unsafe_allow_html=True)

    # ── SECTION B: Тоон KPI cards — 2026 оны тоон үзүүлэлтүүд ──
    st.markdown("<div class='section-title'>📊 2026 оны тоон үзүүлэлтүүд</div>", unsafe_allow_html=True)

    count_kpis_s = [
        ("Хичээлийн тоо",                                                  "📚 Нийт хичээл",               C["blue"]),
        ("Цахим хэлбэрээр орж буй хичээлийн тоо",                         "💻 Цахим хичээл",               C["teal"]),
        ("Гадаад хэлээр зааж буй хичээлийн тоо",                          "🌐 Гадаад хэлний хичээл",       C["green"]),
        ("AI суурилсан хичээлийн тоо",                                     "🤖 AI суурилсан хичээл",        C["purple"]),
        ("Шинээр хөгжүүлсэн хичээлийн тоо",                               "✨ Шинэ хичээл",                C["orange"]),
        ("Гадаад хэлээр заасан нийт группийн тоо",                        "👥 Гадаад хэлний групп",        C["pink"]),
        ("Хэрэгжүүлсэн зэргийн бус сургалтын хөтөлбөрийн тоо",          "🎯 Зэргийн бус хөтөлбөр",       C["teal"]),
        ("Платформ хэлбэрээр хэрэгжүүлж байгаа сургалт, судалгааны тоо", "🖥️ Платформ сургалт",            C["blue"]),
    ]

    cnt_cols = st.columns(4)
    for i, (met, lbl, clr) in enumerate(count_kpis_s):
        v = sv(met, CURRENT_YEAR, D)
        val_str = str(int(v)) if v is not None else "—"
        cnt_cols[i % 4].markdown(f"""
<div style='background:#0a1428;border:1px solid #162040;border-radius:10px;
padding:12px 10px;text-align:center;margin-bottom:8px;border-top:2px solid {clr};'>
    <div style='color:{clr};font-size:24px;font-weight:700;'>{val_str}</div>
    <div style='color:#4a6a98;font-size:10px;margin-top:3px;'>{lbl}</div>
</div>""", unsafe_allow_html=True)

    # ── SECTION C: Хувийн KPI трендийн графикууд (2026-аас хойш зорилт) ──
    st.markdown("<div class='section-title'>📉 Хувийн KPI трендийн графикууд — Бодит ба Зорилт</div>", unsafe_allow_html=True)

    pct_trend_s = [
        ("Виртуал цахимаар хэрэгжиж буй хичээлийн хувь",     "Цахим хичээлийн хувь (%)",          C["blue"]),
        ("AI суурилсан хичээлийн сэтгэл ханамжийн хувь",     "AI хичээлийн сэтгэл ханамж (%)",    C["purple"]),
        ("Шинэ технологи нэвтрүүлэлтийн үр дүн, үр нөлөө",  "Технологи нэвтрүүлэлтийн үр нөлөө (%)", C["teal"]),
        ("Нийт зэргийн бус сургалтын сэтгэл ханамж",         "Зэргийн бус сэтгэл ханамж (%)",     C["green"]),
    ]

    sc1, sc2 = st.columns(2)
    s_cols_cycle = [sc1, sc2, sc1, sc2]
    for i, (met, lbl, clr) in enumerate(pct_trend_s):
        yrs_s, vals_s = sseries(met, D)
        fig_s = go.Figure()
        hx = [y for y,v in zip(yrs_s,vals_s) if y<=CURRENT_YEAR and v is not None]
        hy = [v for y,v in zip(yrs_s,vals_s) if y<=CURRENT_YEAR and v is not None]
        fx = [y for y,v in zip(yrs_s,vals_s) if y>CURRENT_YEAR and v is not None]
        fy = [v for y,v in zip(yrs_s,vals_s) if y>CURRENT_YEAR and v is not None]
        fig_s.add_trace(go.Scatter(x=hx, y=hy, mode="lines+markers", name="Бодит",
            line=dict(color=clr, width=2.5), marker=dict(size=7, color=clr)))
        if fx and hx:
            fig_s.add_trace(go.Scatter(x=[hx[-1]]+fx, y=[hy[-1]]+fy, mode="lines+markers",
                name="Зорилт", line=dict(color=C["target"], width=2, dash="dot"),
                marker=dict(size=7, color=C["target"], symbol="diamond")))
        if CURRENT_YEAR in yrs_s:
            fig_s.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="rgba(255,255,255,0.2)",
                annotation_text="2026", annotation_font_color="rgba(255,255,255,0.4)", annotation_font_size=10)
        ts = dict(**theme(280))
        ts["title"] = dict(text=lbl, font=dict(color=C["white"], size=12))
        ts["yaxis"]["tickformat"] = ".0%"
        fig_s.update_layout(**ts)
        with s_cols_cycle[i]:
            with st.container(border=True):
                st.plotly_chart(fig_s, use_container_width=True)

    # ── SECTION D: 2026 оны тоон үзүүлэлтүүдийн визуализаци ──
    st.markdown("<div class='section-title'>📊 2026 оны хичээлийн бүрэлдэхүүн — Pie chart</div>", unsafe_allow_html=True)

    pie_col1, pie_col2, pie_col3 = st.columns(3)

    with pie_col1:
        # Хичээлийн төрлийн харьцаа
        course_types = [
            "Цахим хэлбэрээр орж буй хичээлийн тоо",
            "Гадаад хэлээр зааж буй хичээлийн тоо",
            "AI суурилсан хичээлийн тоо",
            "Шинээр хөгжүүлсэн хичээлийн тоо",
        ]
        course_labels = ["Цахим", "Гадаад хэлний", "AI суурилсан", "Шинэ"]
        course_vals = [sv(m, CURRENT_YEAR, D) or 0 for m in course_types]
        total_c = sv("Хичээлийн тоо", CURRENT_YEAR, D) or 1
        # Бусад = нийт - тусгай ангиллаас гадна
        fig_pie1 = go.Figure(go.Pie(
            labels=course_labels,
            values=course_vals,
            hole=0.5,
            marker=dict(colors=DEPT_COLORS[:4], line=dict(color=C["bg"], width=2)),
            textinfo="label+percent",
            textfont=dict(color=C["text"], size=10),
            insidetextorientation="radial",
        ))
        t_pie1 = dict(**theme(280))
        t_pie1["title"] = dict(text="Хичээлийн ангиллын харьцаа", font=dict(color=C["white"], size=12))
        t_pie1["showlegend"] = False
        fig_pie1.update_layout(**t_pie1)
        st.plotly_chart(fig_pie1, use_container_width=True)

    with pie_col2:
        # Группийн харьцаа — гадаад хэлний групп vs нийт
        grp_val = sv("Гадаад хэлээр заасан нийт группийн тоо", CURRENT_YEAR, D) or 0
        total_course = sv("Хичээлийн тоо", CURRENT_YEAR, D) or 0
        other_grp = max(total_course - grp_val, 0)
        fig_pie2 = go.Figure(go.Pie(
            labels=["Гадаад хэлний групп", "Бусад"],
            values=[grp_val, other_grp],
            hole=0.5,
            marker=dict(colors=[C["green"], C["grid"]], line=dict(color=C["bg"], width=2)),
            textinfo="label+value",
            textfont=dict(color=C["text"], size=10),
        ))
        t_pie2 = dict(**theme(280))
        t_pie2["title"] = dict(text="Гадаад хэлний группийн харьцаа", font=dict(color=C["white"], size=12))
        t_pie2["showlegend"] = False
        fig_pie2.update_layout(**t_pie2)
        st.plotly_chart(fig_pie2, use_container_width=True)

    with pie_col3:
        # Платформ сургалт vs зэргийн бус хөтөлбөр
        plat_val = sv("Платформ хэлбэрээр хэрэгжүүлж байгаа сургалт, судалгааны тоо", CURRENT_YEAR, D) or 0
        cert_val = sv("Хэрэгжүүлсэн зэргийн бус сургалтын хөтөлбөрийн тоо", CURRENT_YEAR, D) or 0
        fig_pie3 = go.Figure(go.Pie(
            labels=["Платформ сургалт", "Зэргийн бус хөтөлбөр"],
            values=[plat_val, cert_val],
            hole=0.5,
            marker=dict(colors=[C["orange"], C["purple"]], line=dict(color=C["bg"], width=2)),
            textinfo="label+value",
            textfont=dict(color=C["text"], size=10),
        ))
        t_pie3 = dict(**theme(280))
        t_pie3["title"] = dict(text="Платформ & Зэргийн бус сургалт", font=dict(color=C["white"], size=12))
        t_pie3["showlegend"] = False
        fig_pie3.update_layout(**t_pie3)
        st.plotly_chart(fig_pie3, use_container_width=True)

    # ── SECTION E: Тэнхимийн харьцуулсан баганан диаграм ──
    st.markdown("<div class='section-title'>🏛️ Тэнхимийн харьцуулсан үзүүлэлтүүд (2026)</div>", unsafe_allow_html=True)

    stud_dept_opts = {
        "Нийт хичээлийн тоо":                  "Хичээлийн тоо",
        "Цахим хичээлийн тоо":                  "Цахим хэлбэрээр орж буй хичээлийн тоо",
        "Гадаад хэлний хичээлийн тоо":          "Гадаад хэлээр зааж буй хичээлийн тоо",
        "AI суурилсан хичээлийн тоо":            "AI суурилсан хичээлийн тоо",
        "Шинэ хичээлийн тоо":                   "Шинээр хөгжүүлсэн хичээлийн тоо",
        "Гадаад хэлний группийн тоо":            "Гадаад хэлээр заасан нийт группийн тоо",
        "Зэргийн бус хөтөлбөрийн тоо":          "Хэрэгжүүлсэн зэргийн бус сургалтын хөтөлбөрийн тоо",
        "Платформ сургалтын тоо":                "Платформ хэлбэрээр хэрэгжүүлж байгаа сургалт, судалгааны тоо",
    }

    sel_sd = st.selectbox("Тэнхимээр харьцуулах үзүүлэлт:", list(stud_dept_opts.keys()), key="stud_dept_sel")
    sel_met_sd = stud_dept_opts[sel_sd]

    vals_sd = []
    for d in DEPTS_S:
        v = sv(sel_met_sd, CURRENT_YEAR, d)
        vals_sd.append(int(v) if v is not None else 0)

    avg_sd = round(sum(vals_sd) / max(len([v for v in vals_sd if v > 0]), 1), 1)
    fig_sd = go.Figure(go.Bar(
        x=DEPTS_S, y=vals_sd,
        marker=dict(color=DEPT_COLORS, line=dict(color=C["bg"], width=0.5)),
        text=[str(v) for v in vals_sd], textposition="outside",
        textfont=dict(color=C["text"], size=10),
    ))
    t_sd = dict(**theme(340))
    t_sd["title"] = dict(text=f"Тэнхим тус бүрийн {sel_sd} (2026)", font=dict(color=C["white"], size=12))
    t_sd["xaxis"]["tickfont"] = dict(size=10)
    fig_sd.update_layout(**t_sd)
    fig_sd.add_hline(y=avg_sd, line_dash="dash", line_color="#ff4d4d", line_width=1.5,
        annotation_text=f"Дундаж: {avg_sd}",
        annotation_position="top right", annotation_font=dict(color="#ff4d4d", size=11))
    with st.container(border=True):
        st.plotly_chart(fig_sd, use_container_width=True)

    # ── SECTION F: Хичээлийн тоон үзүүлэлтүүдийн хэлбэлзэл — 2026 оны Heatmap ──
    st.markdown("<div class='section-title'>🔥 Хичээлийн үзүүлэлтүүдийн тэнхимийн heatmap (2026)</div>", unsafe_allow_html=True)

    heatmap_metrics = [
        ("Хичээлийн тоо",                                                  "Нийт хичээл"),
        ("Цахим хэлбэрээр орж буй хичээлийн тоо",                         "Цахим"),
        ("Гадаад хэлээр зааж буй хичээлийн тоо",                          "Гадаад хэл"),
        ("AI суурилсан хичээлийн тоо",                                     "AI суурилсан"),
        ("Шинээр хөгжүүлсэн хичээлийн тоо",                               "Шинэ"),
        ("Гадаад хэлээр заасан нийт группийн тоо",                        "Гадаад групп"),
        ("Хэрэгжүүлсэн зэргийн бус сургалтын хөтөлбөрийн тоо",          "Зэргийн бус"),
        ("Платформ хэлбэрээр хэрэгжүүлж байгаа сургалт, судалгааны тоо", "Платформ"),
    ]

    hm_data = []
    hm_labels = []
    for met, lbl in heatmap_metrics:
        row = [sv(met, CURRENT_YEAR, d) or 0 for d in DEPTS_S]
        hm_data.append(row)
        hm_labels.append(lbl)

    fig_hm = go.Figure(go.Heatmap(
        z=hm_data,
        x=DEPTS_S,
        y=hm_labels,
        colorscale=[[0, "#080e1c"], [0.3, "#0d2a5a"], [0.6, "#1a5299"], [1.0, "#00d4ff"]],
        text=[[str(int(v)) for v in row] for row in hm_data],
        texttemplate="%{text}",
        textfont=dict(color=C["white"], size=10),
        showscale=True,
        colorbar=dict(
            tickfont=dict(color=C["text"]),
            outlinecolor=C["grid"],
            outlinewidth=1,
        ),
    ))
    t_hm = dict(**theme(360))
    t_hm["title"] = dict(text="Тэнхимийн хичээлийн үзүүлэлтүүдийн heatmap (2026)", font=dict(color=C["white"], size=12))
    t_hm["xaxis"]["tickfont"] = dict(size=10)
    t_hm["yaxis"]["tickfont"] = dict(size=10)
    t_hm["margin"]["l"] = 140
    fig_hm.update_layout(**t_hm)
    with st.container(border=True):
        st.plotly_chart(fig_hm, use_container_width=True)

    # ── SECTION G: Стэк баганан диаграм — хичээлийн төрлүүд тэнхимээр ──
    st.markdown("<div class='section-title'>📊 Хичээлийн төрлүүдийн стэк диаграм (2026)</div>", unsafe_allow_html=True)

    stack_metrics = [
        ("Цахим хэлбэрээр орж буй хичээлийн тоо",  "Цахим",       C["teal"]),
        ("Гадаад хэлээр зааж буй хичээлийн тоо",   "Гадаад хэл",  C["green"]),
        ("AI суурилсан хичээлийн тоо",              "AI суурилсан", C["purple"]),
        ("Шинээр хөгжүүлсэн хичээлийн тоо",        "Шинэ",        C["orange"]),
    ]

    fig_stk = go.Figure()
    for met, lbl, clr in stack_metrics:
        vals_stk = [sv(met, CURRENT_YEAR, d) or 0 for d in DEPTS_S]
        fig_stk.add_trace(go.Bar(x=DEPTS_S, y=vals_stk, name=lbl, marker_color=clr))

    t_stk = dict(**theme(340))
    t_stk["title"] = dict(text="Хичээлийн төрлүүд тэнхимээр (2026)", font=dict(color=C["white"], size=12))
    t_stk["barmode"] = "stack"
    t_stk["xaxis"]["tickfont"] = dict(size=10)
    fig_stk.update_layout(**t_stk)
    with st.container(border=True):
        st.plotly_chart(fig_stk, use_container_width=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#162040;font-size:11px;padding:8px 0'>
СЭЗИС — Стратегийн KPI Хяналтын Систем | 2026
</div>""", unsafe_allow_html=True)
