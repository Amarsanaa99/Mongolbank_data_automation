import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from pathlib import Path

# ======================
# PAGE
# ======================
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

# ======================
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
        if col.shape[1] == 1:
            return col.iloc[:, 0]
        else:
            return col.iloc[:, 0]
    elif isinstance(col, pd.Series):
        return col
    else:
        return pd.Series(col)

# ======================
# FIX: Year / Month / Quarter block structure
# ======================
for col in ["Year", "Month", "Quarter"]:
    if col in series.columns:
        series[col] = series[col].ffill()

# Time багануудыг тоон утга болгох
for col in ["Year", "Month", "Quarter"]:
    if col in series.columns:
        values = series[col].values.tolist() if hasattr(series[col], 'values') else series[col]
        if isinstance(values, list) and values and isinstance(values[0], list):
            values = [v[0] if isinstance(v, list) else v for v in values]
        series[col] = pd.to_numeric(pd.Series(values), errors='coerce')

# ======================
# CREATE TIME INDEX (FINAL, SAFE)
# ======================
# re module импортлох
import re

# Багануудыг Series болгох
if "Year" in series.columns:
    year_series = as_series(series["Year"])
else:
    year_series = None
    
if "Month" in series.columns:
    month_series = as_series(series["Month"])
else:
    month_series = None
    
if "Quarter" in series.columns:
    quarter_series = as_series(series["Quarter"])
else:
    quarter_series = None

# Хэрэв Year багана байхгүй бол DataFrame-ийн эхний баганыг ашиглах
if year_series is None and len(series.columns) > 0:
    year_series = as_series(series.iloc[:, 0])
    st.warning("⚠️ Year column not found - using first column as year")

# time багана үүсгэх
if year_series is not None and month_series is not None:
    # NaN утгуудыг цэвэрлэх
    mask = year_series.notna() & month_series.notna()
    if mask.any():
        series["time"] = (
            year_series.astype(int).astype(str) + "-" +
            month_series.astype(int).astype(str).str.zfill(2)
        )
    else:
        st.error("❌ No valid Year and Month data found")
        st.stop()

elif year_series is not None and quarter_series is not None:
    # NaN утгуудыг цэвэрлэх
    mask = year_series.notna() & quarter_series.notna()
    if mask.any():
        series["time"] = (
            year_series.astype(int).astype(str) + "-Q" +
            quarter_series.astype(int).astype(str)
        )
    else:
        st.error("❌ No valid Year and Quarter data found")
        st.stop()

elif year_series is not None:
    # Зөвхөн жил байгаа тохиолдолд
    mask = year_series.notna()
    if mask.any():
        series["time"] = year_series.astype(int).astype(str)
    else:
        st.error("❌ No valid Year data found")
        st.stop()

else:
    st.error("❌ No valid time columns found")
    st.stop()

# ======================
# ✅ CREATE time_dt COLUMN FOR CHART
# ======================
def parse_time(time_str):
    if pd.isna(time_str):
        return pd.NaT
        
    if isinstance(time_str, str):
        time_str = str(time_str).strip()
        
        # Сарны форматыг шалгах: "2020-01"
        if re.match(r'^\d{4}-\d{2}$', time_str):
            try:
                year = int(time_str[:4])
                month = int(time_str[5:7])
                return pd.Timestamp(year=year, month=month, day=1)
            except:
                pass
                
        # Улирлын форматыг шалгах: "2020-Q1"
        if re.match(r'^\d{4}-Q[1-4]$', time_str, re.IGNORECASE):
            try:
                year = int(time_str[:4])
                quarter = int(time_str.split('-')[1][1:])
                month = (quarter - 1) * 3 + 1
                return pd.Timestamp(year=year, month=month, day=1)
            except:
                pass
                
        # Зөвхөн жил: "2020"
        if re.match(r'^\d{4}$', time_str):
            try:
                year = int(time_str)
                return pd.Timestamp(year=year, month=1, day=1)
            except:
                pass
    
    return pd.NaT

series["time_dt"] = series["time"].apply(parse_time)

# Хэрэв time_dt үүсэхгүй бол энгийн datetime үүсгэх
if series["time_dt"].isna().all():
    st.warning("⚠️ Could not parse time format - using sequential dates")
    start_date = pd.Timestamp('2000-01-01')
    series["time_dt"] = [start_date + pd.DateOffset(months=i) for i in range(len(series))]

# ======================
# ✅ YEAR LABEL (GLOBAL X AXIS)
# ======================
if "Year" in series.columns:
    series["year_label"] = series["Year"].astype(int).astype(str)

