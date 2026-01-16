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
# LOAD + CLEAN DATA
# ======================
df = read_sheet(dataset)

# ======================
# FIX HEADER (CRITICAL)
# ======================
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [
        c[0] if c[0] in ["Year", "Month", "Quarter"] else c
        for c in df.columns
    ]

# --- БАГАНЫГ ХУВААХ (TIME vs DATA) ---
time_cols = []
for col in df.columns:
    if isinstance(col, str) and col in ["Year", "Month", "Quarter"]:
        time_cols.append(col)
    elif isinstance(col, tuple) and col[0] in ["Year", "Month", "Quarter"]:
        time_cols.append(col)

if not time_cols:
    st.error("❌ No time columns found")
    st.stop()

df_time = df[time_cols].copy()
df_data = df.drop(columns=time_cols)

freq = "Monthly" if "Month" in df_time.columns else "Quarterly"

# --- ensure Year exists safely
if "Year" not in df_time.columns:
    st.error("❌ 'Year' column not detected in this sheet")
    st.stop()

df_time = df_time.dropna(subset=["Year"], how="all")

# ======================
# FIX MULTIINDEX HEADERS (FINAL - SAFE)
# ======================
if isinstance(df_data.columns, pd.MultiIndex):
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
else:
    # Хэрэв MultiIndex биш бол дараах зүйлсийг хийх
    df_data.columns = pd.MultiIndex.from_product([["Data"], df_data.columns])

# ======================
# SELECTORS
# ======================
with left:
    group = st.radio("🧭 Indicator group", sorted(df_data.columns.levels[0]))
    inds = sorted(c[1] for c in df_data.columns if c[0]==group)
    selected = st.multiselect("📌 Indicators", inds, inds[:1] if inds else [])
    st.info(f"Frequency: {freq}")

# ======================
# ROBUST TIME BUILDER
# ======================
if not selected:
    st.warning("⚠️ No indicators selected")
    st.stop()

# Өгөгдлийг цуваа болгон нэгтгэх
series = df_time.reset_index(drop=True).copy()

for i in selected:
    if (group, i) in df_data.columns:
        series[i] = df_data[(group, i)].reset_index(drop=True).values
    else:
        st.warning(f"Indicator '{i}' not found in group '{group}'")

# ======================
# TIME COLUMN БҮТЭЭХ (SAFE)
# ======================
if "Year" in series.columns:
    series = series.dropna(subset=["Year"], how="all")
    
    # Year баганыг бүхэл тоо болгох
    series["Year"] = pd.to_numeric(series["Year"], errors="coerce").fillna(0).astype(int)
    
    if "Month" in series.columns:
        series = series.dropna(subset=["Month"], how="all")
        series["Month"] = pd.to_numeric(series["Month"], errors="coerce").fillna(1).astype(int)
        series["time"] = (
            series["Year"].astype(str)
            + "-"
            + series["Month"].astype(str).str.zfill(2)
        )
    
    elif "Quarter" in series.columns:
        series = series.dropna(subset=["Quarter"], how="all")
        series["Quarter"] = pd.to_numeric(series["Quarter"], errors="coerce").fillna(1).astype(int)
        series["time"] = (
            series["Year"].astype(str)
            + "-Q"
            + series["Quarter"].astype(str)
        )
    
    else:
        # Зөвхөн Year байвал
        series["time"] = series["Year"].astype(str)

else:
    st.error("❌ 'Year' column missing in series")
    st.stop()

# ======================
# МЭДЭЭЛЭЛ АНГИЛАХ
# ======================
# Time баганыг index болгох
try:
    plot_data = series.set_index("time")[selected].sort_index()
    
    # Тэмдэглэгээг хүснэгтэнд харуулах
    plot_data.index.name = "Time"
    
except KeyError as e:
    st.error(f"❌ Error selecting data: {e}")
    st.stop()

# ======================
# MAIN CHART
# ======================
with right:
    st.subheader("📈 Main chart")
    
    if not plot_data.empty:
        st.line_chart(plot_data)
    else:
        st.warning("No data to display")

# ======================
# RAW DATA
# ======================
with right:
    with st.expander("📄 Raw data"):
        if not series.empty:
            # Time баганыг дахин харуулах
            display_df = series.copy()
            if "time" in display_df.columns:
                display_df = display_df.set_index("time")
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No data available")
