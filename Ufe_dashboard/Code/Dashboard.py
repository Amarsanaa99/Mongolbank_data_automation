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

="stSidebar"] {
    background: linear-gradient(180deg, #080d1a 0%, #0a1228 100%);
    border-right: 1px solid #162040;
}
="stSidebar"] * { color: #8aaad8 !important; }

div="stSidebar"] .stButton > button {
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
div="stSidebar"] .stButton > button:hover {
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

# Sidebar-ын дээрээс зай ихэсгэх
[data-testid="stSidebar"] > div:first-child {
    padding-top: 40px !important;   # 8px → 40px болгох

# Товчлуурын хоорондох зай
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 4px !important;            # 0px → 4px болгох

# Товчлуур дотоод зай
div[data-testid="stSidebar"] .stButton > button {
    margin-bottom: 6px !important;  # 4px → 6px болгох
    padding: 10px 14px !important;  # 8px → 10px болгох
section[data-testid="stSidebar"] {
    overflow: hidden !important;
    height: 100vh !important;
}
section[data-testid="stSidebar"] > div {
    overflow-y: auto !important;
    height: 100% !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING — Багшийн хөгжил
# ============================================================
@st.cache_data
def load_teacher_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "..", "data", "Teach_dev_cl.xlsx")
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
# DATA LOADING — Хичээл сургалт
# ============================================================
@st.cache_data
def load_stud_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "..", "data", "Less_dev_cl.xlsx")
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

# ============================================================
# DATA LOADING — Суралцагч хөгжил
# ============================================================
@st.cache_data
def load_stud_dev_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "..", "data", "stud_dev_cl.xlsx")
    df = pd.read_excel(DATA_PATH, sheet_name="Sheet1", header=None)
    df2 = df.copy()
    df2[0] = df2[0].ffill()
    df2[1] = df2[1].ffill()
    df2 = df2[df2[2].notna() & (df2[2] != "Он") & (df2[2] != "Ангилал")]
    df2[2] = pd.to_numeric(df2[2], errors="coerce")
    df2 = df2[df2[2].notna()].copy()
    for c in range(3, 88):
        df2[c] = pd.to_numeric(df2[c], errors="coerce")
    PROGRAMS = [
        "Эдийн засаг", "Нягтлан бодох бүртгэл", "Санхүү, банк", "Даатгал",
        "Бизнесийн удирдлага", "Маркетинг", "Эрх зүй", "Мэдээллийн систем",
        "Зочлох үйлчилгээ", "Аялал жуучлал", "Худалдаа", "АССА", "CGMA",
        "Энтрепренер", "Санхүүгийн манлайлал", "Гадаад хэлний боловсрол", "Нийгмийн инноваци"
    ]
    PROG_COLS = list(range(3, 88, 5))
    return df2, PROGRAMS, PROG_COLS
# ============================================================
# DATA LOADING — Судалгаа, төсөл хөтөлбөр
# ============================================================
@st.cache_data
def load_res_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "..", "data", "res_dev_cl.xlsx")
    df = pd.read_excel(DATA_PATH, sheet_name="Sheet1", header=None)
    df[0] = df[0].ffill()
    df[1] = df[1].ffill()
    df = df[df[2].notna() & (df[2] != "Он") & (df[2] != "Ангилал")]
    df[2] = pd.to_numeric(df[2], errors="coerce")
    df = df[df[2].notna()].copy()
    COLS = ["Ангилал","Үзүүлэлт","Он","БУТ","МКТ","МСМТ","НББТ","ОУАЖССИ",
            "ОУНББСМИ","ОУС","СДСТ","СУТ","СШУТ","ЭкТ","ЭнТИнс","ЭЗТ","Нийт"]
    df.columns = COLS
    for c in COLS[3:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["Үзүүлэлт"] = df["Үзүүлэлт"].str.strip()
    return df

# ============================================================
# DATA LOADING — Санхүү
# ============================================================
@st.cache_data
def load_fin_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "..", "data", "Fin_dev_cl.xlsx")
    df = pd.read_excel(DATA_PATH, sheet_name="Sheet1", header=None)
    
    # ✅ ЗАСВАР: эхлээд ffill хийх, дараа нь шүүх
    df[0] = df[0].ffill()
    df[1] = df[1].ffill()
    
    df = df[df[2].notna() & (df[2] != "Он") & (df[2] != "Ангилал")]
    df[2] = pd.to_numeric(df[2], errors="coerce")
    df = df[df[2].notna()].copy()
    
    COLS = ["Ангилал","Үзүүлэлт","Он",
            "БУТ","МКТ","МСМТ","НББТ","ОУАЖССИ","ОУНББСМИ",
            "ОУС","СДСТ","СУТ","СШУТ","ЭкТ","ЭнТИнс","ЭЗТ","Нийт"]
    df.columns = COLS
    for c in COLS[3:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["Үзүүлэлт"] = df["Үзүүлэлт"].str.strip()
    return df
df, DEPTS       = load_teacher_data()
dfp, DEPTS_P    = load_prog_data()
dfs, DEPTS_S    = load_stud_data()
dfd, PROGRAMS_D, PROG_COLS_D = load_stud_dev_data()
dfr = load_res_data()
dff = load_fin_data()
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
PROG_COLORS = [
    "#00d4ff","#00e676","#b388ff","#ffab40","#ff80ab","#64ffda","#3a8aff",
    "#ff9800","#f06292","#4fc3f7","#aed581","#ce93d8","#ffb74d","#80cbc4",
    "#ef9a9a","#a5d6a7","#90caf9"
]

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
    r = dfs[(dfs["Үзүүлэлт"]==metric)&(dfs["Он"]==year)]
    return r.iloc[0][dept] if not r.empty else None

def sseries(metric, dept):
    s = dfs[dfs["Үзүүлэлт"]==metric].sort_values("Он")
    return list(s["Он"]), list(s[dept])

# ── Суралцагч хөгжил helpers ──
def sdv_prog_total(metric, year, prog_idx):
    """Get total (sum of 5 course years) for a given program index"""
    row = dfd[(dfd[1]==metric)&(dfd[2]==year)]
    if row.empty:
        return None
    cs = PROG_COLS_D[prog_idx]
    vals = [row.iloc[0, cs+j] for j in range(5) if pd.notna(row.iloc[0, cs+j])]
    return int(sum(vals)) if vals else None

def sdv_grand_total(metric, year):
    """Sum across all programs and all course years"""
    row = dfd[(dfd[1]==metric)&(dfd[2]==year)]
    if row.empty:
        return None
    total = 0
    for i in range(len(PROGRAMS_D)):
        cs = PROG_COLS_D[i]
        for j in range(5):
            v = row.iloc[0, cs+j]
            if pd.notna(v):
                total += v
    return total

def sdv_course_breakdown(metric, year, prog_idx):
    """Get list of 5 course year values for a program"""
    row = dfd[(dfd[1]==metric)&(dfd[2]==year)]
    if row.empty:
        return [0]*5
    cs = PROG_COLS_D[prog_idx]
    return [row.iloc[0, cs+j] if pd.notna(row.iloc[0, cs+j]) else 0 for j in range(5)]

def sdv_pct_grand(metric, year):
    """Average pct across all programs (first course col per program as representative)"""
    row = dfd[(dfd[1]==metric)&(dfd[2]==year)]
    if row.empty:
        return None
    vals = []
    for i in range(len(PROGRAMS_D)):
        v = row.iloc[0, PROG_COLS_D[i]]
        if pd.notna(v):
            vals.append(v)
    return sum(vals)/len(vals) if vals else None

def sdv_pct_series(metric):
    """Get year trend for pct metric (average across all programs)"""
    rows = dfd[dfd[1]==metric].sort_values(2)
    years, vals = [], []
    for _, row in rows.iterrows():
        prog_vals = [row[PROG_COLS_D[i]] for i in range(len(PROGRAMS_D)) if pd.notna(row[PROG_COLS_D[i]])]
        avg = sum(prog_vals)/len(prog_vals) if prog_vals else None
        years.append(int(row[2]))
        vals.append(avg)
    return years, vals

def sdv_count_series_grand(metric):
    """Get year trend for count metric (sum all programs all course years)"""
    rows = dfd[dfd[1]==metric].sort_values(2)
    years, vals = [], []
    for _, row in rows.iterrows():
        total = 0
        for i in range(len(PROGRAMS_D)):
            cs = PROG_COLS_D[i]
            for j in range(5):
                v = row[cs+j]
                if pd.notna(v):
                    total += v
        years.append(int(row[2]))
        vals.append(total)
    return years, vals

def sdv_prog_series(metric, prog_idx):
    """Trend for a specific program (sum of course years)"""
    rows = dfd[dfd[1]==metric].sort_values(2)
    years, vals = [], []
    for _, row in rows.iterrows():
        cs = PROG_COLS_D[prog_idx]
        total = sum([row[cs+j] for j in range(5) if pd.notna(row[cs+j])])
        years.append(int(row[2]))
        vals.append(total)
    return years, vals

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
    fig.update_layout(yaxis=dict(tickformat=".1%", gridcolor=C["grid"]))
    return fig
def donut_fig(labels, values, title, h=300, colors=None):
    clrs = colors[:len(labels)] if colors else DEPT_COLORS[:len(labels)]
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
if "sd_prog" not in st.session_state:
    st.session_state.sd_prog = "Эдийн засаг"

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
""", unsafe_allow_html=True)

    if st.session_state.page != "stud_dev":
        st.markdown("""
<div style='color:#4a7acc;font-size:11px;font-weight:600;letter-spacing:1px;margin-bottom:6px;'>ТЭНХИМ СОНГОХ</div>
""", unsafe_allow_html=True)
        all_depts = ["Нийт"] + DEPTS
        for d in all_depts:
            label = dept_labels.get(d, d)
            if st.button(label, key=f"dept_{d}"):
                st.session_state.dept = d
                st.rerun()
    else:
        st.markdown("""
<div style='color:#4a7acc;font-size:11px;font-weight:600;letter-spacing:1px;margin-bottom:6px;'>ХӨТӨЛБӨР СОНГОХ</div>
""", unsafe_allow_html=True)
        for prog in PROGRAMS_D:
            short = prog[:14] + "…" if len(prog) > 14 else prog
            if st.button(f"📋 {short}", key=f"prog_{prog}"):
                st.session_state.sd_prog = prog
                st.rerun()

D = st.session_state.dept
SELECTED_PROG = st.session_state.sd_prog
SELECTED_PROG_IDX = PROGRAMS_D.index(SELECTED_PROG) if SELECTED_PROG in PROGRAMS_D else 0

# ============================================================
# HEADER — page navigation tabs
# ============================================================
col_h1, col_h2, col_h3, col_h4, col_h5, col_h6, col_h7 = st.columns([3, 1, 1, 1, 1, 1, 1])
with col_h1:
    disp_name = dept_labels.get(D, D) if st.session_state.page != "stud_dev" else f"📋 {SELECTED_PROG}"
    st.markdown(f"""
<div style='background:linear-gradient(90deg,#0d1f4a,#1a2d6b,#0d1f4a);
border:1px solid #1e3a8a;border-radius:14px;padding:12px 20px;'>
<span style='color:#fff;font-size:17px;font-weight:700;'>🎓 СЭЗИС — Стратегийн KPI Самбар</span><br>
<span style='color:#5a80b8;font-size:12px;'>Сонголт: <b style='color:#00d4ff'>{disp_name}</b> &nbsp;|&nbsp; Одоогийн жил: <b style='color:#00d4ff'>2026</b></span>
</div>
""", unsafe_allow_html=True)

with col_h2:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("👩‍🏫 Багшийн хөгжил", key="nav_teacher",
                 type="primary" if st.session_state.page == "teacher" else "secondary"):
        st.session_state.page = "teacher"
        st.rerun()

with col_h3:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("📚 Хөтөлбөр хөгжил", key="nav_prog",
                 type="primary" if st.session_state.page == "prog" else "secondary"):
        st.session_state.page = "prog"
        st.rerun()

with col_h4:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("🎓 Хичээл, Сургалт", key="nav_stud",
                 type="primary" if st.session_state.page == "stud" else "secondary"):
        st.session_state.page = "stud"
        st.rerun()

with col_h5:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("🏫 Суралцагч хөгжил", key="nav_stud_dev",
                 type="primary" if st.session_state.page == "stud_dev" else "secondary"):
        st.session_state.page = "stud_dev"
        st.rerun()
with col_h6:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("🔬 Судалгаа, төсөл", key="nav_res",
                 type="primary" if st.session_state.page == "res" else "secondary"):
        st.session_state.page = "res"
        st.rerun()
with col_h7:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("💰 Санхүүгийн мэдээлэл", key="nav_fin",
                 type="primary" if st.session_state.page == "fin" else "secondary"):
        st.session_state.page = "fin"
        st.rerun()
st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

# ============================================================
# PAGE 1 — БАГШИЙН ХӨГЖИЛ
# ============================================================
if st.session_state.page == "teacher":
# ============================================================
# SECTION 1 — KPI КАРТ ҮЗҮҮЛЭЛТҮҮД
# ============================================================
    st.markdown("<div class='section-title'>📈 2026 оны хувийн KPI үзүүлэлтүүд</div>", unsafe_allow_html=True)
    pct_kpis = [
        ("Хувь", "Доктор зэрэгтэй багшийн эзлэх хувь",                     "🔬 Доктор зэрэгтэй багш",             C["blue"]),
        ("Хувь", "Гадаад багшийн эзлэх хувь",                               "🌍 Гадаад багш",              C["blue"]),
        ("Хувь", "Оюутны сэтгэл ханамжийн үнэлгээний дундаж хувь",         "😊 Оюутны сэтгэл ханамж",  C["blue"]),
        ("Хувь", "Багшийн сэтгэл ханамжийн үнэлгээний дундаж хувь",        "👩‍🏫 Багшийн сэтгэл ханамж", C["blue"]),
        ("Хувь", "Гадаад хэлээр заах чадвартай багшийн эзлэх хувь",        "🗣️ Гадаад хэлээр заах чадвартай",         C["blue"]),
        ("Хувь", "Солилцооны хөтөлбөрт хамрагдсан багшийн эзлэх хувь",    "🔄 Солилцоонд хамрагдсан",            C["blue"]),
        ("Хувь", "Төсөл удирдсан багшийн эзлэх хувь",                      "📁 Төсөл удирдсан",               C["blue"]),
        ("Хувь", "Хамтарсан судалгаа, төсөлд оролцсон багшийн эзлэх хувь","🤝 Судалгаанд оролцосон",            C["blue"]),
        ("Хувь", "h-индекстэй багшийн эзлэх хувь",                         "📊 h-индекстэй багш",            C["blue"]),
        ("Хувь", "WOS, Scopus-д өгүүлэл хэвлүүлсэн багшийн эзлэх хувь",  "📰 WOS/Scopus өгүүлэлтэй",          C["blue"]),
    ]
    pct_cols = st.columns(5)
    for i, (cat, met, lbl, clr) in enumerate(pct_kpis):
        v = gv(cat, met, CURRENT_YEAR, D)
        pct_str = f"{v*100:.1f}%" if v is not None else "—"
        pct_cols[i % 5].markdown(f"""
<div style='background:#0a1428;border:1px solid #162040;border-radius:10px;
padding:12px 10px;text-align:center;margin-bottom:8px;border-top:2px solid {clr};'>
    <div style='color:{clr};font-size:20px;font-weight:700;'>{pct_str}</div>
    <div style='color:#ffffff;font-size:14px;margin-top:3px;'>{lbl}</div>
</div>""", unsafe_allow_html=True)
# ============================================================
# SECTION 2 — KPI Трендийн графикууд (col_a — зүүн)
# ============================================================
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
# ============================================================
# SECTION 3 — KPI Трендийн графикууд (col_b — баруун)
# ============================================================
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
# ============================================================
# SECTION 4 — Тэнхимийн харьцуулсан үзүүлэлтүүд
# ============================================================
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
        marker=dict(
            color="#118DFF",
            line=dict(color=C["bg"], width=0.5),
            cornerradius=8
        ),
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
# ============================================================
# SECTION 5 — Donut график ба Насны бүлэг
# ============================================================

    BLUE_PALETTE = ["#1E90FF", "#4DB8FF", "#0A4A8A", "#00BFFF", "#0066CC", "#63CFFF"]
    
    st.markdown("<div class='section-title'>🔵 Нийт бүрэлдэхүүний харьцаа (2026)</div>", unsafe_allow_html=True)
    d_col1, d_col2, d_col3 = st.columns(3)
    with d_col1:
        edu_labels = ["Бакалавр", "Магистр", "Доктор"]
        edu_vals = [gv("Боловсролын түвшин", lv, CURRENT_YEAR, D) or 0 for lv in edu_labels]
        st.plotly_chart(donut_fig(edu_labels, edu_vals, "Боловсролын түвшин", colors=BLUE_PALETTE), use_container_width=True)
    with d_col2:
        rank_labels = ["Дадлагажигч багш", "Багш", "Ахлах багш", "Дэд профессор", "Профессор"]
        rank_vals = [gv("Зэрэглэл", lv, CURRENT_YEAR, D) or 0 for lv in rank_labels]
        st.plotly_chart(donut_fig(rank_labels, rank_vals, "Зэрэглэлийн бүрэлдэхүүн", colors=BLUE_PALETTE), use_container_width=True)
    with d_col3:
        comp_labels = ["Үндсэн багш", "Гэрээт багш"]
        comp_vals = [
            gv("Багшийн тоо", "Нийт үндсэн багшийн тоо", CURRENT_YEAR, D) or 0,
            gv("Багшийн тоо", "Нийт гэрээт багшийн тоо", CURRENT_YEAR, D) or 0,
        ]
        st.plotly_chart(donut_fig(comp_labels, comp_vals, "Үндсэн ба Гэрээт багш", colors=BLUE_PALETTE), use_container_width=True)
    
    st.markdown("<div class='section-title'>👥 Насны бүлэг ба Ажилласан жил (2026)</div>", unsafe_allow_html=True)
    age_col, exp_col = st.columns(2)
    
    with age_col:
        age_groups = ["25 хүртэл", "26-35", "36-45", "46-55", "56 ба түүнээс дээш"]
        age_vals = [gv("Насны бүлэг", ag, CURRENT_YEAR, D) or 0 for ag in age_groups]
        # ✅ Vertical баганан диаграмм болгосон + rounded + цэнхэр
        fig_age = go.Figure(go.Bar(
            x=age_groups, y=age_vals,
            orientation="v",
            marker=dict(color="#1E90FF", cornerradius=8),
            text=age_vals, textposition="outside",
            textfont=dict(color=C["text"], size=10)
        ))
        t_age = dict(**theme(260))
        t_age["title"] = dict(text="Насны бүлгийн бүрэлдэхүүн", font=dict(color=C["white"], size=12))
        t_age["yaxis"]["title"] = "Тоо"
        fig_age.update_layout(**t_age)
        st.plotly_chart(fig_age, use_container_width=True)
    
    with exp_col:
        exp_groups = ["3 жил хүртэл", "4-6 жил", "Ажилласан жил - 7-9 жил", "10-15 жил", "16-20 жил", "21 ба түүнээс дээш"]
        exp_labels = ["≤3 жил", "4-6 жил", "7-9 жил", "10-15 жил", "16-20 жил", "21+ жил"]
        exp_vals = [gv("Ажилласан жил", eg, CURRENT_YEAR, D) or 0 for eg in exp_groups]
        # ✅ Horizontal + rounded + цэнхэр нэг өнгө
        fig_exp = go.Figure(go.Bar(
            x=exp_vals, y=exp_labels,
            orientation="h",
            marker=dict(color="#1E90FF", cornerradius=8),
            text=exp_vals, textposition="outside",
            textfont=dict(color=C["text"], size=10)
        ))
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

    # ── SECTION A: 2026 оны тоон KPI ──
    st.markdown("<div class='section-title'>📊 2026 оны үндсэн үзүүлэлтүүд</div>", unsafe_allow_html=True)

    count_kpis = [
        ("Хэрэгжүүлж буй үндсэн хөтөлбөрийн тоо",          "📋 Үндсэн хөтөлбөр",            C["blue"]),
        ("Цахимаар хэрэгжиж буй хөтөлбөрийн тоо",           "💻 Цахим хөтөлбөр",              C["blue"]),
        ("Цагийн хөтөлбөрийн тоо",                           "⏱ Цагийн хөтөлбөр",              C["blue"]),
        ("Гадаад хэлээр явуулах хөтөлбөрийн тоо",           "🌐 Гадаад хэлний хөтөлбөр",      C["blue"]),
        ("Хамтарсан хөтөлбөрийн тоо",                        "🤝 Хамтарсан хөтөлбөр",          C["blue"]),
        ("ОУ дипломтой хөтөлбөрийн тоо",                     "🎓 ОУ диплом",                   C["blue"]),
        ("Интерактив хөтөлбөрийн тоо",                       "🔬 Интерактив",                   C["blue"]),
        ("Ажлын байранд суурилсан хөтөлбөрийн тоо",         "🏭 Ажлын байранд суурилсан",      C["blue"]),
        ("Хамтын ажиллагааны гэрээтэй байгууллагын тоо",    "📝 Гэрээт байгуулага",            C["blue"]),
        ("Хүлээн зөвшөөрөгдсөн ОУ мэргэжлийн байгууллагын тоо", "✅ ОУ мэргэжлийн байгуулага", C["blue"]),
    ]
    kpi_cols = st.columns(5)
    for i, (met, lbl, clr) in enumerate(count_kpis):
        v = pgv(met, CURRENT_YEAR, D)
        val_str = str(int(v)) if v is not None else "—"
        kpi_cols[i % 5].markdown(f"""
<div style='background:#0a1428;border:1px solid #162040;border-radius:10px;
padding:12px 10px;text-align:center;margin-bottom:8px;border-top:2px solid {clr};'>
    <div style='color:{clr};font-size:24px;font-weight:700;'>{val_str}</div>
    <div style='color:#ffffff;font-size:14px;margin-top:3px;'>{lbl}</div>
</div>""", unsafe_allow_html=True)

    # ── SECTION B: Хувийн KPI трендийн графикууд ──
    st.markdown("<div class='section-title'>📉 Хувийн KPI трендийн графикууд — Бодит ба Зорилт</div>", unsafe_allow_html=True)

    pct_trend_metrics = [
        ("ОУ-д магадлан итгэмжлэгдсэн хөтөлбөрийн хувь",                 "ОУ магадлан итгэмжлэлт %",       C["blue"]),
        ("Үндэсний хэмжээнд магадлан итгэмжлэгдсэн хөтөлбөрийн хувь",    "Үндэсний магадлан итгэмжлэлт %", C["teal"]),
        ("Цахимаар хэрэгжиж буй хөтөлбөрийн нийт хөтөлбөрт эзлэх хувь", "Цахим хөтөлбөрийн %",            C["purple"]),
        ("СҮД хурлаас гарсан санал хүсэлтийн шийдвэрлэлтийн хувь",       "СҮД шийдвэрлэлт %",              C["green"]),
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

# ── SECTION C: Тэнхимийн харьцуулалт ──
    st.markdown("<div class='section-title'>🏛️ Тэнхимийн харьцуулсан үзүүлэлтүүд (2026)</div>", unsafe_allow_html=True)

    prog_dept_opts = {
        "Үндсэн хөтөлбөрийн тоо":          "Хэрэгжүүлж буй үндсэн хөтөлбөрийн тоо",
        "Цахим хөтөлбөрийн тоо":            "Цахимаар хэрэгжиж буй хөтөлбөрийн тоо",
        "Цагийн хөтөлбөрийн тоо":           "Цагийн хөтөлбөрийн тоо",
        "Гадаад хэлний хөтөлбөр":           "Гадаад хэлээр явуулах хөтөлбөрийн тоо",
        "Хамтарсан хөтөлбөр":               "Хамтарсан хөтөлбөрийн тоо",
        "ОУ дипломтой хөтөлбөр":            "ОУ дипломтой хөтөлбөрийн тоо",
        "Интерактив хөтөлбөр":              "Интерактив хөтөлбөрийн тоо",
        "Ажлын байранд суурилсан хөтөлбөр": "Ажлын байранд суурилсан хөтөлбөрийн тоо",
        "Гэрээт байгуулага":                "Хамтын ажиллагааны гэрээтэй байгууллагын тоо",
        "Ажиглалтад хамрагдсан хичээл":     "Ажиглалтад хамрагдсан хичээлийн тоо",
        "СҮД хэлэлцүүлсэн хичээл":         "Хичээлийн СҮД хурлаар хэлэлцүүлсэн хичээлийн тоо",
    }

    sel_p = st.selectbox("Тэнхимээр харьцуулах үзүүлэлт:", list(prog_dept_opts.keys()), key="prog_dept_sel")
    sel_met_p = prog_dept_opts[sel_p]
    vals_dp = [int(pgv(sel_met_p, CURRENT_YEAR, d) or 0) for d in DEPTS]
    avg_dp = round(sum(vals_dp) / max(len([v for v in vals_dp if v > 0]), 1), 1)

    fig_dp = go.Figure(go.Bar(
        x=DEPTS, y=vals_dp,
        marker=dict(
            color="#118DFF",
            line=dict(color=C["bg"], width=0.5),
            cornerradius=8
        ),
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

    # ── SECTION D: Хөтөлбөрийн бүрэлдэхүүн ба үзүүлэлтүүд (2026) ──
    st.markdown("<div class='section-title'>📊 2026 оны хөтөлбөрийн бүрэлдэхүүн ба үзүүлэлтүүд</div>", unsafe_allow_html=True)

    BLUE_PALETTE = ["#1E90FF", "#4DB8FF", "#0A4A8A", "#00BFFF", "#0066CC", "#63CFFF"]

    pie_col, bar_col = st.columns(2)

    # Зүүн — Pie chart (цэнхэр өнгийн палитр)
    with pie_col:
        pie_labels = ["Үндсэн", "Цахим", "Цагийн", "Гадаад хэлний", "Хамтарсан", "ОУ дипломтой"]
        pie_metrics = [
            "Хэрэгжүүлж буй үндсэн хөтөлбөрийн тоо",
            "Цахимаар хэрэгжиж буй хөтөлбөрийн тоо",
            "Цагийн хөтөлбөрийн тоо",
            "Гадаад хэлээр явуулах хөтөлбөрийн тоо",
            "Хамтарсан хөтөлбөрийн тоо",
            "ОУ дипломтой хөтөлбөрийн тоо",
        ]
        pie_vals = [pgv(m, CURRENT_YEAR, D) or 0 for m in pie_metrics]

        fig_pie_prog = go.Figure(go.Pie(
            labels=pie_labels, values=pie_vals, hole=0.52,
            marker=dict(colors=BLUE_PALETTE, line=dict(color=C["bg"], width=2)),
            textinfo="label+value+percent", textfont=dict(color=C["text"], size=11),
            insidetextorientation="radial",
        ))
        t_pie_prog = dict(**theme(360))
        t_pie_prog["title"] = dict(text="Хөтөлбөрийн төрлийн бүрэлдэхүүн (2026)", font=dict(color=C["white"], size=12))
        t_pie_prog["showlegend"] = False
        fig_pie_prog.update_layout(**t_pie_prog)
        with st.container(border=True):
            st.plotly_chart(fig_pie_prog, use_container_width=True)

    # Баруун — Horizontal bar chart (rounded + цэнхэр өнгө)
    with bar_col:
        bar_metrics_2026 = [
            ("Ажиглалтад хамрагдсан хичээлийн тоо",                 "Ажиглалтад хамрагдсан"),
            ("Хичээлийн СҮД хурлаар хэлэлцүүлсэн хичээлийн тоо",  "СҮД хэлэлцүүлсэн"),
            ("СҮД хурлаас гарсан санал, хүсэлтийн тоо",             "СҮД санал хүсэлт"),
            ("Хамтын ажиллагааны гэрээтэй байгууллагын тоо",         "Гэрээт байгуулага"),
            ("Хамтарсан хөтөлбөр хэрэгжүүлэгч сургуулийн тоо",     "Хамтарсан сургууль"),
            ("Солилцооны хөтөлбөр хэрэгжүүлэгч институтийн тоо",   "Солилцооны институт"),
        ]

        labels = [lbl for _, lbl in bar_metrics_2026]
        values = [pgv(met, CURRENT_YEAR, D) or 0 for met, _ in bar_metrics_2026]

        fig_bar6 = go.Figure(go.Bar(
            x=values, y=labels,
            orientation="h",
            marker=dict(
                color="#1E90FF",
                line=dict(color=C["bg"], width=0.5),
                cornerradius=8
            ),
            text=[str(int(v)) for v in values],
            textposition="outside",
            textfont=dict(color=C["text"], size=11),
        ))
        tb6 = dict(**theme(360))
        tb6["title"] = dict(text="Бусад үзүүлэлтүүд (2026)", font=dict(color=C["white"], size=12))
        tb6["xaxis"] = dict(gridcolor=C["grid"], zerolinecolor=C["grid"])
        tb6["yaxis"] = dict(gridcolor=C["grid"], zerolinecolor=C["grid"], tickfont=dict(size=11))
        tb6["margin"] = dict(l=160, r=40, t=40, b=36)
        fig_bar6.update_layout(**tb6)
        with st.container(border=True):
            st.plotly_chart(fig_bar6, use_container_width=True)

# ============================================================
# PAGE 3 — Хичээл сургалт
# ============================================================
elif st.session_state.page == "stud":

    # ── SECTION A: 2026 оны тоон KPI ──
    st.markdown("<div class='section-title'>📊 2026 оны тоон үзүүлэлтүүд</div>", unsafe_allow_html=True)

    count_kpis_s = [
        ("Хичээлийн тоо",                                                  "📚 Нийт хичээл",        C["blue"]),
        ("Цахим хэлбэрээр орж буй хичээлийн тоо",                         "💻 Цахим хичээл",        C["blue"]),
        ("Гадаад хэлээр зааж буй хичээлийн тоо",                          "🌐 Гадаад хэлний хичээл",C["blue"]),
        ("AI суурилсан хичээлийн тоо",                                     "🤖 AI суурилсан хичээл", C["blue"]),
        ("Шинээр хөгжүүлсэн хичээлийн тоо",                               "✨ Шинэ хичээл",         C["blue"]),
        ("Гадаад хэлээр заасан нийт группийн тоо",                        "👥 Гадаад хэлний групп", C["blue"]),
        ("Хэрэгжүүлсэн зэргийн бус сургалтын хөтөлбөрийн тоо",          "🎯 Зэргийн бус хөтөлбөр",C["blue"]),
        ("Платформ хэлбэрээр хэрэгжүүлж байгаа сургалт, судалгааны тоо", "🖥️ Платформ сургалт",    C["blue"]),
    ]

    cnt_cols = st.columns(4)
    for i, (met, lbl, clr) in enumerate(count_kpis_s):
        v = sv(met, CURRENT_YEAR, D)
        val_str = str(int(v)) if v is not None else "—"
        cnt_cols[i % 4].markdown(f"""
<div style='background:#0a1428;border:1px solid #162040;border-radius:10px;
padding:12px 10px;text-align:center;margin-bottom:8px;border-top:2px solid {clr};'>
    <div style='color:{clr};font-size:24px;font-weight:700;'>{val_str}</div>
    <div style='color:#ffffff;font-size:14px;margin-top:3px;'>{lbl}</div>
</div>""", unsafe_allow_html=True)

    # ── SECTION B: Хувийн KPI трендийн графикууд ──
    st.markdown("<div class='section-title'>📉 Хувийн KPI трендийн графикууд — Бодит ба Зорилт</div>", unsafe_allow_html=True)

    pct_trend_s = [
        ("Виртуал цахимаар хэрэгжиж буй хичээлийн хувь",    "Цахим хичээлийн хувь (%)",           C["blue"]),
        ("AI суурилсан хичээлийн сэтгэл ханамжийн хувь",    "AI хичээлийн сэтгэл ханамж (%)",     C["purple"]),
        ("Шинэ технологи нэвтрүүлэлтийн үр дүн, үр нөлөө", "Технологи нэвтрүүлэлтийн үр нөлөө (%)", C["teal"]),
        ("Нийт зэргийн бус сургалтын сэтгэл ханамж",        "Зэргийн бус сэтгэл ханамж (%)",      C["green"]),
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
    # ── SECTION D: Тэнхимийн харьцуулалт ──
    st.markdown("<div class='section-title'>🏛️ Тэнхимийн харьцуулсан үзүүлэлтүүд (2026)</div>", unsafe_allow_html=True)

    stud_dept_opts = {
        "Нийт хичээлийн тоо":         "Хичээлийн тоо",
        "Цахим хичээлийн тоо":         "Цахим хэлбэрээр орж буй хичээлийн тоо",
        "Гадаад хэлний хичээлийн тоо": "Гадаад хэлээр зааж буй хичээлийн тоо",
        "AI суурилсан хичээлийн тоо":  "AI суурилсан хичээлийн тоо",
        "Шинэ хичээлийн тоо":          "Шинээр хөгжүүлсэн хичээлийн тоо",
        "Гадаад хэлний группийн тоо":  "Гадаад хэлээр заасан нийт группийн тоо",
        "Зэргийн бус хөтөлбөрийн тоо": "Хэрэгжүүлсэн зэргийн бус сургалтын хөтөлбөрийн тоо",
        "Платформ сургалтын тоо":       "Платформ хэлбэрээр хэрэгжүүлж байгаа сургалт, судалгааны тоо",
    }

    sel_sd = st.selectbox("Тэнхимээр харьцуулах үзүүлэлт:", list(stud_dept_opts.keys()), key="stud_dept_sel")
    sel_met_sd = stud_dept_opts[sel_sd]
    vals_sd = [int(sv(sel_met_sd, CURRENT_YEAR, d) or 0) for d in DEPTS_S]
    avg_sd = round(sum(vals_sd) / max(len([v for v in vals_sd if v > 0]), 1), 1)
    fig_sd = go.Figure(go.Bar(
        x=DEPTS_S, 
        y=vals_sd,
        marker=dict(
            color="#118DFF", 
            line=dict(color=C["bg"], width=0.5), 
            cornerradius=8
        ),
        text=[str(v) for v in vals_sd],
        textposition="outside",
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

    # ── SECTION E: Heatmap ──
    st.markdown("<div class='section-title'>🔥 Тэнхимийн хичээлийн үзүүлэлтүүдийн heatmap (2026)</div>", unsafe_allow_html=True)

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

    hm_data, hm_labels = [], []
    for met, lbl in heatmap_metrics:
        hm_data.append([sv(met, CURRENT_YEAR, d) or 0 for d in DEPTS_S])
        hm_labels.append(lbl)

    fig_hm = go.Figure(go.Heatmap(
        z=hm_data, x=DEPTS_S, y=hm_labels,
        colorscale=[[0, "#080e1c"], [0.3, "#0d2a5a"], [0.6, "#1a5299"], [1.0, "#00d4ff"]],
        text=[[str(int(v)) for v in row] for row in hm_data],
        texttemplate="%{text}", textfont=dict(color=C["white"], size=10),
        showscale=True, colorbar=dict(tickfont=dict(color=C["text"]), outlinecolor=C["grid"], outlinewidth=1),
    ))
    t_hm = dict(**theme(360))
    t_hm["title"] = dict(text="Тэнхимийн хичээлийн үзүүлэлтүүдийн heatmap (2026)", font=dict(color=C["white"], size=12))
    t_hm["xaxis"]["tickfont"] = dict(size=10)
    t_hm["yaxis"]["tickfont"] = dict(size=10)
    t_hm["margin"]["l"] = 140
    fig_hm.update_layout(**t_hm)
    with st.container(border=True):
        st.plotly_chart(fig_hm, use_container_width=True)

# ============================================================
# PAGE 4 — СУРАЛЦАГЧ ХӨГЖИЛ
# ============================================================
elif st.session_state.page == "stud_dev":

    PROG_IDX = SELECTED_PROG_IDX
    COURSES = ["I курс", "II курс", "III курс", "IV курс", "V+ курс"]

    # ── SECTION A: Сонгосон хөтөлбөрийн 2026 оны тоон KPI ──
    st.markdown(f"<div class='section-title'>📊 {SELECTED_PROG} — 2026 оны тоон үзүүлэлтүүд</div>", unsafe_allow_html=True)

    count_kpis_sd = [
        ("Үндсэн + цагийн + цахим суралцагчийн тоо",           "👥 Нийт суралцагч",      C["blue"]),
        ("Үндсэн хөтөлбөрийн суралцагчийн тоо",                "📘 Үндсэн хөтөлбөр",     C["blue"]),
        ("Цагийн хөтөлбөрийн суралцагчийн тоо",                "⏱ Цагийн хөтөлбөр",      C["blue"]),
        ("Цахимаар хэрэгжиж буй хөтөлбөрийн суралцагчийн тоо","💻 Цахим хөтөлбөр",       C["blue"]),
        ("Гадаад хэлээр явуулах хөтөлбөрийн суралцагчийн тоо","🌐 Гадаад хэлний",         C["blue"]),
        ("Хамтарсан хөтөлбөрийн суралцагчийн тоо",             "🤝 Хамтарсан",            C["blue"]),
        ("ОУ дипломтой хөтөлбөрийн суралцагчийн тоо",          "🎓 ОУ диплом",            C["blue"]),
        ("ОУ мэргэжлийн зэргийн хөтөлбөрийн оюутны тоо",      "🏅 ОУ мэргэжлийн зэрэг", C["blue"]),
        ("Үүнээс эмэгтэй оюутны тоо",                          "👩 Эмэгтэй оюутан",      C["blue"]),
        ("Үүнээс орон нутгийн оюутны тоо",                     "🏘 Орон нутгийн",         C["blue"]),
        ("Үүнээс гадаад оюутны тоо",                           "✈️ Гадаад оюутан",        C["blue"]),
        ("Тэтгэлэг хүртсэн суралцагчийн тоо",                  "🏆 Тэтгэлэгт",           C["blue"]),
    ]

    kpi_cols_sd = st.columns(4)
    for i, (met, lbl, clr) in enumerate(count_kpis_sd):
        v = sdv_prog_total(met, CURRENT_YEAR, PROG_IDX)
        val_str = str(int(v)) if v is not None else "—"
        kpi_cols_sd[i % 4].markdown(f"""
<div style='background:#0a1428;border:1px solid #162040;border-radius:10px;
padding:12px 10px;text-align:center;margin-bottom:8px;border-top:2px solid {clr};'>
    <div style='color:{clr};font-size:22px;font-weight:700;'>{val_str}</div>
    <div style='color:#ffffff;font-size:14px;margin-top:3px;'>{lbl}</div>
</div>""", unsafe_allow_html=True)

    # ── SECTION B: Хувийн KPI трендийн графикууд ──
    st.markdown("<div class='section-title'>📈 Хувийн KPI үзүүлэлтүүдийн трендийн график — Бодит ба Зорилт</div>", unsafe_allow_html=True)

    PCT_METRICS = [
        ("Нийт оюутны тоонд гадаад оюутны эзлэх хувь",          "Гадаад оюутны эзлэх хувь",                         C["blue"]),
        ("Тэтгэлэг хүртсэн оюутны нийт суралцагчдад эзлэх хувь","Тэтгэлэгт оюутны эзлэх хувь",                      C["green"]),
        ("Гадаадад суралцах хөтөлбөрт хамрагдсан оюутны хувь",  "Гадаадад суралцах хөтөлбөрт хамрагдсан оюутны хувь",C["purple"]),
    ]

    pc1, pc2, pc3 = st.columns(3)
    pct_cols_list = [pc1, pc2, pc3]

    for i, (met, lbl, clr) in enumerate(PCT_METRICS):
        yrs_p, vals_p = sdv_pct_series(met)
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
        tp["yaxis"]["tickformat"] = ".1%"
        fig_p.update_layout(**tp)
        with pct_cols_list[i]:
            with st.container(border=True):
                st.plotly_chart(fig_p, use_container_width=True)
                
# ── SECTION C: Нийт суралцагчдын бүрэлдэхүүн (2026) ──
    st.markdown("<div class='section-title'>🥧 2026 оны нийт суралцагчдын бүрэлдэхүүн</div>", unsafe_allow_html=True)

    BLUE_PALETTE = ["#1E90FF", "#4DB8FF", "#0A4A8A", "#00BFFF", "#0066CC", "#63CFFF"]

    pie1, pie2, pie3 = st.columns(3)

    with pie1:
        prog_type_labels = ["Үндсэн хөтөлбөр", "Цагийн хөтөлбөр", "Цахим хөтөлбөр"]
        prog_type_metrics = [
            "Үндсэн хөтөлбөрийн суралцагчийн тоо",
            "Цагийн хөтөлбөрийн суралцагчийн тоо",
            "Цахимаар хэрэгжиж буй хөтөлбөрийн суралцагчийн тоо",
        ]
        prog_type_vals = [sdv_grand_total(m, CURRENT_YEAR) or 0 for m in prog_type_metrics]
        fig_pie_type = go.Figure(go.Pie(
            labels=prog_type_labels, values=prog_type_vals, hole=0.52,
            marker=dict(colors=BLUE_PALETTE[:3], line=dict(color=C["bg"], width=2)),
            textinfo="label+percent+value", textfont=dict(color=C["text"], size=10),
            insidetextorientation="radial",
        ))
        t_pt = dict(**theme(300))
        t_pt["title"] = dict(text="Хөтөлбөрийн төрлийн бүрэлдэхүүн", font=dict(color=C["white"], size=12))
        t_pt["showlegend"] = False
        fig_pie_type.update_layout(**t_pt)
        with st.container(border=True):
            st.plotly_chart(fig_pie_type, use_container_width=True)

    with pie2:
        total_2026  = sdv_grand_total("Үндсэн + цагийн + цахим суралцагчийн тоо", CURRENT_YEAR) or 1
        female_2026 = sdv_grand_total("Үүнээс эмэгтэй оюутны тоо", CURRENT_YEAR) or 0
        male_2026   = max(total_2026 - female_2026, 0)
        fig_pie_gender = go.Figure(go.Pie(
            labels=["Эмэгтэй", "Эрэгтэй"], values=[female_2026, male_2026], hole=0.52,
            marker=dict(colors=["#4DB8FF", "#0A4A8A"], line=dict(color=C["bg"], width=2)),
            textinfo="label+percent+value", textfont=dict(color=C["text"], size=10),
        ))
        t_pg = dict(**theme(300))
        t_pg["title"] = dict(text="Хүйсийн бүрэлдэхүүн", font=dict(color=C["white"], size=12))
        t_pg["showlegend"] = False
        fig_pie_gender.update_layout(**t_pg)
        with st.container(border=True):
            st.plotly_chart(fig_pie_gender, use_container_width=True)

    with pie3:
        total_v   = sdv_grand_total("Үндсэн + цагийн + цахим суралцагчийн тоо", CURRENT_YEAR) or 1
        local_v   = sdv_grand_total("Үүнээс орон нутгийн оюутны тоо", CURRENT_YEAR) or 0
        foreign_v = sdv_grand_total("Үүнээс гадаад оюутны тоо", CURRENT_YEAR) or 0
        domestic_v = max(total_v - local_v - foreign_v, 0)
        fig_pie_origin = go.Figure(go.Pie(
            labels=["Нийслэлийн", "Орон нутгийн", "Гадаад"],
            values=[domestic_v, local_v, foreign_v], hole=0.52,
            marker=dict(colors=["#1E90FF", "#00BFFF", "#0066CC"], line=dict(color=C["bg"], width=2)),
            textinfo="label+percent+value", textfont=dict(color=C["text"], size=10),
            insidetextorientation="radial",
        ))
        t_po = dict(**theme(300))
        t_po["title"] = dict(text="Гарал үүслийн бүрэлдэхүүн", font=dict(color=C["white"], size=12))
        t_po["showlegend"] = False
        fig_pie_origin.update_layout(**t_po)
        with st.container(border=True):
            st.plotly_chart(fig_pie_origin, use_container_width=True)

    # ── SECTION D: Хөтөлбөр + курсын жилийн задаргаа ──
    st.markdown(f"<div class='section-title'>📋 Хөтөлбөр: {SELECTED_PROG} — 2026 оны курсын задаргаа</div>", unsafe_allow_html=True)

    course_vals_total   = sdv_course_breakdown("Үндсэн + цагийн + цахим суралцагчийн тоо", CURRENT_YEAR, PROG_IDX)
    course_vals_undsen  = sdv_course_breakdown("Үндсэн хөтөлбөрийн суралцагчийн тоо", CURRENT_YEAR, PROG_IDX)
    course_vals_tsagiin = sdv_course_breakdown("Цагийн хөтөлбөрийн суралцагчийн тоо", CURRENT_YEAR, PROG_IDX)
    course_vals_tsakhim = sdv_course_breakdown("Цахимаар хэрэгжиж буй хөтөлбөрийн суралцагчийн тоо", CURRENT_YEAR, PROG_IDX)

    sec_c1, sec_c2 = st.columns([1, 2])

    with sec_c1:
        fig_course_pie = go.Figure(go.Pie(
            labels=COURSES, values=course_vals_total, hole=0.50,
            marker=dict(colors=BLUE_PALETTE[:5], line=dict(color=C["bg"], width=2)),
            textinfo="label+value+percent", textfont=dict(color=C["text"], size=10),
            insidetextorientation="radial",
        ))
        t_cp = dict(**theme(300))
        t_cp["title"] = dict(text="Курсын жилийн бүрэлдэхүүн (2026)", font=dict(color=C["white"], size=12))
        t_cp["showlegend"] = False
        fig_course_pie.update_layout(**t_cp)
        with st.container(border=True):
            st.plotly_chart(fig_course_pie, use_container_width=True)

    with sec_c2:
        fig_course_stk = go.Figure()
        for lbl, vals, clr in [
            ("Үндсэн", course_vals_undsen,  "#1E90FF"),
            ("Цагийн", course_vals_tsagiin, "#4DB8FF"),
            ("Цахим",  course_vals_tsakhim, "#0A4A8A"),
        ]:
            fig_course_stk.add_trace(go.Bar(
                x=COURSES, y=vals, name=lbl,
                marker=dict(color=clr, cornerradius=6),
                text=[str(int(v)) for v in vals], textposition="inside",
                textfont=dict(color=C["white"], size=10),
            ))
        t_cs = dict(**theme(300))
        t_cs["title"] = dict(text=f"Курсын жилийн хөтөлбөрийн бүрэлдэхүүн — {SELECTED_PROG} (2026)",
                              font=dict(color=C["white"], size=12))
        t_cs["barmode"] = "stack"
        t_cs["xaxis"]["tickfont"] = dict(size=11)
        fig_course_stk.update_layout(**t_cs)
        with st.container(border=True):
            st.plotly_chart(fig_course_stk, use_container_width=True)

# ── SECTION E: Хөтөлбөр хоорондын харьцуулалт (2026) ──
    st.markdown("<div class='section-title'>🏛️ Хөтөлбөр хоорондын харьцуулсан үзүүлэлтүүд (2026)</div>", unsafe_allow_html=True)

    prog_compare_opts = {
        "Нийт суралцагчдын тоо":     "Үндсэн + цагийн + цахим суралцагчийн тоо",
        "Үндсэн хөтөлбөрийн тоо":    "Үндсэн хөтөлбөрийн суралцагчийн тоо",
        "Цагийн хөтөлбөрийн тоо":    "Цагийн хөтөлбөрийн суралцагчийн тоо",
        "Цахим хөтөлбөрийн тоо":     "Цахимаар хэрэгжиж буй хөтөлбөрийн суралцагчийн тоо",
        "Гадаад хэлний тоо":          "Гадаад хэлээр явуулах хөтөлбөрийн суралцагчийн тоо",
        "Хамтарсан хөтөлбөрийн тоо": "Хамтарсан хөтөлбөрийн суралцагчийн тоо",
        "ОУ дипломтой тоо":           "ОУ дипломтой хөтөлбөрийн суралцагчийн тоо",
        "Эмэгтэй оюутны тоо":         "Үүнээс эмэгтэй оюутны тоо",
        "Орон нутгийн оюутны тоо":    "Үүнээс орон нутгийн оюутны тоо",
        "Гадаад оюутны тоо":          "Үүнээс гадаад оюутны тоо",
        "Тэтгэлэгт оюутны тоо":       "Тэтгэлэг хүртсэн суралцагчийн тоо",
    }

    sel_pc = st.selectbox("Харьцуулах үзүүлэлт сонгох:", list(prog_compare_opts.keys()), key="prog_compare_sel")
    sel_met_pc = prog_compare_opts[sel_pc]

    prog_vals_pc = [sdv_prog_total(sel_met_pc, CURRENT_YEAR, i) or 0 for i in range(len(PROGRAMS_D))]
    avg_pc = round(sum(prog_vals_pc) / max(len([v for v in prog_vals_pc if v > 0]), 1), 1)

    fig_pc = go.Figure(go.Bar(
        x=PROGRAMS_D, y=prog_vals_pc,
        marker=dict(
            color="#118DFF",
            line=dict(color=C["bg"], width=0.5),
            cornerradius=8
        ),
        text=[str(v) for v in prog_vals_pc], textposition="outside",
        textfont=dict(color=C["text"], size=10),
    ))
    t_pc = dict(**theme(360))
    t_pc["title"] = dict(text=f"Хөтөлбөр тус бүрийн {sel_pc} (2026)",
                          font=dict(color=C["white"], size=12))
    t_pc["xaxis"]["tickfont"] = dict(size=9)
    t_pc["xaxis"]["tickangle"] = -35
    t_pc["margin"]["b"] = 100
    fig_pc.update_layout(**t_pc)
    fig_pc.add_hline(y=avg_pc, line_dash="dash", line_color="#ff4d4d", line_width=1.5,
        annotation_text=f"Дундаж: {avg_pc}",
        annotation_position="top right", annotation_font=dict(color="#ff4d4d", size=11))
    with st.container(border=True):
        st.plotly_chart(fig_pc, use_container_width=True)

    # ── SECTION F: Heatmap — бүх хөтөлбөр × үзүүлэлт (2026) ──
    st.markdown("<div class='section-title'>🔥 Хөтөлбөр × Үзүүлэлтийн heatmap (2026)</div>", unsafe_allow_html=True)

    hm_metrics_sd = [
        ("Үндсэн + цагийн + цахим суралцагчийн тоо",            "Нийт"),
        ("Үндсэн хөтөлбөрийн суралцагчийн тоо",                 "Үндсэн"),
        ("Цагийн хөтөлбөрийн суралцагчийн тоо",                 "Цагийн"),
        ("Цахимаар хэрэгжиж буй хөтөлбөрийн суралцагчийн тоо", "Цахим"),
        ("Гадаад хэлээр явуулах хөтөлбөрийн суралцагчийн тоо", "Гадаад хэл"),
        ("Хамтарсан хөтөлбөрийн суралцагчийн тоо",              "Хамтарсан"),
        ("ОУ дипломтой хөтөлбөрийн суралцагчийн тоо",           "ОУ диплом"),
        ("Үүнээс эмэгтэй оюутны тоо",                           "Эмэгтэй"),
        ("Үүнээс гадаад оюутны тоо",                            "Гадаад"),
        ("Тэтгэлэг хүртсэн суралцагчийн тоо",                   "Тэтгэлэгт"),
    ]

    hm_z, hm_y = [], []
    for met, lbl in hm_metrics_sd:
        hm_z.append([sdv_prog_total(met, CURRENT_YEAR, i) or 0 for i in range(len(PROGRAMS_D))])
        hm_y.append(lbl)

    prog_short = [p[:8] + ".." if len(p) > 8 else p for p in PROGRAMS_D]

    fig_hm_sd = go.Figure(go.Heatmap(
        z=hm_z, x=prog_short, y=hm_y,
        colorscale=[[0, "#080e1c"], [0.3, "#0d2a5a"], [0.6, "#1a5299"], [1.0, "#00d4ff"]],
        text=[[str(int(v)) for v in row] for row in hm_z],
        texttemplate="%{text}", textfont=dict(color=C["white"], size=9),
        showscale=True, colorbar=dict(tickfont=dict(color=C["text"]), outlinecolor=C["grid"], outlinewidth=1),
    ))
    t_hm_sd = dict(**theme(400))
    t_hm_sd["title"] = dict(text="Хөтөлбөр × Үзүүлэлтийн heatmap (2026)", font=dict(color=C["white"], size=12))
    t_hm_sd["xaxis"]["tickfont"] = dict(size=9)
    t_hm_sd["xaxis"]["tickangle"] = -30
    t_hm_sd["yaxis"]["tickfont"] = dict(size=10)
    t_hm_sd["margin"]["l"] = 100
    t_hm_sd["margin"]["b"] = 100
    fig_hm_sd.update_layout(**t_hm_sd)
    with st.container(border=True):
        st.plotly_chart(fig_hm_sd, use_container_width=True)
# ============================================================
# PAGE 5 — СУДАЛГАА, ТӨСӨЛ ХӨТӨЛБӨР
# ============================================================
elif st.session_state.page == "res":

    RDEPTS = ["БУТ","МКТ","МСМТ","НББТ","ОУАЖССИ","ОУНББСМИ","ОУС","СДСТ","СУТ","СШУТ","ЭкТ","ЭнТИнс","ЭЗТ"]

    def rgv(metric, year, dept):
        r = dfr[(dfr["Үзүүлэлт"] == metric) & (dfr["Он"] == year)]
        return r.iloc[0][dept] if not r.empty else None

    def rgseries(metric, dept):
        s = dfr[dfr["Үзүүлэлт"] == metric].sort_values("Он")
        return list(s["Он"]), list(s[dept])

        # ── SECTION B: 2026 оны тоон KPI товчлуур ──
    st.markdown("<div class='section-title'>🔢 2026 оны тоон үзүүлэлтүүд</div>", unsafe_allow_html=True)

    TOP_COUNT_KPIS = [
        ("Эрдэм шинжилгээний бүтээлийн тоо",              "📄 ЭШ бүтээл",        C["blue"]),
        ("Эрдэм шинжилгээний ажилтны тоо",                "👩‍🔬 ЭШ ажилтан",      C["blue"]),
        ("Эрдэм шинжилгээний бүтээлд оролцсон багшийн тоо","👨‍🏫 ЭШ бүтээлд оролцсон багш",   C["blue"]),
        ("ОУ импакт өндөртэй сэтгүүлд нийтлүүлсэн бүтээлийн тоо", "⭐ ОУ импакт өндөртэй сэтгүүл нийтлүүлсэн", C["blue"]),
        ("ОУ сэтгүүлд нийтлүүлсэн бүтээлийн тоо",         "📰 ОУ сэтгүүлд нийтлүүлсэн",       C["blue"]),
        ("Гадаадын эрдэмтэдтэй хамтарсан бүтээлийн тоо",  "🌍 Гадаадын эрдэмтэдтэй хамтарсан бүтээл",        C["blue"]),
        ("Эшлэлийн тоо",                                   "🔗 Эшлэлийн тоо",            C["blue"]),
        ("Хамтарсан судалгаа, төслийн тоо",                "🤝 Хамтарсан судалгаа", C["blue"]),
    ]

    kpi_r_cols = st.columns(4)
    for i, (met, lbl, clr) in enumerate(TOP_COUNT_KPIS):
        v = rgv(met, CURRENT_YEAR, D)
        val_str = str(int(v)) if v is not None else "—"
        kpi_r_cols[i % 4].markdown(f"""
<div style='background:#0a1428;border:1px solid #162040;border-radius:10px;
padding:12px 10px;text-align:center;margin-bottom:8px;border-top:2px solid {clr};'>
    <div style='color:{clr};font-size:26px;font-weight:700;'>{val_str}</div>
    <div style='color:#ffffff;font-size:14px;margin-top:3px;'>{lbl}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("")

    # 2-р мөр KPI
    BOT_COUNT_KPIS = [
        ("Хэрэгжүүлсэн төсөл, хөтөлбөрийн тоо",                         "📋 Хэрэгжсэн төсөл",     C["blue"]),
        ("Бойжуулсан гарааны компаний тоо",                              "🚀 Гарааны компани",       C["blue"]),
        ("Патент, лицензийн гэрээ, зохиогчийн эрхийн гэрчилгээний тоо", "📜 Патент/Лиценз",         C["blue"]),
        ("БССА-аас санаачлан хэрэгжүүлсэн төсөл, хөтөлбөрийн тоо",     "🏛️ БССА санаачлага",     C["blue"]),
    ]

    kpi_r_cols2 = st.columns(4)
    for i, (met, lbl, clr) in enumerate(BOT_COUNT_KPIS):
        v = rgv(met, CURRENT_YEAR, D)
        val_str = str(int(v)) if v is not None else "—"
        kpi_r_cols2[i % 4].markdown(f"""
<div style='background:#0a1428;border:1px solid #162040;border-radius:10px;
padding:12px 10px;text-align:center;margin-bottom:8px;border-top:2px solid {clr};'>
    <div style='color:{clr};font-size:26px;font-weight:700;'>{val_str}</div>
    <div style='color:#ffffff;font-size:14px;margin-top:3px;'>{lbl}</div>
</div>""", unsafe_allow_html=True)
    # ── SECTION A: Чухал хувийн KPI товчлуур (2026 + trend) ──
    st.markdown("<div class='section-title'>📈 Хувийн KPI үзүүлэлтүүд — 2026 ба Зорилтын трендийн график</div>", unsafe_allow_html=True)

    PCT_METRICS_R = [
        ("Гадаадтай хамтарсан бүтээлийн хувь",    "🌍 Гадаадтай хамтарсан %",  C["blue"]),
        ("Судалгааны бүтээмж (дундаж)",             "📊 Судалгааны бүтээмж",      C["teal"]),
        ("Эшлэлийн хэмжээ (дундаж)",               "📰 Эшлэлийн хэмжээ",         C["purple"]),
        ("Захиалагчын сэтгэл ханамжийн хувь",      "😊 Захиалагчын сэтгэл ханамж", C["green"]),
    ]

    # Хувийн trend графикууд — бодит + зорилт
    tr_c1, tr_c2 = st.columns(2)
    tr_cycle = [tr_c1, tr_c2, tr_c1, tr_c2]
    for i, (met, lbl, clr) in enumerate(PCT_METRICS_R):
        yrs_r, vals_r = rgseries(met, D)
        fig_r = go.Figure()
        hx = [y for y, v in zip(yrs_r, vals_r) if y <= CURRENT_YEAR and v is not None]
        hy = [v for y, v in zip(yrs_r, vals_r) if y <= CURRENT_YEAR and v is not None]
        fx = [y for y, v in zip(yrs_r, vals_r) if y > CURRENT_YEAR and v is not None]
        fy = [v for y, v in zip(yrs_r, vals_r) if y > CURRENT_YEAR and v is not None]
        fig_r.add_trace(go.Scatter(x=hx, y=hy, mode="lines+markers", name="Бодит",
            line=dict(color=clr, width=2.5), marker=dict(size=7, color=clr)))
        if fx and hx:
            fig_r.add_trace(go.Scatter(x=[hx[-1]] + fx, y=[hy[-1]] + fy, mode="lines+markers",
                name="Зорилт", line=dict(color=C["target"], width=2, dash="dot"),
                marker=dict(size=7, color=C["target"], symbol="diamond")))
        if CURRENT_YEAR in yrs_r:
            fig_r.add_vline(x=CURRENT_YEAR, line_dash="dash",
                            line_color="rgba(255,255,255,0.2)",
                            annotation_text="2026",
                            annotation_font_color="rgba(255,255,255,0.4)",
                            annotation_font_size=10)
        tr = dict(**theme(280))
        tr["title"] = dict(text=lbl, font=dict(color=C["white"], size=12))
        tr["yaxis"]["tickformat"] = ".0%"
        fig_r.update_layout(**tr)
        with tr_cycle[i]:
            with st.container(border=True):
                st.plotly_chart(fig_r, use_container_width=True)

# ── SECTION C: Тэнхимийн харьцуулалт — Баганан диаграм ──
    st.markdown("<div class='section-title'>🏛️ Тэнхимийн харьцуулсан үзүүлэлтүүд (2026)</div>", unsafe_allow_html=True)

    res_dept_opts = {
        # Тоон үзүүлэлтүүд
        "ЭШ бүтээлийн тоо":                "тоо|Эрдэм шинжилгээний бүтээлийн тоо",
        "ЭШ ажилтны тоо":                  "тоо|Эрдэм шинжилгээний ажилтны тоо",
        "ЭШ-д оролцсон багшийн тоо":       "тоо|Эрдэм шинжилгээний бүтээлд оролцсон багшийн тоо",
        "ОУ импакт бүтээлийн тоо":         "тоо|ОУ импакт өндөртэй сэтгүүлд нийтлүүлсэн бүтээлийн тоо",
        "ОУ сэтгүүл бүтээлийн тоо":        "тоо|ОУ сэтгүүлд нийтлүүлсэн бүтээлийн тоо",
        "Гадаадтай хамтарсан бүтээлийн тоо":"тоо|Гадаадын эрдэмтэдтэй хамтарсан бүтээлийн тоо",
        "Эшлэлийн тоо":                    "тоо|Эшлэлийн тоо",
        "Хамтарсан судалгаа/төслийн тоо":  "тоо|Хамтарсан судалгаа, төслийн тоо",
        "Хэрэгжсэн төсөл/хөтөлбөрийн тоо":"тоо|Хэрэгжүүлсэн төсөл, хөтөлбөрийн тоо",
        "Патент/лицензийн тоо":            "тоо|Патент, лицензийн гэрээ, зохиогчийн эрхийн гэрчилгээний тоо",
        "Түншлэгч оролцогчдын тоо":        "тоо|Түншлэгч талуудтай хамтарсан төсөлд оролцогчдын тоо",
        "Бойжуулсан гарааны компани":       "тоо|Бойжуулсан гарааны компаний тоо",
        # Хувийн үзүүлэлтүүд
        "Гадаадтай хамтарсан бүтээлийн хувь":  "хувь|Гадаадтай хамтарсан бүтээлийн хувь",
        "Судалгааны бүтээмж (дундаж)":          "хувь|Судалгааны бүтээмж (дундаж)",
        "Эшлэлийн хэмжээ (дундаж)":            "хувь|Эшлэлийн хэмжээ (дундаж)",
        "Захиалагчын сэтгэл ханамжийн хувь":   "хувь|Захиалагчын сэтгэл ханамжийн хувь",
    }

    sel_r = st.selectbox("Тэнхимээр харьцуулах үзүүлэлт:", list(res_dept_opts.keys()), key="res_dept_sel")
    kind_r, sel_met_r = res_dept_opts[sel_r].split("|")

    if kind_r == "хувь":
        vals_rd = [round((rgv(sel_met_r, CURRENT_YEAR, d) or 0) * 100, 2) for d in RDEPTS]
        avg_rd  = round(sum(vals_rd) / max(len([v for v in vals_rd if v > 0]), 1), 2)
        text_rd = [f"{v}%" for v in vals_rd]
        avg_text_rd  = f"Дундаж: {avg_rd}%"
        tick_suffix_rd = "%"
    else:
        vals_rd = [int(rgv(sel_met_r, CURRENT_YEAR, d) or 0) for d in RDEPTS]
        avg_rd  = round(sum(vals_rd) / max(len([v for v in vals_rd if v > 0]), 1), 1)
        text_rd = [str(v) for v in vals_rd]
        avg_text_rd  = f"Дундаж: {avg_rd}"
        tick_suffix_rd = ""

    fig_rd = go.Figure(go.Bar(
            x=RDEPTS, y=vals_rd,
            marker=dict(
                color="#118DFF",
                line=dict(color=C["bg"], width=0.5),
                cornerradius=8
            ),
            text=text_rd, textposition="outside",
            textfont=dict(color=C["text"], size=10),
        ))
    t_rd = dict(**theme(340))
    t_rd["title"] = dict(text=f"Тэнхим тус бүрийн {sel_r} (2026)", font=dict(color=C["white"], size=12))
    t_rd["xaxis"]["tickfont"] = dict(size=10)
    t_rd["yaxis"]["ticksuffix"] = tick_suffix_rd
    fig_rd.update_layout(**t_rd)
    fig_rd.add_hline(y=avg_rd, line_dash="dash", line_color="#ff4d4d", line_width=1.5,
        annotation_text=avg_text_rd,
        annotation_position="top right",
        annotation_font=dict(color="#ff4d4d", size=11))
    with st.container(border=True):
        st.plotly_chart(fig_rd, use_container_width=True)

# ── SECTION D: Дугуй диаграм — бүрэлдэхүүн ──
    st.markdown("<div class='section-title'>🔵 Судалгааны бүрэлдэхүүний харьцаа (2026)</div>", unsafe_allow_html=True)

    BLUE_PALETTE = ["#1E90FF", "#4DB8FF", "#0A4A8A", "#00BFFF", "#0066CC", "#63CFFF"]

    pie_r1, pie_r2, pie_r3 = st.columns(3)

    with pie_r1:
        pie_l1 = ["ОУ импакт", "ОУ сэтгүүл", "Гадаадтай хамтарсан", "Бусад"]
        ou_imp  = rgv("ОУ импакт өндөртэй сэтгүүлд нийтлүүлсэн бүтээлийн тоо", CURRENT_YEAR, D) or 0
        ou_sut  = rgv("ОУ сэтгүүлд нийтлүүлсэн бүтээлийн тоо", CURRENT_YEAR, D) or 0
        gad_but = rgv("Гадаадын эрдэмтэдтэй хамтарсан бүтээлийн тоо", CURRENT_YEAR, D) or 0
        niylt   = rgv("Эрдэм шинжилгээний бүтээлийн тоо", CURRENT_YEAR, D) or 0
        busa    = max(niylt - ou_imp - ou_sut, 0)
        pie_v1  = [ou_imp, ou_sut, gad_but, busa]
        fig_pr1 = go.Figure(go.Pie(
            labels=pie_l1, values=pie_v1, hole=0.52,
            marker=dict(colors=BLUE_PALETTE[:4], line=dict(color=C["bg"], width=2)),
            textinfo="label+percent+value", textfont=dict(color=C["text"], size=10),
            insidetextorientation="radial",
        ))
        t_pr1 = dict(**theme(300))
        t_pr1["title"] = dict(text="ЭШ бүтээлийн ангиллын харьцаа", font=dict(color=C["white"], size=12))
        t_pr1["showlegend"] = False
        fig_pr1.update_layout(**t_pr1)
        with st.container(border=True):
            st.plotly_chart(fig_pr1, use_container_width=True)

    with pie_r2:
        pie_l2 = ["Хэрэгжсэн төсөл", "Хамтарсан судалгаа", "БССА санаачлага", "Нийгмийн чиглэлт"]
        pie_v2 = [
            rgv("Хэрэгжүүлсэн төсөл, хөтөлбөрийн тоо", CURRENT_YEAR, D) or 0,
            rgv("Хамтарсан судалгаа, төслийн тоо", CURRENT_YEAR, D) or 0,
            rgv("БССА-аас санаачлан хэрэгжүүлсэн төсөл, хөтөлбөрийн тоо", CURRENT_YEAR, D) or 0,
            rgv("Нийгэм эдийн засгийн асуудлыг шийдэхэд чиглэсэн төслийн тоо", CURRENT_YEAR, D) or 0,
        ]
        fig_pr2 = go.Figure(go.Pie(
            labels=pie_l2, values=pie_v2, hole=0.52,
            marker=dict(colors=BLUE_PALETTE[:4], line=dict(color=C["bg"], width=2)),
            textinfo="label+percent+value", textfont=dict(color=C["text"], size=10),
            insidetextorientation="radial",
        ))
        t_pr2 = dict(**theme(300))
        t_pr2["title"] = dict(text="Төсөл хөтөлбөрийн ангиллын харьцаа", font=dict(color=C["white"], size=12))
        t_pr2["showlegend"] = False
        fig_pr2.update_layout(**t_pr2)
        with st.container(border=True):
            st.plotly_chart(fig_pr2, use_container_width=True)

    with pie_r3:
        pie_l3 = ["ЭШ ажилтан", "Оролцсон багш", "Төсөл багш", "Түншлэгч багш"]
        pie_v3 = [
            rgv("Эрдэм шинжилгээний ажилтны тоо", CURRENT_YEAR, D) or 0,
            rgv("Эрдэм шинжилгээний бүтээлд оролцсон багшийн тоо", CURRENT_YEAR, D) or 0,
            rgv("Төсөл, хөтөлбөр хэрэгжүүлсэн багш ажилтны тоо", CURRENT_YEAR, D) or 0,
            rgv("Түншлэгч талуудтай хамтарсан төсөлд хамрагдсан багшийн тоо", CURRENT_YEAR, D) or 0,
        ]
        fig_pr3 = go.Figure(go.Pie(
            labels=pie_l3, values=pie_v3, hole=0.52,
            marker=dict(colors=BLUE_PALETTE[:4], line=dict(color=C["bg"], width=2)),
            textinfo="label+percent+value", textfont=dict(color=C["text"], size=10),
            insidetextorientation="radial",
        ))
        t_pr3 = dict(**theme(300))
        t_pr3["title"] = dict(text="Судалгааны хүн хүчний бүрэлдэхүүн", font=dict(color=C["white"], size=12))
        t_pr3["showlegend"] = False
        fig_pr3.update_layout(**t_pr3)
        with st.container(border=True):
            st.plotly_chart(fig_pr3, use_container_width=True)

    # ── SECTION E: Heatmap — тэнхим × үзүүлэлт ──
    st.markdown("<div class='section-title'>🔥 Тэнхим × Судалгааны үзүүлэлтийн heatmap (2026)</div>", unsafe_allow_html=True)

    hm_r_metrics = [
        ("Эрдэм шинжилгээний бүтээлийн тоо",                          "ЭШ бүтээл"),
        ("Эрдэм шинжилгээний ажилтны тоо",                            "ЭШ ажилтан"),
        ("ОУ импакт өндөртэй сэтгүүлд нийтлүүлсэн бүтээлийн тоо",    "ОУ импакт"),
        ("ОУ сэтгүүлд нийтлүүлсэн бүтээлийн тоо",                    "ОУ сэтгүүл"),
        ("Гадаадын эрдэмтэдтэй хамтарсан бүтээлийн тоо",              "Гадаадтай"),
        ("Эшлэлийн тоо",                                               "Эшлэл"),
        ("Хамтарсан судалгаа, төслийн тоо",                            "Хамтарсан"),
        ("Хэрэгжүүлсэн төсөл, хөтөлбөрийн тоо",                      "Хэрэгжсэн төсөл"),
        ("Патент, лицензийн гэрээ, зохиогчийн эрхийн гэрчилгээний тоо","Патент"),
        ("Түншлэгч талуудтай хамтарсан төсөлд оролцогчдын тоо",        "Түншлэгч"),
    ]

    hm_r_z = []
    hm_r_y = []
    for met, lbl in hm_r_metrics:
        row_v = [rgv(met, CURRENT_YEAR, d) or 0 for d in RDEPTS]
        hm_r_z.append(row_v)
        hm_r_y.append(lbl)

    fig_hm_r = go.Figure(go.Heatmap(
        z=hm_r_z, x=RDEPTS, y=hm_r_y,
        colorscale=[[0, "#080e1c"], [0.3, "#0d2a5a"], [0.6, "#1a5299"], [1.0, "#00d4ff"]],
        text=[[str(int(v)) for v in row] for row in hm_r_z],
        texttemplate="%{text}", textfont=dict(color=C["white"], size=10),
        showscale=True,
        colorbar=dict(tickfont=dict(color=C["text"]), outlinecolor=C["grid"], outlinewidth=1),
    ))
    t_hm_r = dict(**theme(380))
    t_hm_r["title"] = dict(text="Тэнхим × Судалгааны үзүүлэлтүүдийн heatmap (2026)",
                            font=dict(color=C["white"], size=12))
    t_hm_r["xaxis"]["tickfont"] = dict(size=10)
    t_hm_r["yaxis"]["tickfont"] = dict(size=10)
    t_hm_r["margin"]["l"] = 140
    fig_hm_r.update_layout(**t_hm_r)
    with st.container(border=True):
        st.plotly_chart(fig_hm_r, use_container_width=True)

# ── SECTION F: Стэк баганан диаграм ──
    st.markdown("<div class='section-title'>📊 Судалгааны үзүүлэлтүүдийн стэк диаграм (2026)</div>", unsafe_allow_html=True)

    stk_r_tab = st.radio("Харах:", ["Бүтээл & Эшлэл", "Төсөл & Хамтын ажиллагаа"],
                         horizontal=True, label_visibility="collapsed", key="res_stk_tab")

    if stk_r_tab == "Бүтээл & Эшлэл":
        stk_items = [
            ("Эрдэм шинжилгээний бүтээлийн тоо",                       "ЭШ бүтээл",  "#1E90FF"),
            ("ОУ импакт өндөртэй сэтгүүлд нийтлүүлсэн бүтээлийн тоо", "ОУ импакт",  "#4DB8FF"),
            ("ОУ сэтгүүлд нийтлүүлсэн бүтээлийн тоо",                 "ОУ сэтгүүл", "#0A4A8A"),
            ("Гадаадын эрдэмтэдтэй хамтарсан бүтээлийн тоо",           "Гадаадтай",  "#00BFFF"),
        ]
    else:
        stk_items = [
            ("Хэрэгжүүлсэн төсөл, хөтөлбөрийн тоо",                         "Хэрэгжсэн", "#1E90FF"),
            ("Хамтарсан судалгаа, төслийн тоо",                               "Хамтарсан", "#4DB8FF"),
            ("БССА-аас санаачлан хэрэгжүүлсэн төсөл, хөтөлбөрийн тоо",      "БССА",      "#0A4A8A"),
            ("Нийгэм эдийн засгийн асуудлыг шийдэхэд чиглэсэн төслийн тоо", "Нийгмийн",  "#00BFFF"),
        ]

    fig_stk_r = go.Figure()
    for met, lbl, clr in stk_items:
        vals_stk_r = [rgv(met, CURRENT_YEAR, d) or 0 for d in RDEPTS]
        fig_stk_r.add_trace(go.Bar(
            x=RDEPTS, y=vals_stk_r, name=lbl,
            marker=dict(color=clr, cornerradius=6),
        ))
    t_stk_r = dict(**theme(340))
    t_stk_r["title"] = dict(text=f"{stk_r_tab} — Тэнхимээр (2026)", font=dict(color=C["white"], size=12))
    t_stk_r["barmode"] = "stack"
    t_stk_r["xaxis"]["tickfont"] = dict(size=10)
    fig_stk_r.update_layout(**t_stk_r)
    with st.container(border=True):
        st.plotly_chart(fig_stk_r, use_container_width=True)
# ============================================================
# PAGE 6 — САНХҮҮ
# ============================================================
elif st.session_state.page == "fin":

    FDEPTS = ["БУТ","МКТ","МСМТ","НББТ","ОУАЖССИ","ОУНББСМИ","ОУС","СДСТ","СУТ","СШУТ","ЭкТ","ЭнТИнс","ЭЗТ"]
    CY = CURRENT_YEAR  # 2026

    def fgv(metric, year, dept):
        r = dff[(dff["Үзүүлэлт"]==metric)&(dff["Он"]==year)]
        return r.iloc[0][dept] if not r.empty else None

    def fgseries(metric, dept):
        s = dff[dff["Үзүүлэлт"]==metric].sort_values("Он")
        return list(s["Он"]), list(s[dept])

    def fmt_money(v):
        if v is None: return "—"
        if v >= 1_000_000_000: return f"₮{v/1_000_000_000:.1f}тэрбум"
        if v >= 1_000_000: return f"₮{v/1_000_000:.0f}сая"
        return f"₮{int(v):,}"

    # ── SECTION A: 2026 оны гол орлогын KPI badge ──
    st.markdown("<div class='section-title'>💰 2026 оны гол санхүүгийн үзүүлэлтүүд</div>", unsafe_allow_html=True)

    COUNT_FIN_KPIS = [
        ("Нийт орлого",                       "💎 Нийт орлого",              C["blue"]),
        ("Бакалаврын сургалтын орлого",        "🎓 Бакалаврын орлого",         C["blue"]),
        ("Судалгаа, эрдэм шинжилгээний орлого","🔬 Судалгааны орлого",          C["blue"]),
        ("Зэргийн бус сургалтын орлого",       "📚 Зэргийн бус орлого",        C["blue"]),
        ("Патентын орлого",                    "📜 Патентын орлого",            C["blue"]),
        ("Гарааны бизнесийн орлого",           "🚀 Гарааны бизнес",             C["blue"]),
        ("Хандиваар авсан санхүүжилт",         "🤝 Хандив",                    C["blue"]),
        ("Үйлдвэрлэл, худалдааны орлого",      "🏭 Үйлдвэрлэл, худалдаа",      C["blue"]),
    ]

    fin_cols = st.columns(4)
    for i, (met, lbl, clr) in enumerate(COUNT_FIN_KPIS):
        v = fgv(met, CY, D)
        val_str = fmt_money(v)
        fin_cols[i % 4].markdown(f"""
<div style='background:#0a1428;border:1px solid #162040;border-radius:10px;
padding:12px 10px;text-align:center;margin-bottom:8px;border-top:2px solid {clr};'>
    <div style='color:{clr};font-size:20px;font-weight:700;'>{val_str}</div>
    <div style='color:#ffffff;font-size:14px;margin-top:3px;'>{lbl}</div>
</div>""", unsafe_allow_html=True)

# ── SECTION B: Нийт орлогын бүрэлдэхүүн — Pie chart ──
    st.markdown("<div class='section-title'>🥧 2026 оны нийт орлогын бүрэлдэхүүн</div>", unsafe_allow_html=True)

    BLUE_PALETTE = ["#1E90FF", "#4DB8FF", "#0A4A8A", "#00BFFF", "#0066CC", "#63CFFF",
                    "#1565C0", "#42A5F5", "#1976D2", "#90CAF9"]

    pie_f1, pie_f2 = st.columns([1, 2])

    PIE_INCOME_METRICS = [
        ("Бакалаврын сургалтын орлого",         "Бакалаврын сургалт"),
        ("Үйлдвэрлэл, худалдааны орлого",       "Үйлдвэрлэл, худалдаа"),
        ("Патентын орлого",                     "Патентын орлого"),
        ("Судалгаа, эрдэм шинжилгээний орлого", "Судалгааны орлого"),
        ("Зэргийн бус сургалтын орлого",        "Зэргийн бус сургалт"),
        ("Хандиваар авсан санхүүжилт",          "Хандив"),
        ("Түншлэгч талуудтай хамтарсан төслийн ивээн тэтгэлэгийн мөнгөн дүн", "Түншлэгч тэтгэлэг"),
        ("Орлогын эх үүсвэрийг нэмэгдүүлэх үйл ажиллагааны орлого", "Орлогын эх үүсвэр"),
        ("Гарааны бизнесийн орлого",            "Гарааны бизнес"),
        ("Гадаад оюутаны сургалтын орлого",     "Гадаад оюутан"),
    ]

    with pie_f1:
        pie_labels = [lbl for _, lbl in PIE_INCOME_METRICS]
        pie_vals   = [fgv(met, CY, D) or 0 for met, _ in PIE_INCOME_METRICS]
        fig_pie_fin = go.Figure(go.Pie(
            labels=pie_labels, values=pie_vals, hole=0.52,
            marker=dict(colors=BLUE_PALETTE[:len(pie_labels)], line=dict(color=C["bg"], width=2)),
            textinfo="label+percent", textfont=dict(color=C["text"], size=10),
            insidetextorientation="radial",
        ))
        t_pf = dict(**theme(360))
        t_pf["title"] = dict(text="Орлогын эх үүсвэрийн харьцаа (2026)", font=dict(color=C["white"], size=12))
        t_pf["showlegend"] = False
        fig_pie_fin.update_layout(**t_pf)
        with st.container(border=True):
            st.plotly_chart(fig_pie_fin, use_container_width=True)

    with pie_f2:
        sorted_items = sorted(zip(pie_vals, pie_labels), reverse=True)
        s_vals, s_lbls = zip(*sorted_items) if sorted_items else ([], [])
        fig_bar_pie = go.Figure(go.Bar(
            x=list(s_vals), y=list(s_lbls), orientation="h",
            marker=dict(
                color="#1E90FF",
                line=dict(color=C["bg"], width=0.5),
                cornerradius=8
            ),
            text=[fmt_money(v) for v in s_vals],
            textposition="outside", textfont=dict(color=C["text"], size=10),
        ))
        t_bp = dict(**theme(360))
        t_bp["title"] = dict(text="Орлогын эх үүсвэр харьцуулалт (2026)", font=dict(color=C["white"], size=12))
        t_bp["margin"]["l"] = 220
        t_bp["xaxis"]["title"] = "₮"
        fig_bar_pie.update_layout(**t_bp)
        with st.container(border=True):
            st.plotly_chart(fig_bar_pie, use_container_width=True)

    # ── SECTION C: Хувийн KPI badge + Зорилтын трендийн графикууд ──
    st.markdown("<div class='section-title'>📈 Хувийн KPI үзүүлэлтүүд — 2026 ба Зорилтын трендийн график (2024–2031)</div>", unsafe_allow_html=True)

    PCT_FIN_KPIS = [
        ("СЭЗИС-ийн нийт орлогод эзлэх хувь",                      "🏛️ Нийт орлогод эзлэх хувь",    C["blue"]),
        ("Бакалаврын сургалтын орлогын нийт орлогод эзлэх хувь",    "🎓 Бакалаврын орлогын хувь",     C["teal"]),
        ("Судалгаа, эрдэм шинжилгээний орлогын нийт орлогод эзлэх хувь", "🔬 Судалгааны орлогын хувь", C["purple"]),
        ("Зэргийн бус сургалтын орлогын нийт орлогод эзлэх хувь",  "📚 Зэргийн бус орлогын хувь",    C["green"]),
        ("Гарааны бизнесийн нийт орлогод эзлэх хувь",              "🚀 Гарааны бизнесийн хувь",       C["orange"]),
        ("Гадаад оюутнаас олох орлогын нийт орлогод эзлэх хувь",   "🌍 Гадаад оюутны орлогын хувь",  C["pink"]),
        ("Тэнхимийн үйл ажиллагааны төсвийн эзлэх хувь",           "⚙️ Үйл ажиллагааны төсвийн хувь", C["teal"]),
        ("Цахим хөгжилд зарцуулсан төсвийн эзлэх хувь",            "💻 Цахим хөгжлийн төсвийн хувь", C["blue"]),
    ]

    # Хувийн KPI trend графикууд — 2024-2031 (2027+ зорилт)
    fc1, fc2 = st.columns(2)
    fc_cycle = [fc1, fc2, fc1, fc2, fc1, fc2, fc1, fc2]

    for i, (met, lbl, clr) in enumerate(PCT_FIN_KPIS):
        yrs_f, vals_f = fgseries(met, D)
        fig_f = go.Figure()
        hx = [y for y, v in zip(yrs_f, vals_f) if y <= CY and v is not None]
        hy = [v for y, v in zip(yrs_f, vals_f) if y <= CY and v is not None]
        fx = [y for y, v in zip(yrs_f, vals_f) if y > CY and v is not None]
        fy = [v for y, v in zip(yrs_f, vals_f) if y > CY and v is not None]
        fig_f.add_trace(go.Scatter(x=hx, y=hy, mode="lines+markers", name="Бодит",
            line=dict(color=clr, width=2.5), marker=dict(size=7, color=clr)))
        if fx and hx:
            fig_f.add_trace(go.Scatter(x=[hx[-1]]+fx, y=[hy[-1]]+fy, mode="lines+markers",
                name="Зорилт", line=dict(color=C["target"], width=2, dash="dot"),
                marker=dict(size=7, color=C["target"], symbol="diamond")))
        if CY in yrs_f:
            fig_f.add_vline(x=CY, line_dash="dash", line_color="rgba(255,255,255,0.2)",
                annotation_text="2026", annotation_font_color="rgba(255,255,255,0.4)",
                annotation_font_size=10)
        tf = dict(**theme(280))
        tf["title"] = dict(text=lbl, font=dict(color=C["white"], size=12))
        tf["yaxis"]["tickformat"] = ".1%"
        fig_f.update_layout(**tf)
        with fc_cycle[i]:
            with st.container(border=True):
                st.plotly_chart(fig_f, use_container_width=True)

# ── SECTION E+G: Тэнхимийн харьцуулалт ──
    st.markdown("<div class='section-title'>🏛️ Тэнхимийн харьцуулсан санхүүгийн үзүүлэлтүүд (2026)</div>", unsafe_allow_html=True)

    all_dept_opts = {
        "Нэг багшид ногдох судалгааны орлого":   ("мөнгө", "Нэг багшид ногдох судалгааны орлого"),
        "Тэнхимийн 1 багшид ногдох орлого":      ("мөнгө", "Тэнхимийн 1 багшид ногдох орлого"),
        "Багшийн хөгжилд зориулсан төсөв":       ("мөнгө", "Багшийн хөгжилд зориулсан төсөв"),
        "Цахим хөгжилд зарцуулсан төсөв":        ("мөнгө", "Цахим хөгжилд зарцуулсан төсөв"),
        "Нийт орлогод эзлэх хувь":               ("хувь", "СЭЗИС-ийн нийт орлогод эзлэх хувь"),
        "Бакалаврын орлогын хувь":                ("хувь", "Бакалаврын сургалтын орлогын нийт орлогод эзлэх хувь"),
        "Судалгааны орлогын хувь":                ("хувь", "Судалгаа, эрдэм шинжилгээний орлогын нийт орлогод эзлэх хувь"),
        "Зэргийн бус орлогын хувь":               ("хувь", "Зэргийн бус сургалтын орлогын нийт орлогод эзлэх хувь"),
        "Үйл ажиллагааны төсвийн хувь":           ("хувь", "Тэнхимийн үйл ажиллагааны төсвийн эзлэх хувь"),
        "Багшийн хөгжлийн төсвийн хувь":          ("хувь", "Багшийн хөгжилд зориулсан төсвийн эзлэх хувь"),
        "Цахим хөгжлийн төсвийн хувь":            ("хувь", "Цахим хөгжилд зарцуулсан төсвийн эзлэх хувь"),
        "Суралцагчийн үйл ажиллагааны хувь":      ("хувь", "Суралцагч дунд зохион байгуулсан үйл ажиллагааны зардлын эзлэх хувь"),
        "Гарааны бизнесийн орлогын хувь":         ("хувь", "Гарааны бизнесийн нийт орлогод эзлэх хувь"),
        "Гадаад оюутны орлогын хувь":             ("хувь", "Гадаад оюутнаас олох орлогын нийт орлогод эзлэх хувь"),
    }

    sel = st.selectbox("Тэнхимээр харьцуулах үзүүлэлт:", list(all_dept_opts.keys()), key="fin_dept_sel")
    kind, met = all_dept_opts[sel]

    if kind == "хувь":
        vals = [round((fgv(met, CY, d) or 0) * 100, 2) for d in FDEPTS]
        avg  = round(sum(vals) / max(len([v for v in vals if v > 0]), 1), 2)
        text = [f"{v}%" for v in vals]
        avg_text = f"Дундаж: {avg}%"
        tick_suffix = "%"
    else:
        vals = [fgv(met, CY, d) or 0 for d in FDEPTS]
        avg  = round(sum(vals) / max(len([v for v in vals if v > 0]), 1), 1)
        text = [fmt_money(v) for v in vals]
        avg_text = f"Дундаж: {fmt_money(avg)}"
        tick_suffix = ""

    fig_dept = go.Figure(go.Bar(
        x=FDEPTS, y=vals,
        marker=dict(
            color="#118DFF",
            line=dict(color=C["bg"], width=0.5),
            cornerradius=8
        ),
        text=text, textposition="outside", textfont=dict(color=C["text"], size=10),
    ))
    t_dept = dict(**theme(340))
    t_dept["title"] = dict(text=f"Тэнхим тус бүрийн {sel} (2026)", font=dict(color=C["white"], size=12))
    t_dept["xaxis"]["tickfont"] = dict(size=10)
    t_dept["yaxis"]["ticksuffix"] = tick_suffix
    fig_dept.update_layout(**t_dept)
    fig_dept.add_hline(y=avg, line_dash="dash", line_color="#ff4d4d", line_width=1.5,
        annotation_text=avg_text,
        annotation_position="top right", annotation_font=dict(color="#ff4d4d", size=11))
    with st.container(border=True):
        st.plotly_chart(fig_dept, use_container_width=True)

# ── SECTION F: Орлого vs Зардал харьцуулалт — 2026 тэнхимээр ──
    st.markdown("<div class='section-title'>⚖️ Орлого ба Төсвийн харьцуулалт тэнхимээр (2026)</div>", unsafe_allow_html=True)

    fig_ov = go.Figure()
    inc_vals  = [fgv("Суралцагч дунд зохион байгуулсан үйл ажиллагааны зардал", CY, d) or 0 for d in FDEPTS]
    exp_vals  = [fgv("Тэнхимийн үйл ажиллагааны төсөв", CY, d) or 0 for d in FDEPTS]
    tdev_vals = [fgv("Багшийн хөгжилд зориулсан төсөв", CY, d) or 0 for d in FDEPTS]
    dig_vals  = [fgv("Цахим хөгжилд зарцуулсан төсөв", CY, d) or 0 for d in FDEPTS]

    for lbl, vals_ov, clr in [
        ("Суралцагч үйл ажиллагааны зардал", inc_vals,  "#1E90FF"),
        ("Үйл ажиллагааны төсөв",            exp_vals,  "#4DB8FF"),
        ("Багшийн хөгжлийн төсөв",           tdev_vals, "#0A4A8A"),
        ("Цахим хөгжлийн төсөв",             dig_vals,  "#00BFFF"),
    ]:
        fig_ov.add_trace(go.Bar(
            x=FDEPTS, y=vals_ov, name=lbl,
            marker=dict(color=clr, cornerradius=6),
        ))

    t_ov = dict(**theme(360))
    t_ov["title"] = dict(text="Орлого ба Төсвийн харьцуулалт тэнхимээр (2026)", font=dict(color=C["white"], size=12))
    t_ov["barmode"] = "group"
    t_ov["xaxis"]["tickfont"] = dict(size=10)
    fig_ov.update_layout(**t_ov)
    with st.container(border=True):
        st.plotly_chart(fig_ov, use_container_width=True)
# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#162040;font-size:11px;padding:8px 0'>
СЭЗИС — Стратегийн KPI Хяналтын Систем | 2026
</div>""", unsafe_allow_html=True)
