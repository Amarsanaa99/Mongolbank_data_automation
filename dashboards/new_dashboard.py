import streamlit as st
import pandas as pd
from pathlib import Path

# ======================
# PAGE
# ======================
st.set_page_config(
    page_title="Macro Policy Dashboard",
    layout="wide"
)
st.title("🏦 Macro Policy Dashboard")

BASE_DIR = Path(__file__).resolve().parents[1]
EXCEL_PATH = BASE_DIR / "Dashboard_cleaned_data.xlsx"

# ======================
# LOAD DATA
# ======================
@st.cache_data
def load_sheet(sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(EXCEL_PATH, sheet_name=sheet_name)

# ======================
# DATASET SELECT
# ======================
sheets = pd.ExcelFile(EXCEL_PATH).sheet_names
sheets = [s for s in sheets if s.lower() in ["month", "quarter"]]

left, right = st.columns([1.3, 4.7])

with left:
    dataset = st.radio("📦 Dataset", sheets, horizontal=True)

df = load_sheet(dataset)

# ======================
# TIME COLUMNS (STRICT & SIMPLE)
# ======================
time_cols = ["Year"]
freq = None

if "Month" in df.columns:
    time_cols.append("Month")
    freq = "Monthly"
elif "Quarter" in df.columns:
    time_cols.append("Quarter")
    freq = "Quarterly"
else:
    st.error("❌ Month / Quarter column not found")
    st.stop()

df_time = df[time_cols].copy()
df_time = df_time.dropna(subset=["Year"])

# ======================
# INDICATOR COLUMNS
# ======================
value_cols = [c for c in df.columns if c not in time_cols]

with left:
    indicator = st.selectbox(
        "📊 Indicator",
        value_cols
    )
    st.info(f"Frequency: {freq}")

# ======================
# BUILD TIME INDEX
# ======================
series = pd.concat(
    [df_time, df[indicator]],
    axis=1
).dropna(subset=[indicator])

if freq == "Monthly":
    series["time"] = (
        series["Year"].astype(int).astype(str)
        + "-"
        + series["Month"].astype(int).astype(str).str.zfill(2)
    )
else:
    series["time"] = (
        series["Year"].astype(int).astype(str)
        + "-Q"
        + series["Quarter"].astype(int).astype(str)
    )

plot = (
    series
    .set_index("time")[indicator]
    .sort_index()
)

# ======================
# MAIN CHART
# ======================
with right:
    st.subheader(f"📈 {indicator}")
    st.line_chart(plot)

# ======================
# RAW DATA
# ======================
with right:
    with st.expander("📄 Raw data"):
        st.dataframe(series, use_container_width=True)
