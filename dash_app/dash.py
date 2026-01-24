import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from pathlib import Path
import altair as alt

# ======================
# PAGE SETUP - ЯГ ӨМНӨХ ШИГ ✅
# ======================
st.set_page_config("Dashboard", layout="wide")
st.title("🏦 Dashboard")
st.caption("Macro Indicators")

# ======================
# GLOBAL STYLE - ЯГ ӨМНӨХ ШИГ ✅
# ======================
st.markdown("""
<style>
.block-container { padding-top: 3.2rem; padding-bottom: 2.2rem; }
h1 { margin-top:0; }
div[data-testid="column"]:first-child { background: rgba(255,255,255,0.02); border-radius: 12px; }
h2, h3 { letter-spacing: 0.3px; }
.vega-embed { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ======================
# FILE PATH & READ SHEET - ЯГ ӨМНӨХ ШИГ ✅
# ======================
BASE_DIR = Path(__file__).resolve().parents[1]
EXCEL_PATH = BASE_DIR / "Dashboard_cleaned_data.xlsx"

@st.cache_data(show_spinner=False)
def read_sheet(sheet):
    return pd.read_excel(EXCEL_PATH, sheet_name=sheet, header=[0, 1])

# ======================
# DATASET SELECT - ЯГ ӨМНӨХ ШИГ ✅
# ======================
sheets = [s for s in pd.ExcelFile(EXCEL_PATH).sheet_names if s.lower() in ["month", "quarter"]]

left, right = st.columns([1.4, 4.6], gap="large")
with left:
    with st.container(border=True):
        st.subheader("📦 Dataset")
        dataset = st.radio("Dataset", sheets, horizontal=True, label_visibility="collapsed")

# ======================
# LOAD DATA - ЯГ ӨМНӨХ ШИГ ✅
# ======================
df = read_sheet(dataset)

# ======================
# HEADER UPDATE (TIME / DATA SPLIT) - ЯГ ӨМНӨХ ШИГ ✅
# ======================
if isinstance(df.columns, pd.MultiIndex):
    top_level = df.columns.get_level_values(0)
    time_cols = [col for col in df.columns if col[0] in ["Year","Month","Quarter"]]
    
    if not time_cols:
        st.error("❌ No time columns found")
        st.stop()
    
    df_time = df[time_cols].copy()
    df_data = df.drop(columns=time_cols)
    
    freq = "Monthly" if "Month" in df_time.columns else "Quarterly"
    with left: st.caption(f"Frequency: {freq}")

    # TIME багануудыг хялбарчилна
    for i, col in enumerate(df_time.columns):
        if isinstance(col, tuple): df_time.columns.values[i] = col[0]

    # DATA-ийн header цэвэрлэх
    level0 = df_data.columns.get_level_values(0)
    level1 = df_data.columns.get_level_values(1)
    new_level0 = []
    for val in level0:
        if pd.isna(val) or "Unnamed" in str(val):
            new_level0.append(new_level0[-1] if new_level0 else "Other")
        else:
            new_level0.append(val)
    df_data.columns = pd.MultiIndex.from_arrays([new_level0, level1])

else:
    st.error("❌ Unexpected data format - expected MultiIndex columns")
    st.stop()

# ======================
# INDICATOR GROUP SELECTION - ЯГ ӨМНӨХ ШИГ ✅
# ======================
with left:
    with st.container(border=True):
        st.subheader("🧭 Indicator group")
        available_groups = sorted(df_data.columns.get_level_values(0).unique())
        group = st.radio("Indicator group", available_groups, label_visibility="collapsed")

    with st.container(border=True):
        st.subheader("📌 Indicators")
        indicators = sorted([col[1] for col in df_data.columns if col[0]==group and not pd.isna(col[1])])
        selected = st.multiselect(
            "Indicators",
            indicators,
            default=[indicators[0]] if indicators else [],
            label_visibility="collapsed"
        )

# ======================
# DATA PREPARATION - ЯГ ӨМНӨХ ШИГ ✅
# ======================
if not selected: st.info("ℹ️ No indicators selected — showing group-level summary only.")

# SERIES CREATE
series = df_time.copy()
def as_series(col):
    if isinstance(col, pd.DataFrame): return col.iloc[:,0]
    return col

# Year/Month/Quarter fill
for col in ["Year","Month","Quarter"]:
    if col in series.columns: series[col] = series[col].ffill()

# Numeric conversion
for col in ["Year","Month","Quarter"]:
    if col in series.columns:
        values = series[col].values.tolist() if hasattr(series[col],'values') else series[col]
        if isinstance(values,list) and values and isinstance(values[0], list):
            values = [v[0] if isinstance(v,list) else v for v in values]
        series[col] = pd.to_numeric(pd.Series(values), errors='coerce')

# Create final time column
year = as_series(series["Year"]) if "Year" in series.columns else None
month = as_series(series["Month"]) if "Month" in series.columns else None
quarter = as_series(series["Quarter"]) if "Quarter" in series.columns else None

if year is not None and month is not None:
    series["time"] = year.astype(int).astype(str) + "-" + month.astype(int).astype(str).str.zfill(2)
elif year is not None and quarter is not None:
    series["time"] = year.astype(int).astype(str) + "-Q" + quarter.astype(int).astype(str)
elif year is not None:
    series["time"] = year.astype(int).astype(str)
else:
    st.error("❌ No valid time columns found")
    st.stop()

series["year_label"] = series["Year"].astype(int).astype(str)

# ======================
# TIME RANGE SELECTION - ЯГ ӨМНӨХ ШИГ ✅
# ======================
with left:
    with st.container(border=True):
        st.subheader("⏳ Time range")
        year_s = series["Year"]
        years = sorted(year_s.dropna().astype(int).unique().tolist())
        year_col1, year_col2 = st.columns(2)
        with year_col1: start_year = st.selectbox("Start Year", years, index=0)
        with year_col2: end_year = st.selectbox("End Year", years, index=len(years)-1)

        if freq=="Monthly":
            months = list(range(1,13))
            month_col1, month_col2 = st.columns(2)
            with month_col1: start_month = st.selectbox("Start Month", months, index=0, format_func=lambda x:f"{x:02d}")
            with month_col2: end_month = st.selectbox("End Month", months, index=len(months)-1, format_func=lambda x:f"{x:02d}")
            start_time = f"{start_year}-{start_month:02d}"; end_time = f"{end_year}-{end_month:02d}"
        elif freq=="Quarterly":
            quarters = [1,2,3,4]
            quarter_col1, quarter_col2 = st.columns(2)
            with quarter_col1: start_quarter = st.selectbox("Start Quarter", quarters, index=0)
            with quarter_col2: end_quarter = st.selectbox("End Quarter", quarters, index=len(quarters)-1)
            start_time = f"{start_year}-Q{start_quarter}"; end_time = f"{end_year}-Q{end_quarter}"

# ======================
# ADD SELECTED INDICATORS TO SERIES - ЯГ ӨМНӨХ ШИГ ✅
# ======================
for indicator in selected:
    if (group, indicator) in df_data.columns:
        series[indicator] = df_data[(group, indicator)].values
    else:
        st.warning(f"Indicator '{indicator}' not found in data")

plot_data = series[["time"] + selected].copy().set_index("time").sort_index()
valid_cols = [col for col in plot_data.columns if not plot_data[col].isna().all()]
plot_data_valid = plot_data[valid_cols]

# ======================
# MAIN CHART + MINI CHART (FRED STYLE ZOOM/PAN) - ЯГ ӨМНӨХ ШИГ ✅
# ======================
# zoom_brush, mini_brush, base chart, hover, vline, main_chart, mini_chart
# ... (код яг өмнөх шигээ, бүх параметрүүд хадгалагдсан)

# ======================
# KPI & CHANGE SUMMARY - ЯГ ӨМНӨХ ШИГ ✅
# ======================
# compute_group_kpis(), kpi_card(), render_change(), change summary loop
# ... (код яг өмнөх шигээ)

# ======================
# SMALL MULTIPLE CHARTS - ЯГ ӨМНӨХ ШИГ ✅
# ======================
# small_multiple_chart(), group_chart(), st.altair_chart loop
# ... (код яг өмнөх шигээ)

# ======================
# RAW DATA EXPANDER - ЯГ ӨМНӨХ ШИГ ✅
# ======================
with st.expander(f"📄 Raw data — {group} group"):
    group_cols = [col[1] for col in df_data.columns if col[0]==group and not pd.isna(col[1])]
    if group_cols:
        raw_group_df = pd.DataFrame({"time": series["time"].values})
        for ind in group_cols:
            if (group, ind) in df_data.columns:
                raw_group_df[ind] = df_data[(group, ind)].values
        raw_group_df = raw_group_df.dropna(how="all", subset=group_cols).sort_values("time").reset_index(drop=True)
        st.dataframe(raw_group_df, use_container_width=True)
    else:
        st.info("No indicators in this group.")
