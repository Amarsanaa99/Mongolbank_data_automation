"""
СУТ — Стратегийн KPI Хяналтын Самбар
Streamlit Dashboard | dashboards/SUT.py
GitHub: Amarsanaa99/Mongolbank_data_automation
"""

import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="СУТ · KPI Dashboard",
    page_icon="🏛",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── PALETTE ──────────────────────────────────────────────────────────────────
P = {
    "navy":   "#0B2447",
    "blue":   "#1A4F8A",
    "mid":    "#2271B3",
    "teal":   "#0A7B8C",
    "amber":  "#E8960F",
    "green":  "#17855A",
    "red":    "#C0392B",
    "purple": "#7B3FA0",
    "slate":  "#64748B",
    "bg":     "#EEF3FA",
    "white":  "#FFFFFF",
}

CAT_META = {
    "Rank":                   {"icon": "🏆", "color": "#7B3FA0", "short": "Rank"},
    "БАГШИЙН ХӨГЖИЛ":        {"icon": "👨‍🏫", "color": "#1A4F8A", "short": "Багш"},
    "ХӨТӨЛБӨР ХӨГЖИЛ":       {"icon": "📚", "color": "#0A7B8C", "short": "Хөтөлбөр"},
    "СУРАЛЦАГЧ ХӨГЖИЛ":      {"icon": "🎓", "color": "#17855A", "short": "Суралцагч"},
    "СУРГАЛТ":                {"icon": "📖", "color": "#E8960F", "short": "Сургалт"},
    "СУДАЛГАА":               {"icon": "🔬", "color": "#C0392B", "short": "Судалгаа"},
    "ТӨСӨЛ ХӨТӨЛБӨР":        {"icon": "🚀", "color": "#16A085", "short": "Төсөл"},
    "САНХҮҮГИЙН ХУВЬ НЭМЭР": {"icon": "💰", "color": "#8E44AD", "short": "Санхүү"},
}

