import streamlit as st
import pandas as pd

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Macro Dashboard (Excel)",
    layout="wide"
)

st.title("📊 Macro Dashboard (Excel-based)")

EXCEL_PATH = "20251218_Result.xlsx"

# =====================================================
# LOAD EXCEL
# =====================================================
@st.cache_data
def load_excel():
    return pd.ExcelFile(EXCEL_PATH)

xls = load_excel()

# =====================================================
# MAIN LAYOUT
# =====================================================
left_col, right_col = st.columns([1.4, 4.6], gap="large")

# ================= LEFT COLUMN =================
with left_col:

    # ================= DATASET =================
    with st.container(border=True):
        st.markdown("### 📦 Dataset")
        dataset = st.radio(
            "",
            xls.sheet_names,
            horizontal=True
        )

    # ================= READ SHEET =================
    @st.cache_data
    def read_sheet(sheet):
        return pd.read_excel(
            EXCEL_PATH,
            sheet_name=sheet,
            header=[0, 1]
        )

    df_raw = read_sheet(dataset)

    # ================= TIME COLUMNS =================
    time_cols = [
        c for c in df_raw.columns
        if c[0] in ["Year", "Month", "Quarter", ""]
    ]

    df_time = df_raw[time_cols]
    df_data = df_raw.drop(columns=time_cols)

    df_data.columns = pd.MultiIndex.from_tuples(
        [(str(a).strip(), str(b).strip()) for a, b in df_data.columns]
    )

    # ================= GDP TYPE =================
    with st.container(border=True):
        st.markdown("### 📐 GDP type")
        gdp_types = sorted(df_data.columns.levels[0])
        gdp_type = st.radio("", gdp_types)

    # ================= INDICATORS =================
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

    # ================= FREQUENCY =================
    with st.container(border=True):
        st.markdown("### ⏱ Frequency")

        freq = "Monthly" if dataset.lower().startswith("month") else "Quarterly"
        st.info(f"Frequency: {freq}")

# ================= PREPARE DATA =================
series_df = pd.concat(
    [
        df_time,
        df_data[(gdp_type, ind)]
        for ind in selected_indicators
    ],
    axis=1
)

series_df = series_df.dropna(how="all")

# ================= CREATE TIME LABEL =================
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

# ================= RIGHT COLUMN =================
with right_col:

    with st.container(border=True):
        st.markdown("### 📈 Main chart")

        if series_df.empty:
            st.warning("No data available")
        else:
            plot_df = (
                series_df
                .set_index("time_label")[selected_indicators]
            )
            st.line_chart(plot_df)

    # ================= RAW DATA =================
    with st.expander("📄 Raw data"):
        st.dataframe(series_df, use_container_width=True)
