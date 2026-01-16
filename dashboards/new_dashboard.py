import streamlit as st
import pandas as pd
import altair as alt

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Macro Policy Dashboard (Excel)",
    layout="wide"
)

st.title("🏦 Macro Policy Dashboard (Excel-based)")
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
EXCEL_PATH = BASE_DIR / "20251218_Result.xlsx"

# ✅ Sheet names (NO cache)
all_sheets = pd.ExcelFile(EXCEL_PATH).sheet_names

sheet_names = [
    s for s in all_sheets
    if s.lower() in ["month", "monthly", "quarter", "quarterly"]
]

@st.cache_data
def read_sheet(sheet):
    return pd.read_excel(
        EXCEL_PATH,
        sheet_name=sheet,
        header=[0, 1]
    )

left_col, right_col = st.columns([1.4, 4.6], gap="large")

df_raw = read_sheet(dataset)
time_cols = [
    c for c in df_raw.columns
    if c[0] in ["Year", "Month", "Quarter", ""]
]
df_time = df_raw[time_cols]
# 🧭 Time columns-д нэр өгнө
df_time.columns = ["Year", "Month"] if len(df_time.columns) == 2 else ["Year", "Quarter"]
df_data = df_raw.drop(columns=time_cols)

# =====================================
# 🧹 CLEAN MULTIINDEX HEADERS (ЗӨВ ГАЗАР)
# =====================================
df_data.columns = pd.MultiIndex.from_tuples(
    [(str(a).strip(), str(b).strip()) for a, b in df_data.columns]
)

df_data.columns = pd.MultiIndex.from_tuples(
    [
        (
            a if not str(a).startswith("Unnamed") else prev,
            b
        )
        for (a, b), prev in zip(
            df_data.columns,
            pd.Series([c[0] for c in df_data.columns]).ffill()
        )
    ]
)

# ❌ Unnamed group-уудыг бүр мөсөн хасна
df_data = df_data.loc[
    :,
    ~df_data.columns.get_level_values(0).str.startswith("Unnamed")
]


with left_col:
    with st.container(border=True):
        st.markdown("### 📦 Dataset")
        dataset = st.radio("", sheet_names, horizontal=True)

# ================================
# 🧭 Indicator Group (АЛХАМ B)
# ================================
with left_col:
    with st.container(border=True):
        st.markdown("### 🧭 Indicator group")

        indicator_group = st.radio(
            "",
            sorted(df_data.columns.levels[0])
        )
# ================================
# 📌 Indicators (АЛХАМ C)
# ================================
with left_col:
    with st.container(border=True):
        st.markdown("### 📌 Indicators")

        indicators = sorted(
            c[1] for c in df_data.columns if c[0] == indicator_group
        )
        selected_indicators = st.multiselect(
            "",
            indicators,
            default=indicators[:1]
        )
        if "Month" in df_time.columns.get_level_values(0):
            freq = "Monthly"
        else:
            freq = "Quarterly"
        st.info(frequency := f"Frequency: {freq}")
series_df = pd.concat(
    [df_time] + [df_data[(indicator_group, ind)] for ind in selected_indicators],
    axis=1
)
series_df = series_df.dropna(how="all")
if freq == "Monthly":
    series_df["time_label"] = (
        series_df["Year"].astype(str)
        + "-"
        + series_df["Month"].astype(int).astype(str).str.zfill(2)
    )
else:
    series_df["time_label"] = (
        series_df["Year"].astype(str)
        + "-Q"
        + series_df["Quarter"].astype(str)
    )

series_df = series_df.dropna(subset=["time_label"])
with right_col:
    with st.container(border=True):
        st.markdown("### 📈 Main chart")

        plot_df = (
            series_df
            .set_index("time_label")[selected_indicators]
        )

        st.line_chart(plot_df)
with right_col:
    with st.container(border=True):
        st.markdown("### 📊 Latest values")

        kpi_cols = st.columns(len(selected_indicators))

        for col, ind in zip(kpi_cols, selected_indicators):
            values = plot_df[ind].dropna()
            latest = values.iloc[-1] if not values.empty else None
        
            if latest is not None:
                col.metric(ind, f"{latest:.2f}")
            else:
                col.metric(ind, "n/a")

with right_col:
    with st.container(border=True):
        st.markdown("### 🔄 Business cycle")

        cycle = plot_df.copy()
        cycle["phase"] = cycle.mean(axis=1)

        # 1️⃣ index → column болгоно
        cycle = cycle.reset_index().rename(columns={"index": "time_label"})

        # 2️⃣ 🆕 REAL TIME INDEX (professional fix)
        if freq == "Monthly":
            cycle["time_index"] = pd.to_datetime(
                cycle["time_label"],
                format="%Y-%m",
                errors="coerce"
            )
        else:
            cycle["time_index"] = pd.to_datetime(
                cycle["time_label"].str.replace("-Q", "-"),
                errors="coerce"
            )

        # 3️⃣ Altair chart
        chart = (
            alt.Chart(cycle)
            .mark_area(opacity=0.3)
            .encode(
                x=alt.X("time_index:T", title="Time"),
                y=alt.Y("phase:Q", title="Business cycle"),
                color=alt.condition(
                    "datum.phase >= 0",
                    alt.value("green"),
                    alt.value("red")
                )
            )
        )

        st.altair_chart(chart, use_container_width=True)

with right_col:
    with st.container(border=True):
        st.markdown("### 🧱 Contribution (Waterfall)")

        if plot_df.dropna(how="all").empty:
            st.warning("No data available for selected indicators.")
            st.stop()
        
        last = plot_df.dropna(how="all").iloc[-1]


        wf = pd.DataFrame({
            "Indicator": last.index,
            "Value": last.values
        })

        wf_chart = (
            alt.Chart(wf)
            .mark_bar()
            .encode(
                x="Indicator",
                y="Value"
            )
        )

        st.altair_chart(wf_chart, use_container_width=True)
with right_col:
    with st.container(border=True):
        st.markdown("### 📝 Insight")

        st.write(
            f"""
            **{indicator_group}** shows that  
            latest movements are driven mainly by  
            **{last.idxmax()}**.
            """
        )
with right_col:
    with st.expander("📄 Raw data"):
        st.dataframe(series_df, use_container_width=True)