YEARS = [2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stApp { background: #ECF1F9; }
#MainMenu, footer, header, .stDeployButton { display:none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── HEADER ── */
.dash-header {
    background: linear-gradient(120deg, #0B2447 0%, #1A4F8A 55%, #2271B3 100%);
    padding: 18px 32px 15px;
    border-bottom: 3px solid #E8960F;
    position: relative; overflow: hidden;
}
.dash-header::after {
    content:'';
    position:absolute; top:0; right:0; bottom:0;
    width:340px;
    background: radial-gradient(ellipse at right center, rgba(255,255,255,0.06) 0%, transparent 70%);
}
.h-title { color:#fff; font-size:20px; font-weight:800; letter-spacing:-0.3px; }
.h-sub   { color:rgba(255,255,255,0.55); font-size:11.5px; margin-top:2px; }
.h-pill  {
    display:inline-flex; align-items:center; gap:5px;
    background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.18);
    color:rgba(255,255,255,0.85); font-size:10.5px; font-weight:600;
    padding:3px 11px; border-radius:20px; margin-right:6px; margin-top:8px;
}
.live-dot {
    width:7px; height:7px; border-radius:50%; background:#4ADE80;
    display:inline-block; animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.25} }

/* ── NAV BAR ── */
.nav-bar {
    background:#fff;
    padding: 10px 32px;
    display:flex; gap:8px; flex-wrap:nowrap; align-items:center;
    border-bottom: 1px solid #E2E8F0;
    overflow-x: auto;
    position: sticky; top:0; z-index:100;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.nav-bar::-webkit-scrollbar { height:3px; }
.nav-bar::-webkit-scrollbar-thumb { background:#CBD5E1; border-radius:2px; }

/* ── METRIC CARD ── */
.mcard {
    background:#fff; border-radius:10px; padding:15px 17px;
    box-shadow:0 1px 5px rgba(0,0,0,0.06);
    border-top: 3px solid;
    transition: transform 0.15s, box-shadow 0.15s;
}
.mcard:hover { transform:translateY(-2px); box-shadow:0 5px 16px rgba(0,0,0,0.1); }
.mc-lbl  { font-size:9.5px; color:#94A3B8; font-weight:700; letter-spacing:.9px; text-transform:uppercase; }
.mc-val  { font-family:'JetBrains Mono',monospace; font-size:26px; font-weight:700; line-height:1.1; margin:3px 0; }
.mc-sub  { font-size:10px; color:#64748B; }
.mc-tag  { font-size:10px; font-weight:600; margin-top:5px; display:inline-block; padding:2px 8px; border-radius:10px; }

/* ── STATUS BADGE ── */
.badge { font-size:9px; font-weight:700; padding:2px 7px; border-radius:9px; white-space:nowrap; }
.b-g { background:#DCFCE7; color:#166534; }
.b-a { background:#FEF9C3; color:#854D0E; }
.b-r { background:#FEE2E2; color:#991B1B; }
.b-n { background:#F1F5F9; color:#64748B; }

/* ── KPI ROW ── */
.kpi-row {
    background:#fff; border-radius:8px; padding:10px 14px;
    margin-bottom:7px; border-left:3px solid;
    box-shadow:0 1px 4px rgba(0,0,0,0.05);
    transition: transform 0.1s;
}
.kpi-row:hover { transform:translateX(2px); }
.kpi-name { font-size:10.5px; color:#334155; line-height:1.4; }
.kpi-nums { font-family:'JetBrains Mono',monospace; font-size:10px; }

/* ── SECTION PANEL ── */
.spanel {
    background:#fff; border-radius:10px;
    box-shadow:0 1px 5px rgba(0,0,0,0.06);
    overflow:hidden; margin-bottom:14px;
}
.spanel-head {
    padding:11px 16px; border-bottom:1px solid #F1F5F9;
    display:flex; align-items:center; justify-content:space-between;
}
.spanel-title { font-size:12px; font-weight:700; color:#0B2447; }
.spanel-sub   { font-size:10px; color:#94A3B8; }
.spanel-body  { padding:14px 16px; }

/* ── TABS (override Streamlit) ── */
.stTabs [data-baseweb="tab-list"] {
    gap:4px; background:#F8FAFC; border-radius:8px;
    padding:4px; border:none;
}
.stTabs [data-baseweb="tab"] {
    border-radius:6px !important; font-size:11.5px !important;
    font-weight:600 !important; padding:6px 14px !important;
    color:#64748B !important;
}
.stTabs [aria-selected="true"] {
    background:#0B2447 !important; color:#fff !important;
}
.stTabs [data-baseweb="tab-border"] { display:none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top:12px !important; }

/* ── FOOTER ── */
.dash-footer {
    background:#0B2447; color:rgba(255,255,255,0.45);
    font-size:10px; padding:10px 32px;
    display:flex; justify-content:space-between; align-items:center;
    margin-top:20px;
}

/* ── SCROLLABLE ── */
.scroll-box { max-height:440px; overflow-y:auto; padding-right:2px; }
.scroll-box::-webkit-scrollbar { width:3px; }
.scroll-box::-webkit-scrollbar-thumb { background:#CBD5E1; border-radius:2px; }

/* ── DIVIDER ── */
.div-line { height:1px; background:linear-gradient(90deg,#E2E8F0,transparent); margin:10px 0; }

/* Radio & select polish */
div[data-testid="stRadio"] label { font-size:12px !important; font-weight:600 !important; }
div[data-testid="stSelectbox"] label { font-size:10px !important; color:#94A3B8 !important; }
</style>
""", unsafe_allow_html=True)


# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    search = [
        "sut.xlsx",
        "dashboards/sut.xlsx",
        os.path.join(os.path.dirname(__file__), "sut.xlsx"),
        os.path.join(os.path.dirname(__file__), "../sut.xlsx"),
        "/mnt/user-data/uploads/sut.xlsx",
    ]
    raw = None
    for p in search:
        if os.path.exists(p):
            raw = pd.read_excel(p, sheet_name="Sheet1", header=None)
            break
    if raw is None:
        st.error("❌ sut.xlsx файл олдсонгүй.")
        st.stop()

    records = []
    for ri in range(3, len(raw)):
        row = raw.iloc[ri]
        chiglel = str(row[0]).strip().rstrip()
        kpi     = str(row[1]).strip()
        if not kpi or kpi == "nan":
            continue
        # Normalize chiglel
        if chiglel.startswith("СУДАЛГАА"):
            chiglel = "СУДАЛГАА"

        suuri_s = row[2]  if pd.notna(row[2])  else None
        suuri_t = row[18] if pd.notna(row[18]) else None

        for i, yr in enumerate(YEARS):
            zs = row[3  + i*2] if pd.notna(row[3  + i*2]) else None
            bs = row[4  + i*2] if pd.notna(row[4  + i*2]) else None
            zt = row[19 + i*2] if pd.notna(row[19 + i*2]) else None
            bt = row[20 + i*2] if pd.notna(row[20 + i*2]) else None
            records.append(dict(
                chiglel=chiglel, kpi=kpi, year=yr,
                zs=zs, bs=bs, zt=zt, bt=bt,
                suuri_s=suuri_s, suuri_t=suuri_t,
            ))

    return pd.DataFrame(records)


df = load_data()
CATEGORIES = [c for c in CAT_META.keys() if c in df["chiglel"].unique()]


# ── HELPERS ───────────────────────────────────────────────────────────────────
def fmt(v, kpi=""):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    v = float(v)
    if abs(v) >= 1e9:  return f"{v/1e9:.2f}Т₮"
    if abs(v) >= 1e6:  return f"{v/1e6:.1f}М"
    kl = kpi.lower()
    is_pct = any(w in kl for w in ["хувь","харьцаа"])
    if is_pct and abs(v) <= 1.5:  return f"{v*100:.1f}%"
    if v == int(v):               return f"{int(v):,}"
    return f"{v:.2f}"


def achv(z, b, kpi=""):
    """% achievement; rank KPI = lower is better."""
    if z is None or b is None: return None
    try:
        z, b = float(z), float(b)
        if z == 0: return None
        p = (b / z) * 100
        if "эрэмбэ" in kpi.lower() or "the" in kpi.lower():
            p = (z / b) * 100
        return round(p, 1)
    except:
        return None


def pcolor(p):
    if p is None:     return P["slate"]
    if p >= 90:       return P["green"]
    if p >= 70:       return P["amber"]
    return P["red"]


def badge(p):
    if p is None: return '<span class="badge b-n">—</span>'
    if p >= 90:   return f'<span class="badge b-g">✓ {p:.0f}%</span>'
    if p >= 70:   return f'<span class="badge b-a">≈ {p:.0f}%</span>'
    return f'<span class="badge b-r">✗ {p:.0f}%</span>'


def cols_for(school):
    return ("zs","bs","suuri_s") if school == "СЭЗИС" else ("zt","bt","suuri_t")


def plotly_cfg():
    return {"displayModeBar": False, "responsive": True}


# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "cat" not in st.session_state:  st.session_state.cat = "БАГШИЙН ХӨГЖИЛ"
if "sch" not in st.session_state:  st.session_state.sch = "СУТ"
if "yr"  not in st.session_state:  st.session_state.yr  = 2025


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HEADER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<div class="dash-header">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <div style="display:flex;align-items:center;gap:14px;">
      <div style="width:46px;height:46px;background:rgba(255,255,255,0.12);border-radius:10px;
                  display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;">🏛</div>
      <div>
        <div class="h-title">САНХҮҮ-УДИРДЛАГЫН ТЭНХИМ</div>
        <div class="h-sub">СЭЗИС · СУТ — Стратегийн KPI Хяналтын Самбар · 2021–2031</div>
        <div style="margin-top:6px;">
          <span class="h-pill">📊 Зорилт vs Биелэлт</span>
          <span class="h-pill">🏫 СЭЗИС · СУТ</span>
          <span class="h-pill">📅 2024–2031</span>
        </div>
      </div>
    </div>
    <div style="text-align:right;flex-shrink:0;">
      <div style="color:rgba(255,255,255,0.45);font-size:10px;margin-bottom:6px;">sut.xlsx · Streamlit</div>
      <div style="display:flex;align-items:center;gap:6px;justify-content:flex-end;
                  background:rgba(74,222,128,0.12);border:1px solid rgba(74,222,128,0.3);
                  padding:4px 12px;border-radius:20px;">
        <span class="live-dot"></span>
        <span style="color:#4ADE80;font-size:10.5px;font-weight:600;">Шинэчлэгдсэн</span>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NAV BAR  – category buttons (horizontal)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cols_nav = st.columns([1] * len(CATEGORIES) + [0.6, 0.6])
for i, cat in enumerate(CATEGORIES):
    meta = CAT_META[cat]
    active = st.session_state.cat == cat
    with cols_nav[i]:
        btn_style = (
            f"background-color:{meta['color']};color:white;"
            "border:none;box-shadow:0 3px 8px rgba(0,0,0,0.18);"
        ) if active else (
            "background-color:#F1F5F9;color:#475569;"
            "border:1px solid #E2E8F0;"
        )
        label = f"{meta['icon']} {meta['short']}"
        if st.button(label, key=f"nav_{cat}", use_container_width=True, help=cat):
            st.session_state.cat = cat
            st.rerun()

with cols_nav[-2]:
    sch = st.radio("Сургууль", ["СУТ", "СЭЗИС"], horizontal=True,
                   label_visibility="collapsed",
                   index=0 if st.session_state.sch == "СУТ" else 1,
                   key="sch_r")
    st.session_state.sch = sch

with cols_nav[-1]:
    yr = st.selectbox("Жил", YEARS,
                      index=YEARS.index(st.session_state.yr),
                      label_visibility="collapsed", key="yr_sel")
    st.session_state.yr = yr

# ── Active state shortcuts ────────────────────────────────────────────────────
cat    = st.session_state.cat
sch    = st.session_state.sch
yr     = st.session_state.yr
zcol, bcol, scol = cols_for(sch)
meta   = CAT_META.get(cat, {"icon":"●","color":P["blue"],"short":cat})
cc     = meta["color"]                        # category colour

df_cat  = df[df["chiglel"] == cat].copy()
df_yr   = df_cat[df_cat["year"] == yr].copy()
kpi_all = df_yr["kpi"].tolist()

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION HEADER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.container():
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;padding:0 32px 8px;">
      <div style="width:38px;height:38px;background:{cc}20;border-radius:9px;
                  display:flex;align-items:center;justify-content:center;font-size:22px;">{meta['icon']}</div>
      <div>
        <div style="font-size:17px;font-weight:800;color:#0B2447;">{cat}</div>
        <div style="font-size:11px;color:#94A3B8;">{sch} · {yr} оны биелэлт</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SUMMARY METRIC CARDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
achvs = [achv(r[zcol], r[bcol], r["kpi"]) for _, r in df_yr.iterrows()]
n_g   = sum(1 for p in achvs if p and p >= 90)
n_a   = sum(1 for p in achvs if p and 70 <= p < 90)
n_r   = sum(1 for p in achvs if p and p < 70)
avg_p = np.nanmean([p for p in achvs if p]) if any(p for p in achvs if p) else None

mc_data = [
    ("Нийт KPI",        str(len(kpi_all)), "Үзүүлэлтийн тоо",   cc,         "#EEF2FF"),
    ("Биелэгдсэн",      str(n_g),          "≥90% биелэлт",       P["green"], "#F0FDF4"),
    ("Ойртож байна",    str(n_a),          "70–89% биелэлт",     P["amber"], "#FFFBEB"),
    ("Хоцорсон",        str(n_r),          "<70% биелэлт",       P["red"],   "#FEF2F2"),
    ("Дундаж биелэлт",  f"{avg_p:.0f}%" if avg_p else "—", f"{yr} он", cc, "#F8FAFC"),
]

pad = st.container()
with pad:
    m_cols = st.columns(5)
    for col_w, (lbl, val, sub, clr, bg) in zip(m_cols, mc_data):
        with col_w:
            st.markdown(f"""
            <div class="mcard" style="border-top-color:{clr};background:{bg};">
              <div class="mc-lbl">{lbl}</div>
              <div class="mc-val" style="color:{clr};">{val}</div>
              <div class="mc-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN LAYOUT: left list  |  right charts
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
left, right = st.columns([1.05, 2.05], gap="medium")

# ── LEFT: KPI progress list ───────────────────────────────────────────────────
with left:
    st.markdown(f"""
    <div class="spanel-head" style="background:{cc}08;border-radius:10px 10px 0 0;
         border-bottom:2px solid {cc}30;">
      <div>
        <div class="spanel-title">{meta['icon']} KPI Биелэлт</div>
        <div class="spanel-sub">{sch} · {yr} · Зорилт vs Биелэлт</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="scroll-box">', unsafe_allow_html=True)
    for idx, (_, row) in enumerate(df_yr.iterrows()):
        z = row[zcol]; b = row[bcol]
        p = achv(z, b, row["kpi"])
        bw = min(int(p), 100) if p else 0
        bc = pcolor(p)
        kn = row["kpi"]
        kn_d = kn[:55] + "…" if len(kn) > 55 else kn
        b_fmt = fmt(b, kn);  z_fmt = fmt(z, kn)

        st.markdown(f"""
        <div class="kpi-row" style="border-left-color:{bc};">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:6px;margin-bottom:6px;">
            <div class="kpi-name">{kn_d}</div>
            {badge(p)}
          </div>
          <div style="display:flex;align-items:center;gap:8px;">
            <div style="flex:1;background:#F1F5F9;border-radius:4px;height:6px;overflow:hidden;">
              <div style="width:{bw}%;background:{bc};height:100%;border-radius:4px;
                          transition:width .4s ease;"></div>
            </div>
            <div class="kpi-nums" style="color:{bc};font-weight:700;min-width:42px;text-align:right;">{b_fmt}</div>
            <div class="kpi-nums" style="color:#94A3B8;min-width:44px;">/ {z_fmt}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── RIGHT: Tabs with charts ───────────────────────────────────────────────────
with right:
    t1, t2, t3, t4 = st.tabs([
        "📈 Чиг хандлага",
        "📊 Зорилт/Биелэлт",
        "🔥 Хяналтын матриц",
        "🌐 СЭЗИС vs СУТ",
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 1 ── Trend line
    # ─────────────────────────────────────────────────────────────────────────
    with t1:
        sel_kpi = st.selectbox("KPI сонгох", kpi_all, key="t1_kpi",
                               label_visibility="visible")
        dk = df_cat[df_cat["kpi"] == sel_kpi].sort_values("year")

        z_vals  = dk[zcol].tolist()
        b_vals  = dk[bcol].tolist()
        yrs     = dk["year"].tolist()
        suuri   = dk[scol].iloc[0] if len(dk) > 0 else None

        # detect percentage KPI for axis format
        is_pct_kpi = any(w in sel_kpi.lower() for w in ["хувь","харьцаа"])

        fig = go.Figure()

        # fill band between zorilt and bielelt
        rgb = tuple(int(cc.lstrip("#")[i:i+2], 16) for i in (0,2,4))
        fig.add_trace(go.Scatter(
            x=yrs+yrs[::-1], y=z_vals+b_vals[::-1],
            fill="toself", fillcolor=f"rgba({rgb[0]},{rgb[1]},{rgb[2]},0.07)",
            line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip",
        ))

        # baseline
        if suuri is not None:
            fig.add_shape(type="line", x0=min(yrs)-.4, x1=max(yrs)+.4,
                          y0=suuri, y1=suuri,
                          line=dict(color="#94A3B8", dash="dot", width=1.4))
            fig.add_annotation(x=min(yrs), y=suuri, text=f"  Суурь {fmt(suuri,sel_kpi)}",
                               showarrow=False, font=dict(size=9, color="#94A3B8"),
                               xanchor="left", yanchor="bottom")

        # zorilt
        fig.add_trace(go.Scatter(
            x=yrs, y=z_vals, mode="lines+markers", name="Зорилт",
            line=dict(color=cc, dash="dash", width=2.2),
            marker=dict(size=7, symbol="circle-open", color=cc, line=dict(width=2)),
            hovertemplate="<b>%{x}</b>  Зорилт: %{y:.3f}<extra></extra>",
        ))

        # bielelt
        vy = [y for y,b in zip(yrs,b_vals) if b is not None]
        vb = [b for b in b_vals if b is not None]
        fig.add_trace(go.Scatter(
            x=vy, y=vb, mode="lines+markers", name="Биелэлт",
            line=dict(color="#E8960F", width=3),
            marker=dict(size=9, color="#E8960F", line=dict(width=2,color="white")),
            hovertemplate="<b>%{x}</b>  Биелэлт: %{y:.3f}<extra></extra>",
        ))

        # selected year marker
        if yr in yrs:
            fig.add_vline(x=yr, line=dict(color="#C0392B", dash="dot", width=1.5))

        fig.update_layout(
            height=290, margin=dict(l=4,r=4,t=20,b=4),
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="Plus Jakarta Sans", size=11),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        font=dict(size=10)),
            xaxis=dict(tickmode="linear", dtick=1, gridcolor="#F1F5F9",
                       linecolor="#E2E8F0", tickfont=dict(size=10)),
            yaxis=dict(gridcolor="#F1F5F9", linecolor="#E2E8F0", tickfont=dict(size=10),
                       tickformat=".0%" if is_pct_kpi else None),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True, config=plotly_cfg())

        # mini metrics below chart
        cur = df_yr[df_yr["kpi"] == sel_kpi]
        cb = cur[bcol].values[0] if len(cur) > 0 else None
        cz = cur[zcol].values[0] if len(cur) > 0 else None
        cp = achv(cz, cb, sel_kpi)
        mcc = st.columns(4)
        mcc[0].metric("Биелэлт",        fmt(cb, sel_kpi))
        mcc[1].metric("Зорилт",         fmt(cz, sel_kpi))
        mcc[2].metric("Биелэлтийн %",   f"{cp:.0f}%" if cp else "—")
        mcc[3].metric("Суурь (2021)",   fmt(suuri, sel_kpi))

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 2 ── Bar comparison (all KPIs of category for selected year)
    # ─────────────────────────────────────────────────────────────────────────
    with t2:
        st.markdown(f'<div style="font-size:10.5px;color:#94A3B8;margin-bottom:8px;">'
                    f'Бүх KPI-ийн {yr} оны биелэлтийн хувь · {sch}</div>',
                    unsafe_allow_html=True)

        shorts  = [k[:32]+"…" if len(k)>32 else k for k in kpi_all]
        a_vals  = [
            achv(
                df_yr[df_yr["kpi"]==k][zcol].values[0] if len(df_yr[df_yr["kpi"]==k])>0 else None,
                df_yr[df_yr["kpi"]==k][bcol].values[0] if len(df_yr[df_yr["kpi"]==k])>0 else None,
                k
            ) for k in kpi_all
        ]
        bar_v  = [p if p else 0 for p in a_vals]
        bar_c  = [pcolor(p) for p in a_vals]
        bar_tx = [f"{v:.0f}%" if v else "—" for v in bar_v]

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=shorts, y=bar_v, marker_color=bar_c, marker_line_width=0,
            text=bar_tx, textposition="outside",
            textfont=dict(size=9, family="JetBrains Mono"),
            hovertemplate="<b>%{x}</b><br>Биелэлт: %{y:.1f}%<extra></extra>",
        ))
        for lvl, lbl, clr in [(100,"Зорилт 100%","#334155"),(90,"Сайн","#17855A"),(70,"Хангалттай","#E8960F")]:
            fig2.add_hline(y=lvl, line=dict(color=clr,dash="dash",width=1.3),
                           annotation_text=lbl, annotation_font=dict(size=8,color=clr),
                           annotation_position="right")
        fig2.update_layout(
            height=320, margin=dict(l=4,r=60,t=16,b=80),
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="Plus Jakarta Sans", size=10),
            xaxis=dict(tickangle=-38, tickfont=dict(size=8.5), gridcolor="#F8FAFC",
                       linecolor="#E2E8F0"),
            yaxis=dict(gridcolor="#F1F5F9", ticksuffix="%", tickfont=dict(size=9),
                       range=[0, max(bar_v+[115]) if bar_v else 120]),
            showlegend=False, bargap=0.38,
        )
        st.plotly_chart(fig2, use_container_width=True, config=plotly_cfg())

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 3 ── Heatmap (KPI × Year)
    # ─────────────────────────────────────────────────────────────────────────
    with t3:
        st.markdown(f'<div style="font-size:10.5px;color:#94A3B8;margin-bottom:8px;">'
                    f'KPI × Жил хяналтын матриц · {sch}</div>', unsafe_allow_html=True)

        mat, ylabels = [], []
        for kn in kpi_all:
            row_v = []
            dk = df_cat[df_cat["kpi"]==kn].sort_values("year")
            for y in YEARS:
                r = dk[dk["year"]==y]
                if len(r):
                    p = achv(r[zcol].values[0], r[bcol].values[0], kn)
                    row_v.append(p if p else np.nan)
                else:
                    row_v.append(np.nan)
            mat.append(row_v)
            ylabels.append(kn[:38]+"…" if len(kn)>38 else kn)

        mat_np = np.array(mat, dtype=float)
        txt    = [[f"{v:.0f}%" if not np.isnan(v) else "—" for v in rw] for rw in mat_np]

        fig3 = go.Figure(go.Heatmap(
            z=mat_np, x=[str(y) for y in YEARS], y=ylabels,
            colorscale=[[0,"#FEE2E2"],[.35,"#FEF3C7"],[.7,"#DCFCE7"],[1,"#14532D"]],
            zmin=0, zmax=130,
            text=txt, texttemplate="%{text}",
            textfont=dict(size=9, family="JetBrains Mono"),
            hoverongaps=False,
            hovertemplate="<b>%{y}</b><br>%{x}: %{text}<extra></extra>",
            showscale=True,
            colorbar=dict(
                title=dict(text="Биелэлт %", font=dict(size=9)),
                tickvals=[0,50,70,90,110,130],
                ticktext=["0%","50%","70%","90%","110%","130%+"],
                len=0.8, thickness=11, tickfont=dict(size=8),
            ),
        ))
        fig3.update_layout(
            height=max(240, len(kpi_all)*30+50),
            margin=dict(l=4,r=80,t=8,b=4),
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="Plus Jakarta Sans", size=9.5),
            xaxis=dict(side="top", tickfont=dict(size=10,family="JetBrains Mono")),
            yaxis=dict(tickfont=dict(size=9), autorange="reversed"),
        )
        st.plotly_chart(fig3, use_container_width=True, config=plotly_cfg())

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 4 ── СЭЗИС vs СУТ comparison
    # ─────────────────────────────────────────────────────────────────────────
    with t4:
        ct4l, ct4r = st.columns(2)

        # Grouped bar
        with ct4l:
            st.markdown(f'<div style="font-size:10.5px;color:#94A3B8;margin-bottom:8px;">'
                        f'{cat} · {yr} он харьцуулалт</div>', unsafe_allow_html=True)
            dc = df[(df["chiglel"]==cat)&(df["year"]==yr)]
            sh = [k[:26]+"…" if len(k)>26 else k for k in dc["kpi"].tolist()]
            as_ = [achv(r["zs"],r["bs"],r["kpi"]) or 0 for _,r in dc.iterrows()]
            at_ = [achv(r["zt"],r["bt"],r["kpi"]) or 0 for _,r in dc.iterrows()]

            fig4 = go.Figure()
            fig4.add_trace(go.Bar(name="СЭЗИС", x=sh, y=as_,
                marker_color="#1A4F8A", opacity=0.88,
                text=[f"{v:.0f}%" for v in as_],
                textposition="inside", textfont=dict(size=8,color="white"),
                hovertemplate="СЭЗИС · %{x}<br>%{y:.1f}%<extra></extra>"))
            fig4.add_trace(go.Bar(name="СУТ", x=sh, y=at_,
                marker_color="#0A7B8C", opacity=0.88,
                text=[f"{v:.0f}%" for v in at_],
                textposition="inside", textfont=dict(size=8,color="white"),
                hovertemplate="СУТ · %{x}<br>%{y:.1f}%<extra></extra>"))
            fig4.add_hline(y=100, line=dict(color="#334155",dash="dash",width=1.2))
            fig4.update_layout(
                barmode="group", height=310,
                margin=dict(l=4,r=4,t=8,b=80),
                paper_bgcolor="white", plot_bgcolor="white",
                font=dict(family="Plus Jakarta Sans", size=9.5),
                legend=dict(orientation="h",y=1.05,xanchor="right",x=1,font=dict(size=10)),
                xaxis=dict(tickangle=-38, tickfont=dict(size=8), gridcolor="#F8FAFC"),
                yaxis=dict(gridcolor="#F1F5F9", ticksuffix="%", tickfont=dict(size=9),
                           range=[0, max(as_+at_+[115])]),
                bargap=0.18, bargroupgap=0.04,
            )
            st.plotly_chart(fig4, use_container_width=True, config=plotly_cfg())

        # Radar — all categories
        with ct4r:
            st.markdown(f'<div style="font-size:10.5px;color:#94A3B8;margin-bottom:8px;">'
                        f'Бүх чиглэлийн дундаж биелэлт · {yr}</div>', unsafe_allow_html=True)
            r_lbl, r_s, r_t = [], [], []
            for c in CATEGORIES:
                tmp = df[(df["chiglel"]==c)&(df["year"]==yr)]
                ps = [achv(r["zs"],r["bs"],r["kpi"]) for _,r in tmp.iterrows()]
                pt = [achv(r["zt"],r["bt"],r["kpi"]) for _,r in tmp.iterrows()]
                ps = [p for p in ps if p]; pt = [p for p in pt if p]
                r_lbl.append(CAT_META[c]["icon"]+" "+CAT_META[c]["short"])
                r_s.append(np.mean(ps) if ps else 0)
                r_t.append(np.mean(pt) if pt else 0)

            fig5 = go.Figure()
            fig5.add_trace(go.Scatterpolar(
                r=r_s+[r_s[0]], theta=r_lbl+[r_lbl[0]], fill="toself", name="СЭЗИС",
                line=dict(color="#1A4F8A",width=2.2), fillcolor="rgba(26,79,138,0.14)",
                hovertemplate="%{theta}: %{r:.1f}%<extra>СЭЗИС</extra>",
            ))
            fig5.add_trace(go.Scatterpolar(
                r=r_t+[r_t[0]], theta=r_lbl+[r_lbl[0]], fill="toself", name="СУТ",
                line=dict(color="#0A7B8C",width=2.5), fillcolor="rgba(10,123,140,0.16)",
                hovertemplate="%{theta}: %{r:.1f}%<extra>СУТ</extra>",
            ))
            fig5.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True,range=[0,130],
                        tickvals=[0,50,100], ticktext=["0","50%","100%"],
                        tickfont=dict(size=8), gridcolor="#E2E8F0"),
                    angularaxis=dict(tickfont=dict(size=9.5)),
                    bgcolor="white",
                ),
                paper_bgcolor="white", height=310,
                margin=dict(l=20,r=20,t=16,b=20),
                legend=dict(orientation="h",y=-0.08,font=dict(size=10)),
                font=dict(family="Plus Jakarta Sans"),
            )
            st.plotly_chart(fig5, use_container_width=True, config=plotly_cfg())

        # Diff table
        st.markdown("**СЭЗИС vs СУТ — Зөрүүний хүснэгт**")
        diff_rows = []
        dc2 = df[(df["chiglel"]==cat)&(df["year"]==yr)]
        for _, row in dc2.iterrows():
            ps = achv(row["zs"], row["bs"], row["kpi"])
            pt = achv(row["zt"], row["bt"], row["kpi"])
            diff_rows.append({
                "KPI": row["kpi"],
                "СЭЗИС биелэлт": f"{ps:.0f}%" if ps else "—",
                "СУТ биелэлт":   f"{pt:.0f}%" if pt else "—",
                "Зөрүү": f"{(ps-pt):.0f}%" if (ps and pt) else "—",
            })
        ddf = pd.DataFrame(diff_rows)
        st.dataframe(ddf, use_container_width=True, height=220, hide_index=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FULL OVERVIEW SECTION  (all categories mini-cards)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("<div class='div-line'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div style="font-size:13px;font-weight:800;color:#0B2447;margin-bottom:10px;">
  📋 Нийт чиглэлийн дундаж биелэлт — {sch} · {yr}
</div>""", unsafe_allow_html=True)

ov_cols = st.columns(len(CATEGORIES))
for ci, c_name in enumerate(CATEGORIES):
    cm = CAT_META[c_name]
    tmp = df[(df["chiglel"]==c_name)&(df["year"]==yr)]
    pa_list = [achv(r[zcol], r[bcol], r["kpi"]) for _, r in tmp.iterrows()]
    pa_list = [p for p in pa_list if p]
    avg = np.mean(pa_list) if pa_list else None
    avg_str = f"{avg:.0f}%" if avg else "—"
    clr = pcolor(avg)
    bw  = min(int(avg), 100) if avg else 0

    with ov_cols[ci]:
        is_active = c_name == cat
        border = f"border:2px solid {cm['color']};" if is_active else "border:1px solid #E2E8F0;"
        st.markdown(f"""
        <div style="background:white;border-radius:9px;padding:12px 10px;
             {border}box-shadow:0 1px 4px rgba(0,0,0,0.05);text-align:center;cursor:pointer;">
          <div style="font-size:22px;margin-bottom:4px;">{cm['icon']}</div>
          <div style="font-size:9px;font-weight:700;color:{cm['color']};letter-spacing:.5px;
                      text-transform:uppercase;margin-bottom:6px;">{cm['short']}</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:700;
                      color:{clr};">{avg_str}</div>
          <div style="background:#F1F5F9;border-radius:3px;height:5px;margin-top:6px;overflow:hidden;">
            <div style="width:{bw}%;background:{clr};height:100%;border-radius:3px;"></div>
          </div>
          <div style="font-size:8.5px;color:#94A3B8;margin-top:4px;">{len(pa_list)} KPI</div>
        </div>""", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-footer">
  <span>🏛 СЭЗИС · Санхүү-Удирдлагын Тэнхим (СУТ) · Стратегийн хяналт</span>
  <span>🟢 ≥90% Биелэгдсэн · 🟡 70–89% Ойртож байна · 🔴 &lt;70% Хоцорсон</span>
  <span>© 2025 · sut.xlsx · Streamlit Cloud</span>
</div>
""", unsafe_allow_html=True)
