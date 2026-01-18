import streamlit as st
import pandas as pd
from pathlib import Path

# ======================
# PAGE
# ======================
st.set_page_config("Macro Policy Dashboard", layout="wide")
st.title("🏦 Macro Policy Dashboard")

# ✅ GLOBAL STYLE (END USER QUALITY)
st.markdown("""
<style>
/* Page width control */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
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
    st.warning("⚠️ No indicators selected")
    st.stop()

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
# MAIN CHART (FAST, STABLE, NO melt, NO time)
# ======================
with right:
    with st.container(border=True):
        st.subheader("📈 Main chart")
        st.altair_chart(
            lines.properties(height=420).interactive(),
            use_container_width=True
        )
    # ===== 1️⃣ X-axis (Year / Month / Quarter)
    if "Month" in df_time.columns:
        chart_df = series[["Year", "Month"] + selected].copy()    
        year = chart_df["Year"]
        month = chart_df["Month"]
    
        # 🔒 ХОЁУЛАНГ НЬ ЗААВАЛ SERIES БОЛГОНО
        if isinstance(year, pd.DataFrame):
            year = year.iloc[:, 0]
    
        if isinstance(month, pd.DataFrame):
            month = month.iloc[:, 0]
    
        chart_df["x"] = (
            year.astype(int).astype(str)
            + "-"
            + month.astype(int).astype(str).str.zfill(2)
        )

    
    elif "Quarter" in df_time.columns:
        chart_df = series[["Year", "Quarter"] + selected].copy()
    
        year = chart_df["Year"]
        quarter = chart_df["Quarter"]
    
        if isinstance(year, pd.DataFrame):
            year = year.iloc[:, 0]
    
        if isinstance(quarter, pd.DataFrame):
            quarter = quarter.iloc[:, 0]
    
        chart_df["x"] = (
            year.astype(int).astype(str)
            + "-Q"
            + quarter.astype(int).astype(str)
        )

    else:
        chart_df = series[["Year"] + selected].copy()
        chart_df["x"] = chart_df["Year"].astype(int).astype(str)

    # ===== 2️⃣ өгөгдөлтэй indicator л үлдээнэ
    valid_indicators = [
        col for col in selected
        if col in chart_df.columns and not chart_df[col].isna().all()
    ]

    if not valid_indicators:
        st.warning("⚠️ No data available for selected indicator(s)")
        st.stop()

    # ===== 3️⃣ WIDE → Altair (FASTEST WAY)
    import altair as alt

    base = alt.Chart(chart_df).encode(
        x=alt.X(
            "x:N",
            title=None,
            axis=alt.Axis(
                labelAngle=-45,
                labelFontSize=11,
                grid=False          # ❌ GRID УНТРААНА
            )
        )
    ).properties(
        background="transparent"   # ✅ CARD-НЫ BACKGROUND-ТАЙ НИЙЦНЭ
    )
    
    lines = base.transform_fold(
        valid_indicators,
        as_=["Indicator", "Value"]
    ).mark_line(
        strokeWidth=2.2,
        interpolate="linear"       # ✅ ЭНГИЙН, POLICY STYLE
    ).encode(
        y=alt.Y(
            "Value:Q",
            title=None,
            axis=alt.Axis(
                labelFontSize=11,
                grid=False          # ❌ GRID УНТРААНА
            )
        ),
        color=alt.Color(
            "Indicator:N",
            legend=alt.Legend(
                title=None,
                orient="right"
            )
        ),
        tooltip=[
            alt.Tooltip("x:N", title="Time"),
            alt.Tooltip("Indicator:N"),
            alt.Tooltip("Value:Q", format=",.2f")
        ]
    )

# ======================
# RAW DATA (MAIN CHART-ААС ТУСАД НЬ)
# ======================
with st.expander("📄 Raw data"):
    if not plot_data.empty:
        st.dataframe(plot_data, use_container_width=True)
    else:
        st.info("No data available")
