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
EXCEL_PATH = BASE_DIR / "Dashboard_cleaned_data.xlsx"

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
# LOAD + CLEAN DATA  (FIXED)
# ======================
df = read_sheet(dataset)

# --- detect time columns from LEVEL 1 (FIX)
time_cols = [c for c in df.columns if c[1] in ["Year", "Month", "Quarter"]]

df_time = df[time_cols]

# rename time columns properly
df_time.columns = [c[1] for c in time_cols]


# --- detect time columns from LEVEL 1 (FINAL)
time_cols = [c for c in df.columns if c[1] in ["Year", "Month", "Quarter"]]

df_time = df[time_cols].copy()
# normalize ONLY level=1 of MultiIndex
df_time.columns = (
    df_time.columns
    .get_level_values(1)
    .astype(str)
    .str.strip()
    .str.capitalize()
)


# --- ensure Year exists safely
if "Year" not in df_time.columns:
    st.error("❌ 'Year' column not detected in this sheet")
    st.stop()

df_time = df_time.dropna(subset=["Year"], how="all")

df_data = df.drop(columns=time_cols)
freq = "Monthly" if "Month" in df_time.columns else "Quarterly"
# ======================
# FIX MULTIINDEX HEADERS (FINAL - SAFE)
# ======================
lvl0 = pd.Series(df_data.columns.get_level_values(0))
lvl1 = pd.Series(df_data.columns.get_level_values(1))

# force string + clean Unnamed
lvl0 = (
    lvl0.astype(str)
        .where(~lvl0.astype(str).str.contains("Unnamed"), None)
        .ffill()
)

df_data.columns = pd.MultiIndex.from_arrays([lvl0, lvl1])

# SAFE drop unnamed groups
mask = (
    df_data.columns
           .get_level_values(0)
           .astype(str)
           .str.contains("Unnamed", na=False)
)

df_data = df_data.loc[:, ~mask]



# ======================
# SELECTORS
# ======================
with left:
    group = st.radio("🧭 Indicator group", sorted(df_data.columns.levels[0]))
    inds = sorted(c[1] for c in df_data.columns if c[0]==group)
    selected = st.multiselect("📌 Indicators", inds, inds[:1])
    st.info(f"Frequency: {freq}")

# ======================
# ROBUST TIME BUILDER
# ======================
series = pd.concat(
    [df_time.reset_index(drop=True)]
    + [
        df_data[(group, i)]
        .reset_index(drop=True)
        .rename(i)
        for i in selected
    ],
    axis=1
)


# ======================
# ROBUST TIME BUILDER (SAFE)
# ======================
if "Year" in series.columns:
    series = series.dropna(subset=["Year"], how="all")
else:
    st.error("❌ 'Year' column missing in series")
    st.stop()

if "Month" in series.columns:
    series = series.dropna(subset=["Month"], how="all")
    series["time"] = (
        series["Year"].astype(int).astype(str)
        + "-"
        + series["Month"].astype(int).astype(str).str.zfill(2)
    )

elif "Quarter" in series.columns:
    series = series.dropna(subset=["Quarter"], how="all")
    series["time"] = (
        series["Year"].astype(int).astype(str)
        + "-Q"
        + series["Quarter"].astype(int).astype(str)
    )

else:
    st.error("❌ Time columns not found (Month / Quarter)")
    st.stop()
plot = (
    series
    .set_index("time")[selected]
    .sort_index()
)


    
# ======================
# MAIN CHART
# ======================
with right:
    st.subheader("📈 Main chart")
    st.line_chart(plot)


# ======================
# RAW
# ======================
with right:
    with st.expander("📄 Raw data"):
        st.dataframe(series, use_container_width=True)
