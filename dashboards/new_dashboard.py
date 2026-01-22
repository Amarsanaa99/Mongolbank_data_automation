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

        import altair as alt
        
        # ===== 3️⃣ TIME FORMATTING FOR DETAILED X-Axis
        chart_df = chart_df.copy()
        chart_df['time_detailed'] = chart_df['time'].astype(str)
        
        # ===== 4️⃣ BASE CHART (shared X scale)
        base = (
            alt.Chart(chart_df)
            .transform_fold(
                valid_indicators,
                as_=["Indicator", "Value"]
            )
            .encode(
                x=alt.X(
                    'time:T',
                    title=None,
                    axis=alt.Axis(
                        format='%Y-%m',
                        labelAngle=0,
                        labelFontSize=11,
                        grid=False,
                        labelExpr="timeFormat(datum.value, '%Y-%m')"
                    ),
                    scale=alt.Scale(zero=False)
                ),
                y=alt.Y(
                    "Value:Q",
                    title=None,
                    axis=alt.Axis(
                        grid=True,
                        gridOpacity=0.25,
                        domain=False,
                        labelFontSize=11
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
                    alt.Tooltip('time:T', title="Time", format='%Y-%m-%d'),
                    alt.Tooltip("Indicator:N"),
                    alt.Tooltip("Value:Q", format=",.2f")
                ]
            )
        )
        
        # ===== 5️⃣ HOVER EFFECT (FRED style)
        # Hover selection үүсгэх
        hover = alt.selection_point(
            fields=['time'],
            nearest=True,
            on='mouseover',
            empty=False,
            clear='mouseout'
        )
        
        # 1. Гол шугам
        line_chart = base.mark_line(strokeWidth=2.4)
        
        # 2. Hover үед бүх шугамын хувьд босоо шугам
        vertical_rule = (
            alt.Chart(chart_df)
            .mark_rule(color='gray', strokeWidth=1, strokeDash=[5, 5])
            .encode(
                x='time:T',
                opacity=alt.condition(hover, alt.value(0.8), alt.value(0))
            )
            .add_params(hover)
        )
        
        # 3. Hover цэг дээрх дугуй цагираг
        hover_points = (
            base
            .mark_circle(size=60, opacity=1, strokeWidth=2)
            .encode(
                opacity=alt.condition(hover, alt.value(1), alt.value(0)),
                stroke=alt.Color("Indicator:N", legend=None),
                strokeWidth=alt.value(2)
            )
            .add_params(hover)
        )
        
        # 4. Hover үед утгыг харуулах текст
        hover_text = (
            base
            .mark_text(
                align='left',
                dx=5,
                dy=-15,
                fontSize=11,
                fontWeight='bold'
            )
            .encode(
                text=alt.condition(
                    hover,
                    alt.Text('Value:Q', format='.2f'),
                    alt.value('')
                ),
                opacity=alt.condition(hover, alt.value(0.9), alt.value(0))
            )
            .add_params(hover)
        )
        
        # 5. Hover үед огноо харуулах текст
        date_text = (
            alt.Chart(chart_df)
            .mark_text(
                align='center',
                dy=30,
                fontSize=11,
                fontWeight=500
            )
            .encode(
                x='time:T',
                text=alt.condition(
                    hover,
                    alt.Text('time:T', format='%Y-%m'),
                    alt.value('')
                ),
                opacity=alt.condition(hover, alt.value(0.9), alt.value(0))
            )
            .transform_filter(hover)
            .add_params(hover)
        )
        
        # Бүх chart-уудыг нэгтгэх
        main_chart = (
            (line_chart + vertical_rule + hover_points + hover_text + date_text)
            .properties(height=360)
            .interactive()
        )
        
        # ===== 6️⃣ MINI OVERVIEW (CONTEXT NAVIGATOR)
        brush = alt.selection_interval(encodings=["x"], translate=False, zoom=True)
        
        mini_chart = (
            base
            .mark_line(strokeWidth=1.2)
            .encode(
                y=alt.Y(
                    "Value:Q",
                    title=None,
                    axis=alt.Axis(
                        labels=False,
                        ticks=False,
                        grid=False,
                        domain=False
                    )
                ),
                color=alt.Color("Indicator:N", legend=None)
            )
            .properties(height=70)
            .add_params(brush)
        )
        
        # ===== 7️⃣ LINK MAIN ↔ MINI
        final_chart = (
            alt.vconcat(
                main_chart.add_params(brush),
                mini_chart,
                spacing=10
            )
            .properties(background="transparent")
            .configure_axis(grid=True, gridColor='#e0e0e0')
        )
        
        st.altair_chart(final_chart, use_container_width=True)

    
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
