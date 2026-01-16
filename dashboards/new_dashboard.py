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

BASE_DIR = Path(__file__).resolve().parents[1]   # ROOT руу гарна
EXCEL_PATH = BASE_DIR / "20251218_Result.xlsx"


@st.cache_data
def load_excel():
    return pd.ExcelFile(EXCEL_PATH)

xls = load_excel()
left_col, right_col = st.columns([1.4, 4.6], gap="large")
with left_col:
    with st.container(border=True):
        st.markdown("### 📦 Dataset")
        dataset = st.radio(
            "",
            xls.sheet_names,
            horizontal=True
        )
@st.cache_data
def read_sheet(sheet):
    return pd.read_excel(
        EXCEL_PATH,
        sheet_name=sheet,
        header=[0, 1]
    )

df_raw = read_sheet(dataset)
time_cols = [
    c for c in df_raw.columns
    if c[0] in ["Year", "Month", "Quarter", ""]
]

df_time = df_raw[time_cols]
df_data = df_raw.drop(columns=time_cols)

df_data.columns = pd.MultiIndex.from_tuples(
    [(str(a).strip(), str(b).strip()) for a, b in df_data.columns]
)
with left_col:
    with st.container(border=True):
        st.markdown("### 📐 GDP type")
        gdp_types = sorted(df_data.columns.levels[0])
        gdp_type = st.radio("", gdp_types)
with left_col:
    with st.container(border=True):
        st.markdown("### 📌 Indicators")

        indicators = sorted(
            c[1] for c in df_data.columns if c[0] == gdp_type
        )

        selected_indicators = st.multiselect(
            "",
            indicators,
            default=indicators[:1]
        )
with left_col:
    with st.container(border=True):
        st.markdown("### ⏱ Frequency")

        if "Month" in df_time.columns.get_level_values(0):
            freq = "Monthly"
        else:
            freq = "Quarterly"

        st.info(frequency := f"Frequency: {freq}")
series_df = pd.concat(
    [df_time] + [df_data[(gdp_type, ind)] for ind in selected_indicators],
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
            **{gdp_type}** shows that  
            latest movements are driven mainly by  
            **{last.idxmax()}**.
            """
        )
with right_col:
    with st.expander("📄 Raw data"):
        st.dataframe(series_df, use_container_width=True)
