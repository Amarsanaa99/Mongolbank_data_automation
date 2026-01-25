import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from pathlib import Path

# ====================
# PAGE
# =====================
st.set_page_config("Dashboard", layout="wide")
st.title("🏦 Dashboard")
st.caption("Macro Indicators")

# ✅ GLOBAL STYLE (END USER QUALITY)
st.markdown("""
<style>
/* Page width control */
.block-container {
    padding-top: 3.2rem;
    padding-bottom: 2.2rem;
}
h1 {
    margin-top:0;
}
/* Sidebar-like left column feel */
div[data-testid="column"]:first-child {
    background: rgba(255,255,255,0.02);
    border-radius: 12px;
}

/* Section headers */
h2, h3 {
    letter-spacing: 0.3px;
}

/* Remove Altair gray background */
.vega-embed {
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)

BASE_DIR = Path(__file__).resolve().parents[1]
EXCEL_PATH = BASE_DIR / "Dashboard_cleaned_data.xlsx"

@st.cache_data(show_spinner=False)
def read_sheet(sheet):
    return pd.read_excel(EXCEL_PATH, sheet_name=sheet, header=[0, 1])

# =====================
# DATASET SELECT
# ======================
sheets = [s for s in pd.ExcelFile(EXCEL_PATH).sheet_names
          if s.lower() in ["month", "quarter"]]

left, right = st.columns([1.4, 4.6], gap="large")

with left:
    with st.container(border=True):
        st.subheader("📦 Dataset")

        dataset = st.radio(
            "Dataset",
            sheets,
            horizontal=True,
            label_visibility="collapsed"
        )
        
# ======================
# LOAD DATA
# ======================
df = read_sheet(dataset)

# ======================
# HEADER-ийг ШИНЭЧЛЭХ
# ======================
# Excel-ийн бүтцийг хадгална
if isinstance(df.columns, pd.MultiIndex):
    # Зөвхөн эхний түвшний header-ыг шалгана
    top_level = df.columns.get_level_values(0)
    
    # TIME багануудыг олох
    time_cols = []
    for col in df.columns:
        if col[0] in ["Year", "Month", "Quarter"]:
            time_cols.append(col)
    
    if not time_cols:
        st.error("❌ No time columns found")
        st.stop()
    
    # TIME ба DATA салгах
    df_time = df[time_cols].copy()
    df_data = df.drop(columns=time_cols)
    
    freq = "Monthly" if "Month" in df_time.columns else "Quarterly"
    
    with left:
        st.caption(f"Frequency: {freq}")
        
    # TIME багануудыг хялбарчилна
    for i, col in enumerate(df_time.columns):
        if isinstance(col, tuple):
            df_time.columns.values[i] = col[0]  # Зөвхөн эхний түвшний нэрийг ашиглана
    
    # DATA-ийн header-ыг цэвэрлэх
    # Level 0-ийг цэвэрлэх (Unnamed устгах)
    level0 = df_data.columns.get_level_values(0)
    level1 = df_data.columns.get_level_values(1)
    
    # Level 0-д байгаа "Unnamed" утгуудыг өмнөх утгаар дүүргэх
    new_level0 = []
    for val in level0:
        if pd.isna(val) or "Unnamed" in str(val):
            new_level0.append(new_level0[-1] if new_level0 else "Other")
        else:
            new_level0.append(val)
    
    df_data.columns = pd.MultiIndex.from_arrays([new_level0, level1])
    
else:
    # Хэрэв MultiIndex биш бол (баталгаажуулалт)
    st.error("❌ Unexpected data format - expected MultiIndex columns")
    st.stop()
    
with left:
    # ======================
    # 🧭 INDICATOR GROUP (ТУСДАА ХҮРЭЭ)
    # ======================
    with st.container(border=True):
        st.subheader("🧭 Indicator group")

        available_groups = sorted(df_data.columns.get_level_values(0).unique())
        group = st.radio(
            "Indicator group",
            available_groups,
            label_visibility="collapsed"
        )
    # ======================
    # 📌 INDICATORS (ТУСДАА ХҮРЭЭ)
    # ======================
    with st.container(border=True):
        st.subheader("📌 Indicators")

        indicators = sorted([
            col[1] for col in df_data.columns
            if col[0] == group and not pd.isna(col[1])
        ])

        selected = st.multiselect(
            "Indicators",
            indicators,
            default=[indicators[0]] if indicators else [],
            label_visibility="collapsed"
        )

# ======================
# DATA PREPARATION
# ======================
if not selected:
    st.info("ℹ️ No indicators selected — showing group-level summary only.")

# ======================
# 🔧 KPI & CHANGE HELPERS (GLOBAL)
# ======================
def compute_changes(df, indicator, freq):
    s = df[["x", indicator]].dropna().copy()

    # 🔒 X хамгаалалт (ЧИНИЙ ХҮССЭН ХЭСЭГ)
    s["x"] = s["x"].astype(str).str.strip()
    s = s[s["x"] != ""]

    if len(s) < 2:
        return None

    # 🔒 SORT
    s = s.sort_values("x").reset_index(drop=True)

    # 🔒 VALUE SCALAR
    latest_val = float(s.iloc[-1][indicator])
    prev_val   = float(s.iloc[-2][indicator])

    # ======================
    # 🔹 PREV (QoQ / MoM)
    # ======================
    prev = (latest_val / prev_val - 1) * 100 if prev_val != 0 else None

    # ======================
    # 🔹 YoY (INDEX-BASED)
    # ======================
    yoy = None
    if freq == "Quarterly" and len(s) >= 5:
        base_val = float(s.iloc[-5][indicator])
        if base_val != 0:
            yoy = (latest_val / base_val - 1) * 100

    elif freq == "Monthly" and len(s) >= 13:
        base_val = float(s.iloc[-13][indicator])
        if base_val != 0:
            yoy = (latest_val / base_val - 1) * 100

    # ======================
    # 🔹 YTD
    # ======================
    ytd = None
    try:
        current_year = s.iloc[-1]["x"][:4]
        year_data = s[s["x"].str.startswith(current_year)]
        if len(year_data) >= 1:
            year_start = float(year_data.iloc[0][indicator])
            if year_start != 0:
                ytd = (latest_val / year_start - 1) * 100
    except:
        ytd = None

    return {
        "latest": latest_val,
        "prev": prev,
        "yoy": yoy,
        "ytd": ytd
    }


def render_change(label, value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return f"<span class='change-item'>{label}: N/A</span>"

    arrow = "▲" if value > 0 else "▼"
    cls = "change-up" if value > 0 else "change-down"

    return (
        f"<span class='change-item {cls}'>"
        f"<span class='change-arrow'>{arrow}</span>"
        f"{label}: {value:.2f}%"
        f"</span>"
    )


# Өгөгдлийг цуваа болгон нэгтгэх
series = df_time.copy()
# ======================
# HELPER: DataFrame → Series болгох
# ======================
def as_series(col):
    if isinstance(col, pd.DataFrame):
        return col.iloc[:, 0]
    return col

# ======================
# FIX: Year / Month / Quarter block structure
# ======================
for col in ["Year", "Month", "Quarter"]:
    if col in series.columns:
        series[col] = series[col].ffill()

# Time багануудыг тоон утга болгох
for col in ["Year", "Month", "Quarter"]:
    if col in series.columns:
        # Баганын утгуудыг list болгон авах, дараа нь Series болгох
        values = series[col].values.tolist() if hasattr(series[col], 'values') else series[col]
        # Хэрэв nested list байвал задлах
        if isinstance(values, list) and values and isinstance(values[0], list):
            values = [v[0] if isinstance(v, list) else v for v in values]
        series[col] = pd.to_numeric(pd.Series(values), errors='coerce')
# ======================
# CREATE TIME INDEX (FINAL, SAFE)
# ======================
year = as_series(series["Year"]) if "Year" in series.columns else None
month = as_series(series["Month"]) if "Month" in series.columns else None
quarter = as_series(series["Quarter"]) if "Quarter" in series.columns else None

if year is not None and month is not None:
    series["time"] = (
        year.astype(int).astype(str) + "-" +
        month.astype(int).astype(str).str.zfill(2)
    )

elif year is not None and quarter is not None:
    series["time"] = (
        year.astype(int).astype(str) + "-Q" +
        quarter.astype(int).astype(str)
    )

elif year is not None:
    series["time"] = year.astype(int).astype(str)

else:
    st.error("❌ No valid time columns found")
    st.stop()
# ======================
# ✅ YEAR LABEL (GLOBAL X AXIS)
# ======================
series["year_label"] = series["Year"].astype(int).astype(str)

for col in ["Year", "Month", "Quarter"]:
    if col in series.columns:
        series[col] = as_series(series[col])

# ======================
# ⏳ TIME RANGE (MAIN CHART ONLY)
# ======================
with left:
    with st.container(border=True):
        st.subheader("⏳ Time range")
        
        # Жилийн сонголтыг хоёр баганад зэрэгцүүлэх
        year_col1, year_col2 = st.columns(2)
        
        year_s = series["Year"]
        if isinstance(year_s, pd.DataFrame):
            year_s = year_s.iloc[:, 0]
        
        years = sorted(
            year_s.dropna().astype(int).unique().tolist()
        )
        
        with year_col1:
            start_year = st.selectbox(
                "Start Year",
                years,
                index=0
            )
        
        with year_col2:
            end_year = st.selectbox(
                "End Year",
                years,
                index=len(years)-1
            )
        
        # Сар эсвэл улирлын сонголтыг хоёр баганад зэрэгцүүлэх
        if freq == "Monthly":
            months = list(range(1, 13))
            
            month_col1, month_col2 = st.columns(2)
            
            with month_col1:
                start_month = st.selectbox(
                    "Start Month",
                    months,
                    index=0,
                    format_func=lambda x: f"{x:02d}"
                )
            
            with month_col2:
                end_month = st.selectbox(
                    "End Month",
                    months,
                    index=len(months)-1,
                    format_func=lambda x: f"{x:02d}"
                )
            
            # time string үүсгэх
            start_time = f"{start_year}-{start_month:02d}"
            end_time = f"{end_year}-{end_month:02d}"
            
        elif freq == "Quarterly":
            quarters = [1, 2, 3, 4]
            
            quarter_col1, quarter_col2 = st.columns(2)
            
            with quarter_col1:
                start_quarter = st.selectbox(
                    "Start Quarter",
                    quarters,
                    index=0
                )
            
            with quarter_col2:
                end_quarter = st.selectbox(
                    "End Quarter",
                    quarters,
                    index=len(quarters)-1
                )
            
            # time string үүсгэх
            start_time = f"{start_year}-Q{start_quarter}"
            end_time = f"{end_year}-Q{end_quarter}"

# Сонгосон үзүүлэлтүүдийг нэмэх
for indicator in selected:
    if (group, indicator) in df_data.columns:
        series[indicator] = df_data[(group, indicator)].values
    else:
        st.warning(f"Indicator '{indicator}' not found in data")

# Графикийн өгөгдөл бэлтгэх
plot_data = (
    series
    .loc[:, ["time"] + selected]
    .copy()
    .set_index("time")
    .sort_index()
)
# ======================
# SPLIT: DATA vs NO DATA
# ======================

# өгөгдөлтэй баганууд
valid_cols = [
    col for col in plot_data.columns
    if not plot_data[col].isna().all()
]

# өгөгдөлгүй баганууд
nodata_cols = [
    col for col in plot_data.columns
    if plot_data[col].isna().all()
]

# зөвхөн өгөгдөлтэйг графикт ашиглана
plot_data_valid = plot_data[valid_cols]
# ======================
# 🔒 HARD CHECK: time column
# ======================
if "time" not in series.columns:
    st.error("❌ 'time' column was not created. Check Year / Month / Quarter logic.")
    st.stop()

# time хоосон эсэх
if series["time"].isna().all():
    st.error("❌ 'time' column exists but contains only NaN")
    st.stop()
        
# ======================
# MAIN CHART (PRO-LEVEL: ZOOM + PAN + SCROLL)
# ======================
with right:
    with st.container(border=True):
        
        st.subheader("📈 Main chart")
        
        # ===== 1️⃣ DATA (NO AGGREGATION)
        chart_df = series[["time"] + selected].copy()
        
        # ⏳ APPLY TIME RANGE (SAFE STRING FILTER)
        chart_df = chart_df[
            (chart_df["time"] >= start_time) &
            (chart_df["time"] <= end_time)
        ]
        
        # ===== 2️⃣ VALID INDICATORS ONLY
        valid_indicators = [
            c for c in selected
            if c in chart_df.columns and not chart_df[c].isna().all()
        ]
        
        if not valid_indicators:
            st.warning("⚠️ No data available for selected indicator(s)")
            st.stop()
        
        import plotly.graph_objects as go
        
        # ===== 3️⃣ TIME FORMATTING =====
        chart_df = chart_df.copy()
        
        if freq == "Monthly":
            chart_df["time_dt"] = pd.to_datetime(
                chart_df["time"],
                format="%Y-%m",
                errors="coerce"
            )
        elif freq == "Quarterly":
            chart_df["time_dt"] = (
                pd.PeriodIndex(chart_df["time"], freq="Q")
                .to_timestamp()
            )
        else:
            st.error("❌ Unknown frequency")
            st.stop()
        
        # 🔒 HARD CHECK
        if chart_df["time_dt"].isna().all():
            st.error("❌ Failed to convert time → datetime")
            st.stop()
        
        # ===== 4️⃣ X-AXIS CONFIGURATION
        start_year_int = int(start_year) if isinstance(start_year, str) else start_year
        end_year_int = int(end_year) if isinstance(end_year, str) else end_year
        year_count = end_year_int - start_year_int + 1
        
        # ===== 5️⃣ PLOTLY FIGURE (MAIN + RANGE SLIDER) =====
        fig = go.Figure()
        
        # Өнгөний палитр (professional colors)
        colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
        
        # ===== 5️⃣ PLOTLY FIGURE (MAIN + RANGE SLIDER) =====
        fig = go.Figure()
        
        # Өнгөний палитр (Mongolbank colors)
        colors = [
            '#3b82f6',  # Mongolbank primary blue
            '#D4AF37',  # Accent gold
            '#06B6D4',  # Cyan
            '#10B981',  # Green
            '#EF4444',  # Red
            '#8B5CF6'   # Purple
        ]
        
        # 🔥 LINE TRACES
        for i, col in enumerate(valid_indicators):
            color = colors[i % len(colors)]
            
            fig.add_trace(
                go.Scatter(
                    x=chart_df["time_dt"],
                    y=chart_df[col],
                    mode="lines",
                    name=col,
                    line=dict(width=2.4, color=color),
                    hovertemplate=(
                        "<b>%{fullData.name}</b><br>" +
                        "Time: %{x|" + ("%Y-%m" if freq == "Monthly" else "%Y-Q%q") + "}<br>" +
                        "Value: %{y:.2f}<extra></extra>"
                    )
                )
            )
        
        # 🔥 MARKERS (HOVER-only)
        for i, col in enumerate(valid_indicators):
            color = colors[i % len(colors)]
            
            fig.add_trace(
                go.Scatter(
                    x=chart_df["time_dt"],
                    y=chart_df[col],
                    mode="markers",
                    name=col,
                    marker=dict(
                        size=8,
                        color=color,
                        line=dict(width=2, color='white')
                    ),
                    showlegend=False,
                    hoverinfo='skip',
                    visible='legendonly'
                )
            )
        
        # === Layout: FRED-style interaction ===
        fig.update_layout(
            height=460,
            margin=dict(l=40, r=140, t=40, b=60),
            template="plotly_dark",
            
            # ✅ DRAG MODE (BOX ZOOM)
            dragmode='pan',
            
            # 🔥 CROSSHAIR HOVER
            hovermode='x unified',
            
            # 🎨 BACKGROUNDS
            paper_bgcolor="rgba(15, 41, 83, 0.3)",
            plot_bgcolor="rgba(11, 37, 84, 0.5)",
            
            xaxis=dict(
                title=None,
                type="date",
                rangeslider=dict(
                    visible=True,
                    thickness=0.05
                ),
                showgrid=False,
                
                # 🔥 SPIKE LINES
                showspikes=True,
                spikemode='across',
                spikesnap='cursor',
                spikecolor='rgba(170, 170, 170, 0.6)',
                spikethickness=1.5,
                spikedash='solid',
            ),
            yaxis=dict(
                title=None,
                zeroline=False,
                showgrid=True,
                gridcolor="rgba(224,224,224,0.3)",
                
                # 🔥 Y-AXIS SPIKE LINES
                showspikes=True,
                spikemode='across',
                spikesnap='cursor',
                spikecolor='rgba(170, 170, 170, 0.6)',
                spikethickness=1.5,
                spikedash='solid'
            ),
            
            legend=dict(
                title=None,
                x=1.02,
                y=1,
                xanchor="left",
                yanchor="top",
                bgcolor="rgba(0,0,0,0)",
                orientation="v",
                font=dict(size=11)
            )
        )
        
        # 🔥 MODEBAR CONFIGURATION
        config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
            'modeBarButtonsToAdd': ['downloadData'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'mongolbank_macro_chart',
                'height': 800,
                'width': 1400,
                'scale': 2
            },
            'doubleClick': 'reset',
            'scrollZoom': True
        }
        
        st.plotly_chart(fig, use_container_width=True, config=config)
        # 🔹 Chart-ийн өгөгдлийг CSV болгон татах
        csv = chart_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download chart data (CSV)",
            data=csv,
            file_name='main_chart_data.csv',
            mime='text/csv'
        )



    
    def compute_group_kpis(df, indicators):
        stats = []
    
        for ind in indicators:
            if ind not in df.columns:
                continue
    
            series = df[["time", ind]].copy()
            series[ind] = pd.to_numeric(series[ind], errors="coerce")
    
            last_valid_idx = series[ind].last_valid_index()
            if last_valid_idx is None:
                continue
    
            raw_val = series.loc[last_valid_idx, ind]
    
            try:
                last_value = float(raw_val)
            except:
                continue
    
            last_date = str(series.loc[last_valid_idx, "time"])
    
            stats.append({
                "Indicator": ind,
                "Min": series[ind].min(),
                "Max": series[ind].max(),
                "Mean": series[ind].mean(),
                "Median": series[ind].median(),
                "Std": series[ind].std(),
                "Last": last_value,
                "Last date": last_date
            })
    
        return pd.DataFrame(stats)


    
    # ======================
    # 📊 KPI CALCULATION (INDICATOR LEVEL)
    # ======================
    
    group_indicators = [
        col[1] for col in df_data.columns
        if col[0] == group
    ]
    
    # 🔹 БҮХ indicator-уудын KPI-г НЭГ УДАА бодно
    kpi_df = compute_group_kpis(chart_df, group_indicators)
    
    # 🔹 KPI-д харуулах PRIMARY indicator
    primary_indicator = selected[0]
    
    # 🔹 KPI-г салгах
    kpi_main = kpi_df[kpi_df["Indicator"] == primary_indicator]
    kpi_rest = kpi_df[kpi_df["Indicator"] != primary_indicator]
    
    # 🔥 FIXED STYLING (no purple gradient, compact)
    st.markdown("""
    <style>
    /* ===== KPI CARDS ===== */
    .kpi-card {
        background: linear-gradient(
            135deg,
            rgba(15, 23, 42, 0.95),
            rgba(30, 41, 59, 0.85)
        );
        border: 1px solid rgba(59,130,246,0.3);
        border-radius: 12px;
        padding: 16px 18px;
        margin: 8px 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 28px rgba(59,130,246,0.25);
        border-color: rgba(59,130,246,0.6);
    }
    
    .kpi-label {
        font-size: 10px;
        font-weight: 700;
        color: #94a3b8;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 8px;
        font-family: 'Monaco', 'Courier New', monospace;
    }
    
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #60a5fa;
        font-family: 'Monaco', 'Courier New', monospace;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 8px rgba(96,165,250,0.3);
        line-height: 1.2;
    }
    
    .kpi-sub {
        font-size: 11px;
        color: #cbd5e1;
        opacity: 0.7;
        margin-top: 6px;
        font-weight: 500;
    }
    
    /* ===== HEADER STYLING ===== */
    .kpi-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 20px 0 16px 0;
        padding: 12px 16px;
        background: linear-gradient(
            90deg,
            rgba(59,130,246,0.1),
            rgba(139,92,246,0.05)
        );
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
    }
    
    .kpi-header-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e2e8f0;
    }
    
    .kpi-header-indicator {
        font-size: 1.1rem;
        font-weight: 700;
        color: #60a5fa;
        font-family: 'Monaco', 'Courier New', monospace;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ===== KPI CARD HELPER
    def kpi_card(label, value, sublabel=None):
        sub = ""
        if sublabel is not None:
            sub = f"<div class='kpi-sub'>{str(sublabel)}</div>"
        
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                {sub}
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # 🔥 HEADER
    st.markdown(
        f"""
        <div class="kpi-header">
            <span class="kpi-header-title">📌 Indicator-level KPIs</span>
            <span style="opacity: 0.4;">→</span>
            <span class="kpi-header-indicator">{primary_indicator}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if kpi_main.empty:
        st.info("No KPI data available.")
        st.stop()
    
    row = kpi_main.iloc[0]
    
    # 🔽 KPI CARDS
    cols = st.columns(6)
    
    with cols[0]:
        last_date = str(row["Last date"]).split('\n')[0].split('Name:')[0].strip()
        kpi_card(
            "LAST VALUE",
            f"{float(row['Last']):.2f}",
            last_date
        )
    
    with cols[1]:
        kpi_card("MEAN", f"{row['Mean']:.2f}")
    with cols[2]:
        kpi_card("MEDIAN", f"{row['Median']:.2f}")
    with cols[3]:
        kpi_card("MINIMUM VALUE", f"{row['Min']:.2f}")
    with cols[4]:
        kpi_card("MAXIMUM VALUE", f"{row['Max']:.2f}")
    with cols[5]:
        kpi_card("STD (VOLATILITY)", f"{row['Std']:.2f}")
    
    # ======================
    # 📋 OPTIONAL — Indicator-level KPI TABLE
    # ======================
    if not kpi_rest.empty:
        with st.expander("📋 Indicator-level statistics"):
            st.dataframe(
                kpi_rest
                .set_index("Indicator")
                .round(2),
                use_container_width=True
            )
    
    # ======================
    # 📉 CHANGE SUMMARY — ENHANCED PRO STYLE
    # ======================
    st.markdown("### 📉 Change summary")
    
    # 🔥 Change summary-д ашиглах indicator-ууд
    if selected:
        change_indicators = selected
    else:
        change_indicators = [
            col[1] for col in df_data.columns
            if col[0] == group and not pd.isna(col[1])
        ]
    
    if not group_indicators:
        st.caption("No indicators in this group.")
    else:
        cards_html = ""
        
        for ind in change_indicators:
            tmp = pd.DataFrame({
                "x": series["time"],
                ind: df_data[(group, ind)].values
            })
            
            if not tmp[ind].isna().all():
                changes = compute_changes(tmp, ind, freq)
            else:
                changes = None
            
            if changes:
                # 🔹 Өнгөний логик (up=green, down=red)
                def render_metric(label, value):
                    if value is None or (isinstance(value, float) and pd.isna(value)):
                        return f"<span class='metric-item metric-neutral'><span class='metric-label'>{label}</span><span class='metric-value'>N/A</span></span>"
                    
                    cls = "metric-up" if value > 0 else "metric-down" if value < 0 else "metric-neutral"
                    arrow = "▲" if value > 0 else "▼" if value < 0 else "─"
                    
                    return (
                        f"<span class='metric-item {cls}'>"
                        f"<span class='metric-label'>{label}</span>"
                        f"<span class='metric-value'>{arrow} {value:.1f}%</span>"
                        f"</span>"
                    )
                
                cards_html += f"""
                <div class="change-card-pro">
                    <div class="change-title-pro">{ind}</div>
                    <div class="change-metrics-pro">
                        {render_metric("YoY", changes.get("yoy"))}
                        {render_metric("YTD", changes.get("ytd"))}
                        {render_metric("Prev", changes.get("prev"))}
                    </div>
                </div>
                """
        
        # ✅ ENHANCED STYLING
        if cards_html:
            components.html(
                """
                <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                .change-container-pro {
                    display: inline-flex;
                    flex-wrap: wrap;  /* Олон мөр болгох */
                    gap: 6px;
                    padding: 8px 0;
                    max-height: none;
                    overflow: visible;
                }
                .change-grid-pro {
                    display: inline-flex;
                    flex-wrap: wrap;
                    gap: 6px;
                    padding: 8px 4px;
                    overflow: visible;
                }
                .change-card-pro {
                    width: fit-content;          
                    min-width: unset;          
                    max-width: unset;            
                    flex: 0 0 auto;             
                    padding: 16px 18px;
                    background: linear-gradient(
                        135deg,
                        rgba(19, 47, 94, 0.85),
                        rgba(15, 41, 83, 0.75)
                    );
                    border: 1px solid rgba(20, 52, 124, 0.35);
                    border-radius: 10px;
                    transition: all 0.25s ease;
                }
                
                .change-card-pro:hover {
                    transform: translateY(-3px);
                    border-color: rgba(20, 52, 124, 0.6);
                    box-shadow: 0 6px 20px rgba(20, 52, 124, 0.25);
                }
                
                .change-title-pro {
                    font-size: 14px;
                    font-weight: 700;
                    color: #e2e8f0;
                    margin-bottom: 14px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid rgba(148,163,184,0.2);
                }
                
                .change-metrics-pro {
                    display: inline-flex;
                    flex-direction: column;
                    gap: 4px;
                }
                
                .metric-item {
                    width: fit-content;
                    max-width: 100%;
                    display: inline-flex;
                    justify-content: flex-start;
                    align-items: center;
                    gap: 6px;
                    padding: 4px 8px;
                    background: rgba(30,41,59,0.6);
                    border-radius: 8px;
                    border-left: 3px solid transparent;
                    transition: all 0.2s ease;
                }
                
                .metric-item:hover {
                    background: rgba(30,41,59,0.9);
                }
                
                .metric-label {
                    font-size: 11px;
                    font-weight: 600;
                    color: #94a3b8;
                    text-transform: uppercase;
                    letter-spacing: 0.01em;
                }
                
                .metric-value {
                    font-size: 15px;
                    font-weight: 700;
                    font-family: 'Monaco', 'Courier New', sans-serif;
                }
                
                .metric-up {
                    border-left-color: #22c55e;
                }
                
                .metric-up .metric-value {
                    color: #22c55e;
                    text-shadow: 0 0 8px rgba(34,197,94,0.4);
                }
                
                .metric-down {
                    border-left-color: #ef4444;
                }
                
                .metric-down .metric-value {
                    color: #ef4444;
                    text-shadow: 0 0 8px rgba(239,68,68,0.4);
                }
                
                .metric-neutral .metric-value {
                    color: #94a3b8;
                }
                
                /* Scrollbar */
                ::-webkit-scrollbar {
                    height: 8px;
                }
                
                ::-webkit-scrollbar-track {
                    background: rgba(30,41,59,0.5);
                    border-radius: 4px;
                }
                
                ::-webkit-scrollbar-thumb {
                    background: rgba(148,163,184,0.4);
                    border-radius: 4px;
                }
                
                ::-webkit-scrollbar-thumb:hover {
                    background: rgba(148,163,184,0.6);
                }
                </style>
                
                <div class="change-grid-pro">
                """ + cards_html + """
                </div>
                """,
                height=200
            )
        else:
            st.caption("No data yet")
# ======================
# SMALL MULTIPLE CHART
# ======================
def small_multiple_chart(df, indicator):
    import altair as alt

    return (
        alt.Chart(df)
        .transform_filter(
            alt.datum[indicator] != None
        )
        .mark_line(
            strokeWidth=2,
            interpolate="linear"
        )
        .encode(
            x=alt.X(
                "x:N",
                title=None,
                axis=alt.Axis(
                    labels=False,
                    ticks=False,
                    grid=False
                )
            ),
            y=alt.Y(
                f"{indicator}:Q",
                title=None,
                axis=alt.Axis(
                    grid=True,
                    gridOpacity=0.2,
                    domain=False
                )
            ),
            tooltip=[
                alt.Tooltip("x:N"),
                alt.Tooltip(f"{indicator}:Q", format=",.1f")
            ]
        )
        .properties(
            height=320,
            title=alt.TitleParams(
                text=indicator,
                anchor="start",
                fontSize=14,
                offset=6
            ),
            background="transparent"
        )
    )


# ======================
# 📊 ALL INDICATOR GROUPS — SMALL MULTIPLES (FULL WIDTH)
# ======================

st.markdown("### 📊 All indicator groups")

import plotly.graph_objects as go

# бүх group-ууд
all_groups = df_data.columns.get_level_values(0).unique()

NUM_COLS = 4
rows = [
    all_groups[i:i + NUM_COLS]
    for i in range(0, len(all_groups), NUM_COLS)
]

def group_chart_plotly(group_name):
    """Plotly график үүсгэх"""
    
    # 1️⃣ тухайн group-ийн бүх indicator
    inds = [
        col[1] for col in df_data.columns
        if col[0] == group_name and not pd.isna(col[1])
    ]
    
    # 2️⃣ суурь dataframe (TIME + INDICATORS)
    gdf = pd.DataFrame({
        "time": series["time"].values
    })
    
    # 🔥 indicator-уудыг НЭМНЭ
    for ind in inds:
        if (group_name, ind) in df_data.columns:
            gdf[ind] = df_data[(group_name, ind)].values
    
    # ⛔ SMALL CHART — 2020 оноос хойш
    gdf = gdf[gdf["time"] >= "2020"]
    
    # ✅ өгөгдөлтэй indicator-ууд
    valid_inds = [
        c for c in inds
        if c in gdf.columns and not gdf[c].isna().all()
    ]
    
    # 6️⃣ TIME FORMATTING
    if freq == "Monthly":
        gdf["time_dt"] = pd.to_datetime(gdf["time"], format="%Y-%m", errors="coerce")
    elif freq == "Quarterly":
        gdf["time_dt"] = pd.PeriodIndex(gdf["time"], freq="Q").to_timestamp()
    else:
        gdf["time_dt"] = pd.to_datetime(gdf["time"], errors="coerce")
    
    # 7️⃣ ХЭРВЭЭ ӨГӨГДӨЛ БАЙХГҮЙ БОЛ
    if not valid_inds:
        fig = go.Figure()
        fig.add_annotation(
            text="No data yet",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=13, color="#94a3b8")
        )
        fig.update_layout(
            height=320,
            title=dict(text=group_name, x=0, xanchor='left', font=dict(size=14)),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(l=6, r=6, t=40, b=6)
        )
        return fig
    
    # 8️⃣ ХЭРВЭЭ ӨГӨГДӨЛ БАЙВАЛ LINE
    fig = go.Figure()
    
    # Өнгөний палитр
    colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
    
    for i, ind in enumerate(valid_inds):
        color = colors[i % len(colors)]
        
        fig.add_trace(
            go.Scatter(
                x=gdf["time_dt"],
                y=gdf[ind],
                mode="lines",
                name=ind,
                line=dict(width=2, color=color),
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>" +
                    "Time: %{x|%Y-%m}<br>" +
                    "Value: %{y:.2f}<extra></extra>"
                )
            )
        )
    
    # 9️⃣ LAYOUT
    fig.update_layout(
        height=320,
        title=dict(
            text=group_name,
            x=0,
            xanchor='left',
            font=dict(size=14)
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title=None,
            showgrid=False,
            tickfont=dict(size=11),
            tickformat="%Y"
        ),
        yaxis=dict(
            title=None,
            showgrid=True,
            gridcolor="#334155",
            gridwidth=1,
            zeroline=False,
            tickfont=dict(size=11, color="#cbd5e1")
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
            bgcolor="rgba(0,0,0,0)"
        ),
        margin=dict(l=6, r=6, t=40, b=6),
        hovermode='x unified'
    )
    
    return fig
# RENDER CHARTS (ЭНЭ ХЭСЭГ ДУТУУ БАЙСАН!)

for row in rows:
    cols = st.columns(NUM_COLS, gap="small")
    for col, grp in zip(cols, row):
        with col:
            with st.container(border=True):
                chart = group_chart_plotly(grp)
                if chart is not None:
                    st.plotly_chart(chart, use_container_width=True, config={'displayModeBar': False})
# ======================
# 📄 RAW DATA — INDICATOR GROUP LEVEL
# ======================
with st.expander(f"📄 Raw data — {group} group"):
    
    # 1️⃣ тухайн group-д хамаарах бүх indicator
    group_cols = [
        col[1] for col in df_data.columns
        if col[0] == group and not pd.isna(col[1])
    ]

    if not group_cols:
        st.info("No indicators in this group.")
    else:
        raw_group_df = pd.DataFrame({
            "time": series["time"]
        })

        # 2️⃣ indicator-уудыг нэмэх
        for ind in group_cols:
            if (group, ind) in df_data.columns:
                raw_group_df[ind] = df_data[(group, ind)].values

        # 3️⃣ цэгцлэх
        raw_group_df = (
            raw_group_df
            .dropna(how="all", subset=group_cols)
            .sort_values("time")
            .reset_index(drop=True)
        )

        st.dataframe(
            raw_group_df,
            use_container_width=True
        )
