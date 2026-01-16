import streamlit as st
import pandas as pd

# =====================================================
# CONFIG
# =====================================================
EXCEL_PATH = "20251218_Result.xlsx"

st.set_page_config(
    page_title="Macro Dashboard",
    layout="wide"
)

st.title("📊 Macro Economic Dashboard")

# =====================================================
# LOAD EXCEL
# =====================================================
@st.cache_data
def load_excel():
    return pd.ExcelFile(EXCEL_PATH)

xls = load_excel()

# =====================================================
# SIDEBAR – DATASET (SHEET)
# =====================================================
st.sidebar.header("📂 Dataset")

dataset = st.sidebar.selectbox(
    "Select dataset",
    options=xls.sheet_names
)

# =====================================================
# READ SHEET WITH MULTIHEADER
# =====================================================
@st.cache_data
def read_sheet(sheet_name):
    df = pd.read_excel(
        EXCEL_PATH,
        sheet_name=sheet_name,
        header=[0, 1]  # GDP type / Indicator
    )
    return df

df_raw = read_sheet(dataset)

# =====================================================
# IDENTIFY TIME COLUMNS
# =====================================================
time_cols = []
for col in df_raw.columns:
    if "Year" in str(col[0]) or col[0] == "":
        time_cols.append(col)

df_time = df_raw[time_cols]
df_data = df_raw.drop(columns=time_cols)

# Clean column names
df_data.columns = pd.MultiIndex.from_tuples([
    (str(c[0]).strip(), str(c[1]).strip()) for c in df_data.columns
])

# =====================================================
# SIDEBAR – GDP TYPE
# =====================================================
st.sidebar.header("📐 GDP Type")

gdp_types = sorted(set([c[0] for c in df_data.columns]))

gdp_type = st.sidebar.selectbox(
    "Select GDP type",
    gdp_types
)

# =====================================================
# SIDEBAR – INDICATOR
# =====================================================
indicators = sorted([
    c[1] for c in df_data.columns if c[0] == gdp_type
])

indicator = st.sidebar.selectbox(
    "Select indicator",
    indicators
)

# =====================================================
# FILTER DATA
# =====================================================
series = df_data[(gdp_type, indicator)]

df_plot = pd.concat([df_time, series], axis=1)
df_plot.columns = ["Year", "Period", "Value"]

df_plot = df_plot.dropna(subset=["Value"])

# =====================================================
# AUTO START DATE (NO FORCED RANGE)
# =====================================================
df_plot = df_plot.loc[df_plot["Value"].first_valid_index():]

# =====================================================
# MAIN VIEW
# =====================================================
st.subheader(f"{gdp_type} – {indicator}")

st.line_chart(
    df_plot.set_index(df_plot.index)["Value"]
)

# =====================================================
# RAW DATA (OPTIONAL)
# =====================================================
with st.expander("📄 Raw data"):
    st.dataframe(df_plot)

