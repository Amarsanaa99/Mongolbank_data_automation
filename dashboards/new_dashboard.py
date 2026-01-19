import streamlit as st
import pandas as pd
from pathlib import Path

# ======================
# PAGE
# ======================
st.set_page_config("Macro Policy Dashboard", layout="wide")
st.title("🏦 Macro Policy Dashboard")
st.caption("Survey-based Macro Indicators")
st.success("🔥 APP STARTED — UI rendering OK")

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
# ======================
# ⏳ TIME RANGE (MAIN CHART ONLY)
# ======================
with left:
    with st.container(border=True):
        st.subheader("⏳ Time range")

        all_time = (
            series["time"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
        all_time = sorted(all_time)

        start_time = st.selectbox(
            "Start",
            options=all_time,
            index=0
        )

        end_time = st.selectbox(
            "End",
            options=all_time,
            index=len(all_time) - 1
        )


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
        
        # ======================
        # ⏳ APPLY TIME RANGE (MAIN CHART ONLY)
        # ======================
        chart_df = chart_df[
            (chart_df["x"] >= start_time) &
            (chart_df["x"] <= end_time)
        ]
    
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
                title="Date",
                axis=alt.Axis(
                    labelAngle=-45,
                    labelFontSize=11,
                    labelLimit=140,
                    grid=False
                )
            )
        ).properties(
            padding={"bottom": 60},   # 🔥 CARD ДООД ТАЛД ЗАЙ ӨГНӨ
            background="transparent"
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
                title="Value",
                axis=alt.Axis(
                    labelFontSize=11,
                    grid=True,
                    gridColor="#94a3b8",
                    gridOpacity=0.25,
                    gridWidth=0.6,
                    tickColor="#94a3b8",
                    domain=False
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
        st.altair_chart(
            lines.properties(height=520).interactive(),
            use_container_width=True
        )
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
                alt.Tooltip("x:N", title="Time"),
                alt.Tooltip(f"{indicator}:Q", format=",.2f")
            ]
        )
        .properties(
            height=400,
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

    # 2️⃣ суурь dataframe (БҮХ ОНУУД)
    gdf = pd.DataFrame({
        "time": series["time"].values
    })

    # 3️⃣ indicator-уудыг нэмэх
    for ind in inds:
        if (group_name, ind) in df_data.columns:
            gdf[ind] = df_data[(group_name, ind)].values

    # 4️⃣ TIME FILTER (дараа нь!)
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
            title="Date",
            axis=alt.Axis(
                labelAngle=-45, 
                grid=False,
                titleFontSize=10
                labelPadding=2,
                tickPadding=2
            )
        )
    ).properties(
        height=400,
        padding={"top": 8, "bottom": 4, "left": 8, "right":8},
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
                height=400,
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
            title="Value",
            axis=alt.Axis(
                grid=True,
                gridOpacity=0.25,
                domain=False,
                titleFontSize=11
            )
        ),
        color=alt.Color(
            "Indicator:N", 
            legend=alt.Legend(
                orient="bottom",
                direction="horizontal",
                title=None,
                labelFontSize=10,
                symbolSize=70,
                padding=2,
                offset=0
            )
        ),
        tooltip=[
            alt.Tooltip("time:N", title="Date"),
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
# RAW DATA (MAIN CHART-ААС ТУСАД НЬ)
# ======================
with st.expander("📄 Raw data"):
    if not plot_data.empty:
        st.dataframe(plot_data, use_container_width=True)
    else:
        st.info("No data available")
