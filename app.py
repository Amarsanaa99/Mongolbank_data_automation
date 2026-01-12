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
st.caption("Quarterly GDP indicators (2000–2025)")

# -------------------------
# BIGQUERY CONNECTION
# -------------------------
@st.cache_data(ttl=3600)
def load_data():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )

    client = bigquery.Client(
        credentials=credentials,
        project=st.secrets["gcp_service_account"]["project_id"]
    )

    query = """
    SELECT
        year,
        indicator_code,
        value
    FROM `mongol-bank-macro-data.Automation_data.fact_macro`
    ORDER BY year
    """

    return client.query(query).to_dataframe()

df = load_data()

# -------------------------
# PREP DATA
# -------------------------
# year = "2000-1" → numeric index for plotting
df["year_num"] = (
    df["year"].str.split("-").str[0].astype(int)
    + (df["year"].str.split("-").str[1].astype(int) - 1) / 4
)

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.header("🔎 Filters")

indicator_list = sorted(df["indicator_code"].unique())

selected_indicator = st.sidebar.selectbox(
    "Select indicator",
    indicator_list
)

filtered_df = df[df["indicator_code"] == selected_indicator]

# -------------------------
# MAIN CHART
# -------------------------
st.subheader(f"📈 Indicator: {selected_indicator}")

st.line_chart(
    filtered_df.set_index("year_num")["value"]
)

# -------------------------
# DATA PREVIEW
# -------------------------
with st.expander("📄 Raw data"):
    st.dataframe(
        filtered_df[["year", "indicator_code", "value"]],
        use_container_width=True
    )
