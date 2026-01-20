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
    if value is None:
        return f"<span class='change-item'>{label}: N/A</span>"

    arrow = "▲" if value > 0 else "▼"
    cls = "change-up" if value > 0 else "change-down"

    return f"""
    <span class="change-item {cls}">
        <span class="change-arrow">{arrow}</span>
        {label}: {value:.2f}%
    </span>
    """


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
            padding={"bottom": 20},   # 🔥 CARD ДООД ТАЛД ЗАЙ ӨГНӨ
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
        points = base.transform_fold(
            valid_indicators,
            as_=["Indicator", "Value"]
        ).mark_point(
            opacity=0,
            size=80
        ).encode(
            y="Value:Q",
            tooltip=[
                alt.Tooltip("x:N", title="Time"),
                alt.Tooltip("Indicator:N"),
                alt.Tooltip("Value:Q", format=",.2f")
            ]
        )

        st.altair_chart(
            lines.properties(height=350).interactive(),
            width="stretch"
        )
    # ======================
    # 📉 CHANGE SUMMARY (BLOOMBERG STYLE)
    # ======================
    
    # ======================
    # 📉 CHANGE SUMMARY — PER INDICATOR
    # ======================
    st.markdown("### 📉 Change summary")
    
    cols = st.columns(len(selected))
    
    for col, ind in zip(cols, selected):
        with col:
            changes = None
            if ind in chart_df.columns and not chart_df[ind].isna().all():
                changes = compute_changes(chart_df, ind, freq)
    
            st.markdown(f"**{ind}**")
    
            if changes:
                st.markdown(
                    f"""
                    <div class="change-bar">
                        {render_change("YoY", changes["yoy"])}
                        {render_change("YTD", changes["ytd"])}
                        {render_change("Prev", changes["prev"])}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.caption("No data yet")

    
    def compute_group_kpis(df, indicators):
        stats = []
    
        for ind in indicators:
            if ind not in df.columns:
                continue
    
            s = pd.to_numeric(df[ind], errors="coerce").dropna()
            if s.empty:
                continue
    
            stats.append({
                "Indicator": ind,
                "Min": s.min(),
                "Max": s.max(),
                "Mean": s.mean(),
                "Median": s.median(),
                "Std": s.std(),
                "Last": s.iloc[-1]
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
    
        /* 🔥 АМЬСГАЛ */
        margin: 10px 0;   /* дээд/доод */
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
    /* ======================
    CHANGE BAR (Bloomberg style)
    ====================== */
    .change-bar {
        display: flex;
        gap: 18px;
        padding: 8px 14px;
        border-radius: 14px;
        background: rgba(15, 23, 42, 0.45);
        border: 1px solid rgba(148,163,184,0.25);
        margin: 10px 0 14px 0;
    }
    
    .change-item {
        font-size: 13px;
        font-weight: 500;
        color: #e5e7eb;
    }
    
    .change-up {
        color: #22c55e;
    }
    
    .change-down {
        color: #ef4444;
    }
    
    .change-arrow {
        font-size: 14px;
        margin-right: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ===== KPI CARD HELPER (OUTSIDE BLOCK)
    def kpi_card(label, value):
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("### 📌 Indicator-level KPIs")
    
    if kpi_main.empty:
        st.info("No KPI data available.")
    else:
        row = kpi_main.iloc[0]
        with st.container(border=True):
            st.subheader(f"📊 {row['Indicator']}")
    
            cols = st.columns(6)
    
            with cols[0]:
                kpi_card("MINIMUM VALUE", f"{row['Min']:.2f}")
            with cols[1]:
                kpi_card("MAXIMUM VALUE", f"{row['Max']:.2f}")
            with cols[2]:
                kpi_card("MEAN", f"{row['Mean']:.2f}")
            with cols[3]:
                kpi_card("MEDIAN", f"{row['Median']:.2f}")
            with cols[4]:
                kpi_card("STD (VOTATILITY)", f"{row['Std']:.2f}")
            with cols[5]:
                kpi_card("LAST VALUE", f"{row['Last']:.2f}")
                
    # ✅ ЭНЭ МӨР — KPI SECTION-ИЙГ "АМЬСГАЛТАЙ" БОЛГОНО
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

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
                titleFontSize=12,
                labelFontSize=11
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
            title="Value",
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
