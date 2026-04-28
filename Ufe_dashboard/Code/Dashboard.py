import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="СЭЗИС - Багшийн хөгжлийн KPI Хяналтын Самбар",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === DARK THEME CSS ===
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1528 50%, #0a1220 100%);
        color: #e0e8ff;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1528 0%, #091020 100%);
        border-right: 1px solid #1e3a6e;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] p { color: #a0b8e8 !important; }
    
    /* Header */
    .main-header {
        background: linear-gradient(90deg, #0d1f4a 0%, #1a2d6b 50%, #0d1f4a 100%);
        border: 1px solid #1e3a8a;
        border-radius: 12px;
        padding: 18px 24px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .header-title { color: #ffffff; font-size: 18px; font-weight: 700; }
    .header-subtitle { color: #7090d0; font-size: 13px; }
    
    /* Tab buttons */
    .tab-container {
        display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #0d1f4a, #1a2d5a) !important;
        color: #8aabdc !important;
        border: 1px solid #1e3a6e !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
        min-height: 38px !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1a3a7a, #2a4d8a) !important;
        color: #ffffff !important;
        border-color: #4a7acc !important;
    }
    .stButton > button:focus {
        background: linear-gradient(135deg, #1e4080, #2e5898) !important;
        color: #ffffff !important;
        border-color: #5a8adc !important;
        box-shadow: 0 0 0 2px rgba(90,138,220,0.4) !important;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #0d1f4a 0%, #1a2d5a 100%);
        border: 1px solid #1e3a6e;
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
        margin-bottom: 8px;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3a6adc, #00c8ff);
    }
    .metric-icon { font-size: 22px; margin-bottom: 6px; }
    .metric-value { color: #00d4ff; font-size: 32px; font-weight: 700; line-height: 1; }
    .metric-label { color: #7090c0; font-size: 12px; margin-top: 4px; }
    
    /* Section headers */
    .section-header {
        color: #4a9eff;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 16px 0 8px 0;
        border-bottom: 1px solid #1e3a6e;
        padding-bottom: 6px;
    }
    
    /* Chart container */
    .chart-box {
        background: linear-gradient(135deg, #0a1830 0%, #0d1f3a 100%);
        border: 1px solid #1e3a6e;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    /* Sidebar dept buttons */
    .sidebar-dept {
        background: #0d1528 !important;
        color: #8aabdc !important;
        border: 1px solid #1e3a6e !important;
        border-radius: 6px !important;
        padding: 6px 12px !important;
        font-size: 13px !important;
        width: 100% !important;
        text-align: left !important;
    }
    
    /* Plotly chart background fix */
    .js-plotly-plot { border-radius: 8px; }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0a0e1a; }
    ::-webkit-scrollbar-thumb { background: #1e3a6e; border-radius: 3px; }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: #0d1528 !important;
        color: #a0b8e8 !important;
        border-color: #1e3a6e !important;
    }
    
    [data-testid="stMetricValue"] { color: #00d4ff !important; }
    [data-testid="stMetricLabel"] { color: #7090c0 !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_excel("Taech_dev_cl.xlsx", sheet_name="Sheet1", header=None)
    df.columns = ["Ангилал", "Үзүүлэлт", "Он", "БУТ", "МКТ", "МСМТ", "НББТ",
                  "ОУАЖССИ", "ОУНББСМИ", "ОУС", "СДСТ", "СУТ", "СШУТ", "ЭкТ", "ЭнТИнс", "ЭЗТ", "Нийт"]
    df = df[df["Он"].notna()]
    df = df[df["Он"] != "Он"]
    df["Он"] = pd.to_numeric(df["Он"], errors="coerce").astype("Int64")
    df = df[df["Он"].notna()]
    
    DEPTS = ["БУТ", "МКТ", "МСМТ", "НББТ", "ОУАЖССИ", "ОУНББСМИ", "ОУС", "СДСТ", "СУТ", "СШУТ", "ЭкТ", "ЭнТИнс", "ЭЗТ"]
    for c in DEPTS + ["Нийт"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df, DEPTS

df, DEPTS = load_data()
CURRENT_YEAR = 2026
FUTURE_YEARS = [y for y in sorted(df["Он"].unique()) if y > CURRENT_YEAR]
HIST_YEARS = [y for y in sorted(df["Он"].unique()) if y <= CURRENT_YEAR]
ALL_YEARS = sorted(df["Он"].unique())

# Chart colors
COLORS = {
    "main": "#00d4ff",
    "accent": "#3a8aff",
    "target": "#ff4da6",
    "green": "#00e676",
    "orange": "#ff9800",
    "purple": "#b388ff",
    "bg": "#0a1830",
    "grid": "#1a2d4a",
    "text": "#a0b8e8",
}

DEPT_COLORS = [
    "#00d4ff","#3a8aff","#00e676","#ff9800",
    "#b388ff","#ff4da6","#ffeb3b","#4fc3f7",
    "#81c784","#ffb74d","#ce93d8","#4dd0e1","#aed581"
]

def plotly_theme():
    return dict(
        plot_bgcolor=COLORS["bg"],
        paper_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"], size=12),
        xaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"]),
        yaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"]),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=COLORS["text"])),
        margin=dict(l=40, r=20, t=40, b=40),
    )

def get_val(category, metric, year, dept):
    row = df[(df["Ангилал"] == category) & (df["Үзүүлэлт"] == metric) & (df["Он"] == year)]
    if row.empty: return None
    return row.iloc[0][dept]

def get_series(category, metric, dept):
    sub = df[(df["Ангилал"] == category) & (df["Үзүүлэлт"] == metric)].sort_values("Он")
    return sub["Он"].tolist(), sub[dept].tolist()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### 🏛️ СЭЗИС")
    st.markdown("---")
    st.markdown("**Тэнхим сонгох**")
    
    dept_choice = st.selectbox(
        "Тэнхим",
        ["Нийт (бүх тэнхим)"] + DEPTS,
        label_visibility="collapsed"
    )
    selected_dept = "Нийт" if dept_choice == "Нийт (бүх тэнхим)" else dept_choice
    
    st.markdown("---")
    st.markdown("**Он харах**")
    show_year = st.selectbox("Харах он", ALL_YEARS, index=list(ALL_YEARS).index(CURRENT_YEAR))
    
    st.markdown("---")
    st.markdown(f"""
    <div style='color:#4a9eff;font-size:12px;'>
    📌 <b>2026</b> = Одоогийн жил<br>
    <span style='color:#ff4da6;'>●</span> Ягаан = Ирээдүйн зорилт<br>
    <span style='color:#00d4ff;'>●</span> Цэнхэр = Тоон утга
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
st.markdown(f"""
<div class='main-header'>
    <div>
        <div class='header-title'>🎓 СЭЗИС — Багшийн хөгжлийн KPI Хяналтын Самбар</div>
        <div class='header-subtitle'>Тэнхим: <b style='color:#00d4ff'>{dept_choice}</b> &nbsp;|&nbsp; Харах он: <b style='color:#00d4ff'>{show_year}</b></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# TAB NAVIGATION
# ============================================================
tabs = ["📊 Багшийн тоо", "🎓 Боловсролын түвшин", "⭐ Зэрэглэл", "📈 Хувийн үзүүлэлт", "👥 Насны бүлэг", "🕒 Ажилласан жил", "🔧 Мэргэжил дээшлүүлэлт"]

if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

cols_tab = st.columns(len(tabs))
for i, (col, tab) in enumerate(zip(cols_tab, tabs)):
    with col:
        if st.button(tab, key=f"tab_{i}"):
            st.session_state.active_tab = i

active = st.session_state.active_tab
st.markdown(f"<div style='color:#4a9eff;font-size:13px;font-weight:600;border-bottom:2px solid #3a6adc;padding-bottom:6px;margin-bottom:16px;'>▶ {tabs[active]}</div>", unsafe_allow_html=True)

# ============================================================
# HELPER: Line chart with future targets
# ============================================================
def line_chart_with_target(title, years, values, is_pct=False, height=300):
    fig = go.Figure()
    hist_x = [y for y, v in zip(years, values) if y <= CURRENT_YEAR and v is not None]
    hist_y = [v for y, v in zip(years, values) if y <= CURRENT_YEAR and v is not None]
    fut_x = [y for y, v in zip(years, values) if y > CURRENT_YEAR and v is not None]
    fut_y = [v for y, v in zip(years, values) if y > CURRENT_YEAR and v is not None]
    
    fig.add_trace(go.Scatter(
        x=hist_x, y=hist_y, mode="lines+markers",
        name="Бодит утга", line=dict(color=COLORS["main"], width=2.5),
        marker=dict(size=7, color=COLORS["main"]),
    ))
    if fut_x:
        # Connect last hist to first future
        if hist_x:
            fig.add_trace(go.Scatter(
                x=[hist_x[-1]] + fut_x, y=[hist_y[-1]] + fut_y,
                mode="lines+markers", name="Зорилт",
                line=dict(color=COLORS["target"], width=2, dash="dot"),
                marker=dict(size=7, color=COLORS["target"], symbol="diamond"),
            ))
    
    suffix = "%" if is_pct else ""
    fig.update_layout(
        **plotly_theme(), height=height, title=dict(text=title, font=dict(color="#ffffff", size=13)),
        yaxis=dict(tickformat=".0%" if is_pct else None, gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"]),
        xaxis=dict(tickvals=years, gridcolor=COLORS["grid"]),
        showlegend=True,
        legend=dict(orientation="h", y=-0.15),
    )
    # Mark current year
    if CURRENT_YEAR in years:
        fig.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="#ffffff", opacity=0.3,
                      annotation_text="2026", annotation_font_color="#ffffff", annotation_font_size=10)
    return fig

def bar_chart_by_dept(title, category, metric, year, height=300):
    row = df[(df["Ангилал"] == category) & (df["Үзүүлэлт"] == metric) & (df["Он"] == year)]
    if row.empty:
        return None
    vals = [row.iloc[0][d] for d in DEPTS]
    fig = go.Figure(go.Bar(
        x=DEPTS, y=vals,
        marker=dict(color=DEPT_COLORS, line=dict(color="#000", width=0.5)),
        text=vals, textposition="outside", textfont=dict(color=COLORS["text"], size=11),
    ))
    fig.update_layout(**plotly_theme(), height=height, title=dict(text=title, font=dict(color="#ffffff", size=13)),
                      xaxis=dict(tickfont=dict(size=11)), yaxis=dict(gridcolor=COLORS["grid"]))
    return fig

def donut_chart(labels, values, title, height=280):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=DEPT_COLORS[:len(labels)], line=dict(color="#0a1830", width=2)),
        textinfo="label+percent", textfont=dict(color=COLORS["text"], size=11),
    ))
    fig.update_layout(**plotly_theme(), height=height,
                      title=dict(text=title, font=dict(color="#ffffff", size=13)),
                      showlegend=False)
    return fig

# ============================================================
# TAB 0: БАГШИЙН ТОО
# ============================================================
if active == 0:
    # Key metrics row
    metrics = [
        ("Үндсэн багш /Дотоод/", "Нийт үндсэн багшийн тоо", "👤"),
        ("Нийт үндсэн багшийн тоо", "Нийт үндсэн багшийн тоо", "🧑‍🏫"),  
        ("Нийт гэрээт багшийн тоо", "Нийт гэрээт багшийн тоо", "📋"),
        ("Нийт багшийн тоо", "Нийт багшийн тоо", "👥"),
        ("Үндсэн эмэгтэй багшийн тоо", "Үндсэн эмэгтэй багшийн тоо", "👩‍🏫"),
    ]
    
    # Use Багшийн тоо category
    cat = "Багшийн тоо"
    metric_rows = [
        ("Нийт үндсэн багшийн тоо", "👤", "Үндсэн багш"),
        ("Нийт гэрээт багшийн тоо", "📋", "Гэрээт багш"),
        ("Нийт багшийн тоо", "👥", "Нийт багш"),
        ("Үндсэн эмэгтэй багшийн тоо", "👩", "Эмэгтэй багш"),
        ("Нийт багш, ажилтаны тоо", "🏢", "Нийт ажилтан"),
        ("Зохицуулагчийн тоо", "🔧", "Зохицуулагч"),
    ]
    
    cols = st.columns(6)
    for i, (metric, icon, label) in enumerate(metric_rows):
        val = get_val(cat, metric, show_year, selected_dept)
        cols[i].markdown(f"""
        <div class='metric-card'>
            <div class='metric-icon'>{icon}</div>
            <div class='metric-value'>{int(val) if val is not None else '-'}</div>
            <div class='metric-label'>{label}</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("")
    col1, col2 = st.columns(2)
    
    with col1:
        years, vals = get_series(cat, "Нийт үндсэн багшийн тоо", selected_dept)
        fig = line_chart_with_target("Үндсэн багшийн тооны өөрчлөлт", years, vals)
        st.plotly_chart(fig, use_container_width=True)
        
        years2, vals2 = get_series(cat, "Нийт гэрээт багшийн тоо", selected_dept)
        fig2 = line_chart_with_target("Гэрээт багшийн тооны өөрчлөлт", years2, vals2)
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        # Доктор зэрэгтэй болон Эмэгтэй bagsh
        years3, vals3 = get_series(cat, "Үндсэн эмэгтэй багшийн тоо", selected_dept)
        fig3 = line_chart_with_target("Эмэгтэй багшийн тооны өөрчлөлт", years3, vals3)
        st.plotly_chart(fig3, use_container_width=True)
        
        # Bar by dept for current year
        fig4 = bar_chart_by_dept(f"Тэнхим тус бүрийн нийт багшийн тоо ({show_year})", cat, "Нийт багшийн тоо", show_year)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True)

# ============================================================
# TAB 1: БОЛОВСРОЛЫН ТҮВШИН
# ============================================================
elif active == 1:
    cat = "Боловсролын түвшин"
    levels = ["Бакалавр", "Магистр", "Доктор"]
    
    vals_2026 = [get_val(cat, lv, show_year, selected_dept) for lv in levels]
    vals_2026 = [v if v is not None else 0 for v in vals_2026]
    
    col1, col2, col3 = st.columns(3)
    icons = ["🎓", "📚", "🔬"]
    for col, lv, v, ic in zip([col1, col2, col3], levels, vals_2026, icons):
        col.markdown(f"""
        <div class='metric-card'>
            <div class='metric-icon'>{ic}</div>
            <div class='metric-value'>{int(v)}</div>
            <div class='metric-label'>{lv}</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("")
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Donut
        fig_d = donut_chart(levels, vals_2026, f"Боловсролын түвшингийн харьцаа ({show_year})")
        st.plotly_chart(fig_d, use_container_width=True)
    
    with col_b:
        # Stacked bar over years
        fig = go.Figure()
        for lv, clr in zip(levels, [COLORS["accent"], COLORS["main"], COLORS["green"]]):
            yrs, vs = get_series(cat, lv, selected_dept)
            is_fut = [y > CURRENT_YEAR for y in yrs]
            fig.add_trace(go.Bar(
                x=yrs, y=vs, name=lv, marker_color=clr,
                opacity=1,
            ))
        fig.update_layout(**plotly_theme(), barmode="stack", height=320,
                          title=dict(text="Боловсролын түвшингийн динамик", font=dict(color="#fff", size=13)))
        fig.add_vline(x=CURRENT_YEAR+0.5, line_dash="dash", line_color=COLORS["target"], opacity=0.5,
                      annotation_text="Зорилт →", annotation_font_color=COLORS["target"])
        st.plotly_chart(fig, use_container_width=True)
    
    # Line per level
    cols = st.columns(3)
    for col, lv in zip(cols, levels):
        yrs, vs = get_series(cat, lv, selected_dept)
        fig = line_chart_with_target(lv, yrs, vs, height=250)
        col.plotly_chart(fig, use_container_width=True)
    
    # By dept bar
    st.markdown("<div class='section-header'>Тэнхим тус бүрийн боловсролын түвшин</div>", unsafe_allow_html=True)
    fig_dept = go.Figure()
    for lv, clr in zip(levels, [COLORS["accent"], COLORS["main"], COLORS["green"]]):
        row = df[(df["Ангилал"] == cat) & (df["Үзүүлэлт"] == lv) & (df["Он"] == show_year)]
        if not row.empty:
            vals = [row.iloc[0][d] for d in DEPTS]
            fig_dept.add_trace(go.Bar(x=DEPTS, y=vals, name=lv, marker_color=clr))
    fig_dept.update_layout(**plotly_theme(), barmode="stack", height=300,
                           title=dict(text=f"Тэнхим тус бүрийн боловсролын түвшин ({show_year})", font=dict(color="#fff", size=13)))
    st.plotly_chart(fig_dept, use_container_width=True)

# ============================================================
# TAB 2: ЗЭРЭГЛЭЛ
# ============================================================
elif active == 2:
    cat = "Зэрэглэл"
    ranks = ["Дадлагажигч багш", "Багш", "Ахлах багш", "Дэд профессор", "Профессор"]
    rank_colors = [COLORS["text"], COLORS["accent"], COLORS["main"], COLORS["orange"], COLORS["green"]]
    
    cols = st.columns(5)
    icons = ["🌱", "📖", "⭐", "🏆", "👑"]
    for col, rk, ic, clr in zip(cols, ranks, icons, rank_colors):
        v = get_val(cat, rk, show_year, selected_dept)
        col.markdown(f"""
        <div class='metric-card'>
            <div class='metric-icon'>{ic}</div>
            <div class='metric-value' style='color:{clr}'>{int(v) if v is not None else '-'}</div>
            <div class='metric-label'>{rk}</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("")
    col1, col2 = st.columns(2)
    
    with col1:
        vals_cur = [get_val(cat, rk, show_year, selected_dept) or 0 for rk in ranks]
        fig_d = donut_chart(ranks, vals_cur, f"Зэрэглэлийн харьцаа ({show_year})", height=320)
        st.plotly_chart(fig_d, use_container_width=True)
    
    with col2:
        fig = go.Figure()
        for rk, clr in zip(ranks, rank_colors):
            yrs, vs = get_series(cat, rk, selected_dept)
            hist_x = [y for y, v in zip(yrs, vs) if y <= CURRENT_YEAR]
            hist_y = [v for y, v in zip(yrs, vs) if y <= CURRENT_YEAR]
            fut_x = [y for y, v in zip(yrs, vs) if y > CURRENT_YEAR]
            fut_y = [v for y, v in zip(yrs, vs) if y > CURRENT_YEAR]
            fig.add_trace(go.Scatter(x=hist_x, y=hist_y, name=rk, mode="lines+markers",
                                     line=dict(color=clr, width=2), marker=dict(size=6)))
            if fut_x and hist_x:
                fig.add_trace(go.Scatter(x=[hist_x[-1]]+fut_x, y=[hist_y[-1]]+fut_y, name=f"{rk} зорилт",
                                         mode="lines", line=dict(color=clr, dash="dot", width=1.5),
                                         showlegend=False))
        fig.update_layout(**plotly_theme(), height=320,
                          title=dict(text="Зэрэглэлийн динамик", font=dict(color="#fff", size=13)))
        fig.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="#ffffff", opacity=0.3)
        st.plotly_chart(fig, use_container_width=True)
    
    # By dept
    fig_dept = go.Figure()
    for rk, clr in zip(ranks, rank_colors):
        row = df[(df["Ангилал"] == cat) & (df["Үзүүлэлт"] == rk) & (df["Он"] == show_year)]
        if not row.empty:
            vals = [row.iloc[0][d] for d in DEPTS]
            fig_dept.add_trace(go.Bar(x=DEPTS, y=vals, name=rk, marker_color=clr))
    fig_dept.update_layout(**plotly_theme(), barmode="stack", height=300,
                           title=dict(text=f"Тэнхим тус бүрийн зэрэглэл ({show_year})", font=dict(color="#fff", size=13)))
    st.plotly_chart(fig_dept, use_container_width=True)

# ============================================================
# TAB 3: ХУВИЙН ҮЗҮҮЛЭЛТ
# ============================================================
elif active == 3:
    cat = "Хувь"
    pct_metrics = [
        ("Доктор зэрэгтэй багшийн эзлэх хувь", "🔬 Доктор", COLORS["green"]),
        ("Гадаад багшийн эзлэх хувь", "🌍 Гадаад", COLORS["accent"]),
        ("Оюутны сэтгэл ханамжийн үнэлгээний дундаж хувь", "😊 Оюутны сэтгэл ханамж", COLORS["orange"]),
        ("Багшийн сэтгэл ханамжийн үнэлгээний дундаж хувь", "👩‍🏫 Багшийн сэтгэл ханамж", COLORS["main"]),
        ("Гадаад хэлээр заах чадвартай багшийн эзлэх хувь", "🗣️ Гадаад хэлээр заах", COLORS["purple"]),
        ("Солилцооны хөтөлбөрт хамрагдсан багшийн эзлэх хувь", "🔄 Солилцоо", "#ff9800"),
        ("Төсөл удирдсан багшийн эзлэх хувь", "📁 Төсөл", "#f06292"),
        ("Хамтарсан судалгаа, төсөлд оролцсон багшийн эзлэх хувь", "🤝 Хамтарсан судалгаа", "#4fc3f7"),
        ("h-индекстэй багшийн эзлэх хувь", "📊 h-индекс", "#aed581"),
        ("WOS, Scopus-д өгүүлэл хэвлүүлсэн багшийн эзлэх хувь", "📰 WOS/Scopus", "#ffb74d"),
        ("ОУ мэргэжлийн зэрэгтэй багшийн эзлэх хувь", "🏅 ОУ мэргэжлийн зэрэг", "#ce93d8"),
        ("Дотоодын мэргэжлийн зэрэгтэй багшийн эзлэх хувь", "🎖️ Дотоодын зэрэг", "#80cbc4"),
    ]
    
    # 2026 values as gauge cards
    cols = st.columns(4)
    for i, (metric, label, clr) in enumerate(pct_metrics[:8]):
        v = get_val(cat, metric, CURRENT_YEAR, selected_dept)
        pct = f"{v*100:.1f}%" if v is not None else "-"
        col = cols[i % 4]
        col.markdown(f"""
        <div class='metric-card' style='margin-bottom:8px;'>
            <div class='metric-value' style='font-size:24px;color:{clr}'>{pct}</div>
            <div class='metric-label' style='font-size:11px;'>{label}</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("")
    # Line charts for key % metrics
    key_pcts = [
        ("Доктор зэрэгтэй багшийн эзлэх хувь", "Доктор зэрэгтэй багшийн хувь"),
        ("Гадаад хэлээр заах чадвартай багшийн эзлэх хувь", "Гадаад хэлээр заах чадвартай"),
        ("Оюутны сэтгэл ханамжийн үнэлгээний дундаж хувь", "Оюутны сэтгэл ханамж"),
        ("Багшийн сэтгэл ханамжийн үнэлгээний дундаж хувь", "Багшийн сэтгэл ханамж"),
    ]
    cols2 = st.columns(2)
    for i, (metric, label) in enumerate(key_pcts):
        yrs, vs = get_series(cat, metric, selected_dept)
        fig = line_chart_with_target(label, yrs, vs, is_pct=True, height=280)
        cols2[i % 2].plotly_chart(fig, use_container_width=True)
    
    # All % metrics bar for current year
    st.markdown("<div class='section-header'>2026 оны бүх хувийн үзүүлэлт</div>", unsafe_allow_html=True)
    labels_bar = [label for _, label, _ in pct_metrics]
    values_bar = [get_val(cat, m, CURRENT_YEAR, selected_dept) or 0 for m, _, _ in pct_metrics]
    clrs_bar = [c for _, _, c in pct_metrics]
    fig_bar = go.Figure(go.Bar(
        x=[v*100 for v in values_bar], y=labels_bar,
        orientation="h",
        marker=dict(color=clrs_bar),
        text=[f"{v*100:.1f}%" for v in values_bar],
        textposition="outside", textfont=dict(color=COLORS["text"]),
    ))
    fig_bar.update_layout(**plotly_theme(), height=400,
                          title=dict(text=f"Хувийн үзүүлэлтүүд ({CURRENT_YEAR}, {dept_choice})", font=dict(color="#fff", size=13)),
                          xaxis=dict(title="%", ticksuffix="%"),
                          margin=dict(l=250))
    st.plotly_chart(fig_bar, use_container_width=True)

# ============================================================
# TAB 4: НАСНЫ БҮЛЭГ
# ============================================================
elif active == 4:
    cat = "Насны бүлэг "
    age_groups = ["25 хүртэл", "26-35", "36-45", "46-55", "56 ба түүнээс дээш"]
    age_colors = [COLORS["accent"], COLORS["main"], COLORS["green"], COLORS["orange"], COLORS["purple"]]
    
    vals_cur = [get_val(cat, ag, show_year, selected_dept) or 0 for ag in age_groups]
    
    col1, col2 = st.columns(2)
    with col1:
        fig_d = donut_chart(age_groups, vals_cur, f"Насны бүлгийн харьцаа ({show_year})", height=320)
        st.plotly_chart(fig_d, use_container_width=True)
    
    with col2:
        # Horizontal bar
        fig_h = go.Figure(go.Bar(
            x=vals_cur, y=age_groups, orientation="h",
            marker=dict(color=age_colors),
            text=vals_cur, textposition="outside",
            textfont=dict(color=COLORS["text"]),
        ))
        fig_h.update_layout(**plotly_theme(), height=320,
                            title=dict(text=f"Насны бүлэг ({show_year})", font=dict(color="#fff", size=13)),
                            xaxis=dict(title="Багшийн тоо"))
        st.plotly_chart(fig_h, use_container_width=True)
    
    # Trend lines
    st.markdown("<div class='section-header'>Насны бүлгийн өөрчлөлт</div>", unsafe_allow_html=True)
    fig_t = go.Figure()
    for ag, clr in zip(age_groups, age_colors):
        yrs, vs = get_series(cat, ag, selected_dept)
        hist_x = [y for y, v in zip(yrs, vs) if y <= CURRENT_YEAR]
        hist_y = [v for y, v in zip(yrs, vs) if y <= CURRENT_YEAR]
        fut_x = [y for y, v in zip(yrs, vs) if y > CURRENT_YEAR]
        fut_y = [v for y, v in zip(yrs, vs) if y > CURRENT_YEAR]
        fig_t.add_trace(go.Scatter(x=hist_x, y=hist_y, name=ag, mode="lines+markers",
                                   line=dict(color=clr, width=2), marker=dict(size=6)))
        if fut_x and hist_x:
            fig_t.add_trace(go.Scatter(x=[hist_x[-1]]+fut_x, y=[hist_y[-1]]+fut_y,
                                       mode="lines", line=dict(color=clr, dash="dot", width=1.5), showlegend=False))
    fig_t.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="#ffffff", opacity=0.3,
                    annotation_text="2026", annotation_font_color="#ffffff")
    fig_t.update_layout(**plotly_theme(), height=320,
                        title=dict(text="Насны бүлгийн динамик", font=dict(color="#fff", size=13)))
    st.plotly_chart(fig_t, use_container_width=True)
    
    # By dept
    fig_dept = go.Figure()
    for ag, clr in zip(age_groups, age_colors):
        row = df[(df["Ангилал"] == cat) & (df["Үзүүлэлт"] == ag) & (df["Он"] == show_year)]
        if not row.empty:
            vals = [row.iloc[0][d] for d in DEPTS]
            fig_dept.add_trace(go.Bar(x=DEPTS, y=vals, name=ag, marker_color=clr))
    fig_dept.update_layout(**plotly_theme(), barmode="stack", height=300,
                           title=dict(text=f"Тэнхим тус бүрийн насны бүлэг ({show_year})", font=dict(color="#fff", size=13)))
    st.plotly_chart(fig_dept, use_container_width=True)

# ============================================================
# TAB 5: АЖИЛЛАСАН ЖИЛ
# ============================================================
elif active == 5:
    cat = "Ажилласан жил"
    exp_groups = ["3 жил хүртэл", "4-6 жил", "Ажилласан жил - 7-9 жил", "10-15 жил", "16-20 жил", "21 ба түүнээс дээш"]
    exp_labels = ["≤3 жил", "4-6 жил", "7-9 жил", "10-15 жил", "16-20 жил", "21+ жил"]
    exp_colors = [COLORS["accent"], COLORS["main"], COLORS["green"], COLORS["orange"], COLORS["purple"], "#f06292"]
    
    vals_cur = [get_val(cat, eg, show_year, selected_dept) or 0 for eg in exp_groups]
    
    col1, col2 = st.columns(2)
    with col1:
        fig_d = donut_chart(exp_labels, vals_cur, f"Ажилласан жилийн харьцаа ({show_year})", height=320)
        st.plotly_chart(fig_d, use_container_width=True)
    
    with col2:
        fig_h = go.Figure(go.Bar(
            x=vals_cur, y=exp_labels, orientation="h",
            marker=dict(color=exp_colors),
            text=vals_cur, textposition="outside",
            textfont=dict(color=COLORS["text"]),
        ))
        fig_h.update_layout(**plotly_theme(), height=320,
                            title=dict(text=f"Ажилласан жил ({show_year})", font=dict(color="#fff", size=13)))
        st.plotly_chart(fig_h, use_container_width=True)
    
    # Trends
    fig_t = go.Figure()
    for eg, el, clr in zip(exp_groups, exp_labels, exp_colors):
        yrs, vs = get_series(cat, eg, selected_dept)
        hist_x = [y for y, v in zip(yrs, vs) if y <= CURRENT_YEAR]
        hist_y = [v for y, v in zip(yrs, vs) if y <= CURRENT_YEAR]
        fut_x = [y for y, v in zip(yrs, vs) if y > CURRENT_YEAR]
        fut_y = [v for y, v in zip(yrs, vs) if y > CURRENT_YEAR]
        fig_t.add_trace(go.Scatter(x=hist_x, y=hist_y, name=el, mode="lines+markers",
                                   line=dict(color=clr, width=2), marker=dict(size=6)))
        if fut_x and hist_x:
            fig_t.add_trace(go.Scatter(x=[hist_x[-1]]+fut_x, y=[hist_y[-1]]+fut_y,
                                       mode="lines", line=dict(color=clr, dash="dot", width=1.5), showlegend=False))
    fig_t.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="#ffffff", opacity=0.3)
    fig_t.update_layout(**plotly_theme(), height=320,
                        title=dict(text="Ажилласан жилийн динамик", font=dict(color="#fff", size=13)))
    st.plotly_chart(fig_t, use_container_width=True)

# ============================================================
# TAB 6: МЭРГЭЖИЛ ДЭЭШЛҮҮЛЭЛТ
# ============================================================
elif active == 6:
    cat = "Мэргэжил дээшлүүлэлт"
    
    location_metrics = ["Гадаадад", "Дотоодод"]
    duration_metrics = ["1-3 хоног", "4-10 хоног", "11-29 хоног", "1 сараас дээш"]
    
    # Metrics row
    all_prof = location_metrics + duration_metrics
    cols = st.columns(6)
    icons2 = ["✈️", "🏠", "📅", "📆", "🗓️", "📊"]
    for i, (m, ic) in enumerate(zip(all_prof, icons2)):
        v = get_val(cat, m, show_year, selected_dept)
        cols[i].markdown(f"""
        <div class='metric-card'>
            <div class='metric-icon'>{ic}</div>
            <div class='metric-value'>{int(v) if v is not None else '-'}</div>
            <div class='metric-label'>{m}</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("")
    col1, col2 = st.columns(2)
    
    with col1:
        # Location donut
        vals_loc = [get_val(cat, m, show_year, selected_dept) or 0 for m in location_metrics]
        fig_d = donut_chart(location_metrics, vals_loc, f"Сургалтын байршил ({show_year})", height=300)
        st.plotly_chart(fig_d, use_container_width=True)
    
    with col2:
        # Duration donut
        vals_dur = [get_val(cat, m, show_year, selected_dept) or 0 for m in duration_metrics]
        fig_d2 = donut_chart(duration_metrics, vals_dur, f"Сургалтын үргэлжлэх хугацаа ({show_year})", height=300)
        st.plotly_chart(fig_d2, use_container_width=True)
    
    # Trend lines
    st.markdown("<div class='section-header'>Мэргэжил дээшлүүлэлтийн динамик</div>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    
    with col3:
        fig_l = go.Figure()
        for m, clr in zip(location_metrics, [COLORS["main"], COLORS["accent"]]):
            yrs, vs = get_series(cat, m, selected_dept)
            hist_x = [y for y, v in zip(yrs, vs) if y <= CURRENT_YEAR]
            hist_y = [v for y, v in zip(yrs, vs) if y <= CURRENT_YEAR]
            fut_x = [y for y, v in zip(yrs, vs) if y > CURRENT_YEAR]
            fut_y = [v for y, v in zip(yrs, vs) if y > CURRENT_YEAR]
            fig_l.add_trace(go.Scatter(x=hist_x, y=hist_y, name=m, mode="lines+markers",
                                       line=dict(color=clr, width=2), marker=dict(size=6)))
            if fut_x and hist_x:
                fig_l.add_trace(go.Scatter(x=[hist_x[-1]]+fut_x, y=[hist_y[-1]]+fut_y,
                                           mode="lines", line=dict(color=clr, dash="dot"), showlegend=False))
        fig_l.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="#ffffff", opacity=0.3)
        fig_l.update_layout(**plotly_theme(), height=300,
                            title=dict(text="Гадаад/Дотоод сургалт", font=dict(color="#fff", size=13)))
        st.plotly_chart(fig_l, use_container_width=True)
    
    with col4:
        fig_dur = go.Figure()
        dur_colors = [COLORS["green"], COLORS["orange"], COLORS["purple"], "#f06292"]
        for m, clr in zip(duration_metrics, dur_colors):
            yrs, vs = get_series(cat, m, selected_dept)
            hist_x = [y for y, v in zip(yrs, vs) if y <= CURRENT_YEAR]
            hist_y = [v for y, v in zip(yrs, vs) if y <= CURRENT_YEAR]
            fut_x = [y for y, v in zip(yrs, vs) if y > CURRENT_YEAR]
            fut_y = [v for y, v in zip(yrs, vs) if y > CURRENT_YEAR]
            fig_dur.add_trace(go.Scatter(x=hist_x, y=hist_y, name=m, mode="lines+markers",
                                         line=dict(color=clr, width=2), marker=dict(size=6)))
            if fut_x and hist_x:
                fig_dur.add_trace(go.Scatter(x=[hist_x[-1]]+fut_x, y=[hist_y[-1]]+fut_y,
                                             mode="lines", line=dict(color=clr, dash="dot"), showlegend=False))
        fig_dur.add_vline(x=CURRENT_YEAR, line_dash="dash", line_color="#ffffff", opacity=0.3)
        fig_dur.update_layout(**plotly_theme(), height=300,
                              title=dict(text="Сургалтын хугацааны динамик", font=dict(color="#fff", size=13)))
        st.plotly_chart(fig_dur, use_container_width=True)
    
    # By dept stacked
    fig_dept = go.Figure()
    for m, clr in zip(location_metrics + duration_metrics, [COLORS["main"], COLORS["accent"], COLORS["green"], COLORS["orange"], COLORS["purple"], "#f06292"]):
        row = df[(df["Ангилал"] == cat) & (df["Үзүүлэлт"] == m) & (df["Он"] == show_year)]
        if not row.empty:
            vals = [row.iloc[0][d] for d in DEPTS]
            fig_dept.add_trace(go.Bar(x=DEPTS, y=vals, name=m, marker_color=clr))
    fig_dept.update_layout(**plotly_theme(), barmode="group", height=320,
                           title=dict(text=f"Тэнхим тус бүрийн мэргэжил дээшлүүлэлт ({show_year})", font=dict(color="#fff", size=13)))
    st.plotly_chart(fig_dept, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(f"<div style='color:#1e3a6e;font-size:11px;text-align:center;'>СЭЗИС — Стратегийн KPI Хяналтын Систем | Багшийн хөгжил | {CURRENT_YEAR}</div>", unsafe_allow_html=True)
