import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import json
import os
import plotly.express as px

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Mongolia Macro Dashboard",
    layout="wide"
)

st.title("📊 Mongolia Macroeconomic Dashboard")
st.caption("Source: NSO / Mongolbank API")

# -------------------------------------------------
# AUTH (Streamlit Secrets)
# -------------------------------------------------
credentials_info = json.loads(st.secrets["gcp_service_account"])

credentials = service_account.Credentials.from_service_account_info(
    credentials_info
)

client = bigquery.Client(
    credentials=credentials,
    project=credentials.project_id
)

# -------------------------------------------------
# LOAD DATA FROM BIGQUERY
# -------------------------------------------------
@st.cache_data(ttl=3600)
def load_data():
    query = """
        SELECT
            year,
            indicator_code,
            value
        FROM `mongol-bank-macro-data.Automation_data.fact_macro`
        WHERE indicator_code IN ('ngdp', 'rgdp_2015', 'growth')
    """
    return client.query(query).to_dataframe()

df = load_data()

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------
st.sidebar.header("🔎 Filters")

indicator = st.sidebar.selectbox(
    "Indicator",
    options=df["indicator_code"].unique()
)

years = sorted(df["year"].unique())
selected_years = st.sidebar.multiselect(
    "Year / Quarter",
    years,
    default=years[-8:]
)

filtered = df[
    (df["indicator_code"] == indicator) &
    (df["year"].isin(selected_years))
]

# -------------------------------------------------
# KPI
# -------------------------------------------------
latest = filtered.sort_values("year").iloc[-1]

col1, col2 = st.columns(2)
col1.metric("Indicator", indicator.upper())
col2.metric("Latest value", f"{latest['value']:,.2f}")

# -------------------------------------------------
# CHART
# -------------------------------------------------
fig = px.line(
    filtered,
    x="year",
    y="value",
    markers=True,
    title=f"{indicator.upper()} over time"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# DATA TABLE
# -------------------------------------------------
with st.expander("📄 View raw data"):
    st.dataframe(filtered, use_container_width=True)
