import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# ======================
# PAGE
# ======================
st.set_page_config("Macro Policy Dashboard", layout="wide")
st.title("🏦 Macro Policy Dashboard")

BASE_DIR = Path(__file__).resolve().parents[1]
EXCEL_PATH = BASE_DIR / "20251218_Result.xlsx"

@st.cache_data
def read_sheet(sheet):
    return pd.read_excel(EXCEL_PATH, sheet_name=sheet, header=[0, 1])

# ======================
# DATASET SELECT
# ======================
sheets = [s for s in pd.ExcelFile(EXCEL_PATH).sheet_names
          if s.lower() in ["month","monthly","quarter","quarterly"]]

left, right = st.columns([1.4, 4.6], gap="large")

with left:
    dataset = st.radio("📦 Dataset", sheets, horizontal=True)

# ======================
# LOAD + CLEAN DATA
# ======================
df = read_sheet(dataset)

time_cols = [c for c in df.columns if c[0] in ["Year","Month","Quarter",""]]
df_time = df[time_cols]
df_time.columns = ["Year","Month"] if len(df_time.columns)==2 else ["Year","Quarter"]

df_data = df.drop(columns=time_cols)
df_data.columns = pd.MultiIndex.from_tuples(
    [(a if not str(a).startswith("Unnamed") else prev, b)
     for (a,b), prev in zip(
         df_data.columns,
         pd.Series([c[0] for c in df_data.columns]).ffill()
     )]
)
df_data = df_data.loc[:, ~df_data.columns.get_level_values(0).str.startswith("Unnamed")]

freq = "Monthly" if "Month" in df_time.columns else "Quarterly"

# ======================
# SELECTORS
# ======================
with left:
    group = st.radio("🧭 Indicator group", sorted(df_data.columns.levels[0]))
    inds = sorted(c[1] for c in df_data.columns if c[0]==group)
    selected = st.multiselect("📌 Indicators", inds, inds[:1])
    st.info(f"Frequency: {freq}")

# ======================
# SERIES BUILD
# ======================
series = pd.concat(
    [df_time] + [df_data[(group,i)] for i in selected],
    axis=1
).dropna(how="all")

series["time"] = (
    series["Year"].astype(str) + (
        "-" + series["Month"].astype(int).astype(str).str.zfill(2)
        if freq=="Monthly" else "-Q"+series["Quarter"].astype(str)
    )
)

plot = series.set_index("time")[selected]

# ======================
# MAIN CHART
# ======================
with right:
    st.subheader("📈 Main chart")
    st.line_chart(plot)

# ======================
# KPI
# ======================
with right:
    cols = st.columns(len(selected))
    for c,i in zip(cols, selected):
        v = plot[i].dropna()
        c.metric(i, f"{v.iloc[-1]:.2f}" if not v.empty else "n/a")

# ======================
# BUSINESS CYCLE
# ======================
with right:
    cycle = plot.mean(axis=1).reset_index()
    cycle["date"] = pd.to_datetime(
        cycle["time"].str.replace("-Q","-"),
        errors="coerce"
    )

    chart = alt.Chart(cycle).mark_area(opacity=0.3).encode(
        x="date:T", y="0:Q",
        color=alt.condition("datum['0']>=0", alt.value("green"), alt.value("red"))
    )
    st.altair_chart(chart, use_container_width=True)

# ======================
# CONTRIBUTION
# ======================
with right:
    last = plot.dropna(how="all").iloc[-1]
    wf = pd.DataFrame({"Indicator":last.index,"Value":last.values})
    st.altair_chart(
        alt.Chart(wf).mark_bar().encode(x="Indicator",y="Value"),
        use_container_width=True
    )

# ======================
# RAW
# ======================
with right:
    with st.expander("📄 Raw data"):
        st.dataframe(series, use_container_width=True)