for col in ["Year", "Month", "Quarter"]:
    if col in series.columns:
        series[col] = as_series(series[col])
# ======================
# ⏳ TIME RANGE (MAIN CHART ONLY)
# ======================
# ======================
# ⏳ TIME RANGE (MAIN CHART ONLY)
# ======================
with left:
    with st.container(border=True):
        st.subheader("⏳ Time range")
    
        # Жилийн сонголт
        year_s = series["Year"]
        if isinstance(year_s, pd.DataFrame):
            year_s = year_s.iloc[:, 0]
        
        years = sorted(
            year_s.dropna().astype(int).unique().tolist()
        )
        
        # Эхлэх жил
        start_year = st.selectbox(
            "Start Year",
            years,
            index=0
        )
        
        # Дуусах жил
        end_year = st.selectbox(
            "End Year",
            years,
            index=len(years)-1
        )
        
        # Сар эсвэл улирлын сонголт
        if freq == "Monthly":
            months = list(range(1, 13))
            
            # Эхлэх сар
            start_month = st.selectbox(
                "Start Month",
                months,
                index=0,
                format_func=lambda x: f"{x:02d}"
            )
            
            # Дуусах сар
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
            
            # Эхлэх улирал
            start_quarter = st.selectbox(
                "Start Quarter",
                quarters,
                index=0
            )
            
            # Дуусах улирал
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
# MAIN CHART (FAST, STABLE, NO melt, NO time)
# ======================
with right:
    with st.container(border=True):
        st.subheader("📈 Main chart")

        # ===== 1️⃣ ШАЛГАЛТ: series дотор шаардлагатай баганууд байгаа эсэх
        if "time" not in series.columns:
            st.error("❌ 'time' column not found in series")
            st.stop()
            
        if "time_dt" not in series.columns:
            st.error("❌ 'time_dt' column not found in series")
            st.stop()
        
        if not selected:
            st.warning("⚠️ No indicators selected")
            st.stop()

        # ===== 2️⃣ DATA
        try:
            chart_df = series[["time", "time_dt"] + selected].copy()
        except KeyError as e:
            st.error(f"❌ Column error: {e}")
            st.stop()
        
        # ===== 3️⃣ ШАЛГАЛТ: chart_df хоосон эсэх
        if chart_df.empty:
            st.warning("⚠️ No data available")
            st.stop()
        
        # ===== 4️⃣ ЦАГ ХУГАЦААНЫ ХЯЗГААРЛАЛТ
        try:
            chart_df = chart_df[
                (chart_df["time"] >= start_time) &
                (chart_df["time"] <= end_time)
            ]
        except Exception as e:
            st.error(f"❌ Time range filter error: {e}")
            st.stop()
        
        # ===== 5️⃣ ШАЛГАЛТ: шүүлтүүр хийсний дараа хоосон эсэх
        if chart_df.empty:
            st.warning(f"⚠️ No data in selected time range: {start_time} to {end_time}")
            st.stop()

        # ===== 6️⃣ ШАЛГАЛТ: time_dt datetime төрөлтэй эсэх
        if not pd.api.types.is_datetime64_any_dtype(chart_df["time_dt"]):
            st.warning("⚠️ Converting time_dt to datetime")
            chart_df["time_dt"] = pd.to_datetime(chart_df["time_dt"], errors='coerce')
        
        # ===== 7️⃣ Valid indicators
        valid_indicators = [
            col for col in selected
            if col in chart_df.columns and not chart_df[col].isna().all()
        ]

        if not valid_indicators:
            st.warning("⚠️ No data available for selected indicator(s)")
            st.stop()

        # ===== 8️⃣ ШАЛГАЛТ: мэдээлэл хангалттай эсэх
        # Хамгийн багадаа 2 цэг байх ёстой
        min_data_points = 2
        valid_indicators_with_data = []
        
        for ind in valid_indicators:
            non_na_count = chart_df[ind].notna().sum()
            if non_na_count >= min_data_points:
                valid_indicators_with_data.append(ind)
            else:
                st.warning(f"⚠️ Indicator '{ind}' has only {non_na_count} data point(s) - needs at least {min_data_points}")
        
        if not valid_indicators_with_data:
            st.warning("⚠️ No indicators have enough data points")
            st.stop()
        
        valid_indicators = valid_indicators_with_data

        # ===== 9️⃣ BASE
        import altair as alt

        # Өгөгдлийг эрэмбэлэх
        chart_df = chart_df.sort_values("time_dt").reset_index(drop=True)
        
        base = alt.Chart(chart_df).encode(
            x=alt.X(
                "time_dt:T",
                title=None,
                axis=alt.Axis(
                    labelAngle=0,
                    labelFontSize=11,
                    grid=False,
                    format="%Y-%m"  # Цагийн форматыг тодорхойлох
                )
            )
        )

        # ===== 🔟 Folded data
        folded = base.transform_fold(
            valid_indicators,
            as_=["Indicator", "Value"]
        )

        # ===== 1️⃣1️⃣ Hover selection
        hover = alt.selection_point(
            encodings=["x"],
            nearest=True,
            on="mouseover",
            empty="none"
        )
        
        # ===== 1️⃣2️⃣ Invisible selector layer
        selectors = base.mark_point(
            opacity=0,
            size=200  # Hover талбарыг томруулах
        ).encode(
            x="time_dt:T"
        ).add_params(
            hover
        )

        # ===== 1️⃣3️⃣ Lines
        lines = folded.mark_line(
            strokeWidth=2.2,
            interpolate='linear'
        ).encode(
            x="time_dt:T",
            y=alt.Y(
                "Value:Q",
                title=None,
                axis=alt.Axis(
                    grid=True,
                    gridColor="#e2e8f0",
                    gridOpacity=0.3
                )
            ),
            color=alt.Color(
                "Indicator:N",
                legend=alt.Legend(
                    title="Indicators",
                    orient="top",
                    labelLimit=200
                )
            )
        ).add_params(
            hover
        )

        # ===== 1️⃣4️⃣ Vertical line
        vline = alt.Chart(chart_df).mark_rule(
            color="#64748b",
            strokeWidth=1.2,
            strokeDash=[5, 5]
        ).encode(
            x="time_dt:T",
            opacity=alt.condition(hover, alt.value(0.7), alt.value(0))
        )

        # ===== 1️⃣5️⃣ Hover points + tooltip
        hover_points = folded.mark_point(
            size=100,
            filled=True,
            strokeWidth=2,
            stroke="white"
        ).encode(
            x="time_dt:T",
            y="Value:Q",
            opacity=alt.condition(hover, alt.value(1), alt.value(0)),
            color="Indicator:N",
            tooltip=[
                alt.Tooltip("time:N", title="Time Period"),
                alt.Tooltip("Indicator:N", title="Indicator"),
                alt.Tooltip("Value:Q", title="Value", format=",.3f")
            ]
        )

        # ===== 1️⃣6️⃣ Layered chart
        chart = (
            lines
            + vline
            + hover_points
            + selectors
        ).properties(
            height=340,
            padding={"bottom": 5, "top": 5, "left": 5, "right": 5},
            background="transparent"
        ).configure_view(
            strokeWidth=0
        )
        
        # ===== 1️⃣7️⃣ Графикийг харуулах
        try:
            st.altair_chart(chart, width='stretch') 
        except Exception as e:
            st.error(f"❌ Error displaying chart: {e}")
            # Алдааг илүү дэлгэрэнгүй харуулах
            st.write("Debug info:")
            st.write(f"chart_df shape: {chart_df.shape}")
            st.write(f"chart_df columns: {chart_df.columns.tolist()}")
            st.write(f"valid_indicators: {valid_indicators}")
            if not chart_df.empty:
                st.write("First few rows:")
                st.write(chart_df.head())





    
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
                last_value = float(raw_val.iloc[0]) if isinstance(raw_val, pd.Series) else float(raw_val)
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
    # ======================
    # 📊 KPI CALCULATION (INDICATOR LEVEL)
    # ======================
    
    # 🔹 БҮХ indicator-уудын KPI-г НЭГ УДАА бодно
    kpi_df = compute_group_kpis(chart_df, group_indicators)
    
    # 🔹 KPI-д харуулах PRIMARY indicator
    primary_indicator = selected[0]
    
    # 🔹 KPI-г салгах
    kpi_main = kpi_df[kpi_df["Indicator"] == primary_indicator]
    kpi_rest = kpi_df[kpi_df["Indicator"] != primary_indicator]
    
    st.markdown("""
    <style>
    .kpi-card {
        background: linear-gradient(
            180deg,
            rgba(15, 23, 42, 0.85),
            rgba(15, 23, 42, 0.65)
        );
        border: 1px solid rgba(59,130,246,0.25);
        border-radius: 16px;
        padding: 10px 14px;
        margin: 10px 0;
    
        /* ✅ ЭНЭ 1 МӨР */
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 24px rgba(0,0,0,0.25);
    }

    .kpi-label {
        font-size: 11px;
        color: #93c5fd;
        letter-spacing: 0.06em;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 600;
        color: #3b82f6;
    }
    .kpi-sub {
    font-size: 11px;
    opacity: 0.6;
    margin-top: -2px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ===== KPI CARD HELPER (OUTSIDE BLOCK)
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


        
    # 🔥 HEADER ROW — INLINE
    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 6px;
            margin-bottom: 4px;
        ">
            <span style="font-size: 1.25rem; font-weight: 600;">
                📌 Indicator-level KPIs
            </span>
            <span style="opacity: 0.6;">➜</span>
            <span style="font-size: 1.25rem; font-weight: 600; color: #60a5fa;">
                📊 {primary_indicator}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if kpi_main.empty:
        st.info("No KPI data available.")
        st.stop()
        
    row = kpi_main.iloc[0]   # ✅ row ЭНД Л ҮҮСНЭ

    # 🔽 KPI CARDS (ӨМНӨХӨӨРӨӨ)
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
        kpi_card("STD (VOTATILITY)", f"{row['Std']:.2f}")

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
    # 📉 CHANGE SUMMARY — GROUP LEVEL (FIXED)
    # ======================
    st.markdown("### 📉 Change summary")
    
    # 🔥 Change summary-д ашиглах indicator-ууд
    if selected:
        change_indicators = selected
    else:
        # fallback: group-level (хэрвээ юу ч сонгоогүй бол)
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
                cards_html += f"""
                <div class="change-card">
                    <div class="change-title">{ind}</div>
                    <div class="change-bar">
                        {render_change("YoY", changes.get("yoy"))}
                        {render_change("YTD", changes.get("ytd"))}
                        {render_change("Prev", changes.get("prev"))}
                    </div>
                </div>
                """
    
        # ✅ LOOP ДУУССАНЫ ДАРАА ГАНЦ УДАА RENDER
        if cards_html:
            components.html(
            """
            <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            .change-bar {
                display: flex;
                flex-direction: column;
                gap: 6px;
                margin-top: 6px;
            }
            .change-item {
                display: block;
                font-size: 13px;
                line-height: 1.4;
            }

            .change-grid {
                display: flex;
                gap: 12px;
                overflow-x: auto;
                padding: 6px 2px;
            }
            
            .change-card {
                width: fit-content;
                min-width: unset;
                padding: 10px 14px;
            
                background: linear-gradient(
                    180deg,
                    rgba(15, 23, 42, 0.85),
                    rgba(15, 23, 42, 0.65)
                );
                border: 1px solid rgba(148,163,184,0.25);
                border-radius: 16px;
            
                white-space: nowrap;   /* 🔥 яг бичвэртээ таарна */
                transition: all 0.2s ease;
            }

            .change-card:hover {
                transform: translateY(-4px);
                border-color: rgba(148,163,184,0.4);
                box-shadow: 0 12px 24px rgba(0,0,0,0.2);
            }
            
            .change-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 16px;
                padding-bottom: 12px;
                border-bottom: 1px solid rgba(148,163,184,0.1);
            }
            
            .change-title {
                font-size: 14px;
                font-weight: 600;
                color: #e2e8f0;
                line-height: 1.4;
                max-width: 60%;
            }
            
            .change-latest {
                font-size: 24px;
                font-weight: 700;
                color: #60a5fa;
                text-shadow: 0 2px 8px rgba(96,165,250,0.3);
            }
            .change-up {
                color: #22c55e;        /* green */
                font-weight: 600;
            }
            
            .change-down {
                color: #ef4444;        /* red */
                font-weight: 600;
            }
            
            .change-arrow {
                margin-right: 4px;
            }

            .change-metrics {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 12px;
            }
            
            .metric-item {
                display: flex;
                flex-direction: column;
                gap: 4px;
                padding: 10px;
                background: rgba(30,41,59,0.5);
                border-radius: 8px;
                transition: all 0.2s ease;
                border: 1px solid transparent;
            }
            
            .metric-item:hover {
                background: rgba(30,41,59,0.8);
                border-color: rgba(148,163,184,0.3);
            }
            
            .metric-label {
                font-size: 11px;
                font-weight: 600;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .metric-value {
                font-size: 16px;
                font-weight: 700;
                font-family: 'Monaco', 'Courier New', monospace;
            }
            
            .metric-up .metric-value {
                color: #22c55e;
                text-shadow: 0 0 8px rgba(34,197,94,0.4);
            }
            
            .metric-down .metric-value {
                color: #ef4444;
                text-shadow: 0 0 8px rgba(239,68,68,0.4);
            }
            
            .metric-neutral .metric-value {
                color: #94a3b8;
            }
            
            /* Scrollbar styling */
            ::-webkit-scrollbar {
                height: 8px;
                width: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: rgba(30,41,59,0.5);
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb {
                background: rgba(148,163,184,0.3);
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: rgba(148,163,184,0.5);
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .change-grid {
                    grid-template-columns: 1fr;
                }
            }
            </style>
            
            <div class="change-grid">
            """+ cards_html+"""
            </div>
            """,
            height=120
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
                alt.Tooltip(f"{indicator}:Q", format=",.2f")
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

import altair as alt

# бүх group-ууд
all_groups = df_data.columns.get_level_values(0).unique()

NUM_COLS = 4
rows = [
    all_groups[i:i + NUM_COLS]
    for i in range(0, len(all_groups), NUM_COLS)
]

def group_chart(group_name):
    import altair as alt

    # 1️⃣ тухайн group-ийн бүх indicator
    inds = [
        col[1] for col in df_data.columns
        if col[0] == group_name and not pd.isna(col[1])
    ]

    # 2️⃣ суурь dataframe (YEAR + INDICATORS)
    gdf = pd.DataFrame({
        "time": series["time"].values
    })
    
    # 🔥 indicator-уудыг НЭМНЭ
    for ind in inds:
        if (group_name, ind) in df_data.columns:
            gdf[ind] = df_data[(group_name, ind)].values
    # ⛔ SMALL CHART — 2020 оноос хойш
    gdf = gdf[gdf["time"] >= "2020"]



    # ✅ 5️⃣ өгөгдөлтэй indicator-ууд
    valid_inds = [
        c for c in inds
        if c in gdf.columns and not gdf[c].isna().all()
    ]

    # 6️⃣ BASE CHART (үргэлж харагдана)
    base = alt.Chart(gdf).encode(
        x=alt.X(
            "time:N",
            title=None,
            sort="ascending",
            axis=alt.Axis(
                labelAngle=0,
                grid=False,
                labelFontSize=11,
                labelExpr="substring(datum.value, 0, 4)"
            )
        )
    ).properties(
        height=320,
        padding={"top": 6, "bottom": 0, "left": 6, "right": 6},
        title=alt.TitleParams(
            text=group_name,
            anchor="start",
            fontSize=14,
            offset=6
        ),
        background="transparent"
    )


    # 7️⃣ ХЭРВЭЭ ӨГӨГДӨЛ БАЙХГҮЙ БОЛ
    if not valid_inds:
        return (
            alt.Chart(
                pd.DataFrame({"x": [0], "y": [0], "label": ["No data yet"]})
            )
            .mark_text(
                align="center",
                baseline="middle",
                fontSize=13,
                color="#94a3b8"
            )
            .encode(
                x=alt.X("x:Q", axis=None),
                y=alt.Y("y:Q", axis=None),
                text="label:N"
            )
            .properties(
                height=320,
                title=alt.TitleParams(
                    text=group_name,
                    anchor="start",
                    fontSize=14,
                    offset=6
                ),
                background="transparent"
            )
        )

    # 8️⃣ ХЭРВЭЭ ӨГӨГДӨЛ БАЙВАЛ LINE
    lines = base.transform_fold(
        valid_inds,
        as_=["Indicator", "Value"]
    ).mark_line(strokeWidth=2).encode(
        y=alt.Y(
            "Value:Q",
            title=None,
            axis=alt.Axis(
                grid=True,
                gridColor="#334155",   # 🔥 GRID COLOR (slate-700)
                gridOpacity=0.45,      # 🔥 илүү тод
                gridWidth=1,           # 🔥 нимгэн
                domain=False,
                tickColor="#475569",   # (сонголт)
                labelColor="#cbd5e1",  # (сонголт)
                titleColor="#e5e7eb",
                labelFontSize=11,
                titleFontSize=12
            )
        ),
        color=alt.Color(
            "Indicator:N", 
            legend=alt.Legend(
                orient="bottom",
                direction="horizontal",
                title=None,
                labelLimit=150,
                labelFontSize=11,
                symbolSize=80,
                symbolStrokeWidth=2,
                columnPadding=4,
                padding=0,
                offset=2
            )
        ),
        tooltip=[
            alt.Tooltip("time:N"),
            alt.Tooltip("Indicator:N"),
            alt.Tooltip("Value:Q", format=",.2f")
        ]
    )

    return lines



for row in rows:
    cols = st.columns(NUM_COLS, gap="small")
    for col, grp in zip(cols, row):
        with col:
            with st.container(border=True):
                chart = group_chart(grp)
                if chart is not None:
                    st.altair_chart(chart, use_container_width=True)


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
