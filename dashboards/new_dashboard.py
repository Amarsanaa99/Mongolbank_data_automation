import streamlit as st
import pandas as pd
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
    """Excel файлыг хоёр түвшний header-ээр уншина"""
    return pd.read_excel(EXCEL_PATH, sheet_name=sheet, header=[0, 1])

# ======================
# DATASET SELECT
# ======================
sheets = [s for s in pd.ExcelFile(EXCEL_PATH).sheet_names
          if s.lower() in ["month", "quarter"]]

left, right = st.columns([1.4, 4.6], gap="large")

with left:
    dataset = st.radio("📦 Dataset", sheets, horizontal=True)

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

# ======================
# FREQUENCY тодорхойлох
# ======================
freq = "Monthly" if "Month" in df_time.columns else "Quarterly"

# ======================
# SELECTORS
# ======================
with left:
    # Боломжит бүлгүүдийг харуулах
    available_groups = sorted(df_data.columns.get_level_values(0).unique())
    if not available_groups:
        st.error("❌ No indicator groups found")
        st.stop()
    
    group = st.radio("🧭 Indicator group", available_groups)
    
    # Сонгосон бүлгийн үзүүлэлтүүд
    indicators = sorted([
        col[1] for col in df_data.columns 
        if col[0] == group and not pd.isna(col[1])
    ])
    
    if not indicators:
        st.error(f"❌ No indicators found in group '{group}'")
        st.stop()
    
    selected = st.multiselect(
        "📌 Indicators", 
        indicators, 
        default=[indicators[0]] if indicators else []
    )
    
    st.info(f"Frequency: {freq}")

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
plot_data = series.set_index("time")[selected].sort_index()

# 🔍 Safety check
plot_data = plot_data.dropna(how="all")


# ======================
# MAIN CHART
# ======================
with right:
    st.subheader("📈 Main chart")

    # ===== 3️⃣ CHART SAFETY CHECK =====
    if plot_data is None or plot_data.empty:
        st.warning("⚠️ Plot data is empty or invalid")
        st.write("plot_data columns:", None if plot_data is None else plot_data.columns.tolist())
        st.write("Requested indicators:", selected)
        st.stop()

    missing = [c for c in selected if c not in plot_data.columns]
    if missing:
        st.error(f"❌ Missing columns in plot_data: {missing}")
        st.write("plot_data columns:", plot_data.columns.tolist())
        st.stop()

    # ===== SAFE CHART =====
    st.line_chart(plot_data)

    if len(selected) > 1:
        st.caption("📊 Multiple indicators shown - check scale differences")


# ======================
# RAW DATA
# ======================
with right:
    with st.expander("📄 Raw data"):
        if not series.empty:
            # Цэвэр харагдацтай хүснэгт
            display_cols = ["time"] + selected
            if all(col in series.columns for col in display_cols):
                display_df = series[display_cols].copy()
                display_df = display_df.set_index("time")
                st.dataframe(display_df, use_container_width=True)
            else:
                st.dataframe(series, use_container_width=True)
        else:
            st.info("No data available")

# ======================
# DEBUG INFO (Optional)
# ======================
with st.expander("🔍 Debug Info (for development)"):
    st.write("**Time columns:**", list(df_time.columns))
    st.write("**Data columns shape:**", df_data.shape)
    st.write("**Data column groups:**", available_groups)
    st.write("**Selected group indicators:**", indicators)
