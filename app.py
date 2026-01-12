import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Mongolbank Macro Dashboard",
    layout="wide"
)

st.title("📊 Mongolbank Macro Dashboard")

# -------------------------
# BIGQUERY CONNECTION
# -------------------------
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

@st.cache_data(ttl=3600)
def load_data():
    client = bigquery.Client(
        credentials=credentials,
        project=st.secrets["gcp_service_account"]["project_id"]
    )

    query = """
    SELECT
        CAST(year AS INT64) AS year,
        indicator_code,
        value
    FROM `mongol-bank-macro-data.Automation_data.fact_macro`
    ORDER BY year
    """


    df = client.query(query).to_dataframe()
    return df


df = load_data()

# -------------------------
# SIDEBAR FILTERS
# -------------------------
st.sidebar.header("🔎 Filters")

indicator_list = sorted(df["indicator_code"].unique())
selected_indicator = st.sidebar.selectbox(
    "Select indicator",
    indicator_list
)

filtered_df = df[df["indicator_code"] == selected_indicator].copy()

# -------------------------
# MAIN CHART
# -------------------------
st.subheader(f"📈 Indicator: {selected_indicator}")

st.line_chart(
    filtered_df.set_index("year")["value"]
)

# -------------------------
# DATA PREVIEW
# -------------------------
with st.expander("📄 Raw data"):
    st.dataframe(filtered_df)
