import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# =====================================================
# PAGE CONFIG (⚠️ ЗААВАЛ ЭХНИЙ МӨРҮҮДИЙН НЭГ БАЙНА)
# =====================================================
st.set_page_config(
    page_title="Mongolbank Macro Dashboard",
    layout="wide"
)

# =====================================================
# APP START (TEST RENDER)
# =====================================================
st.title("📊 Mongolbank Macro Dashboard")
st.caption("Quarterly GDP indicators (2000–2025)")
st.success("🔥 APP STARTED — UI rendering OK")

# =====================================================
# SIDEBAR — DATASET SELECTOR (⚠️ ХАМГИЙН ЧУХАЛ)
# =====================================================
st.sidebar.header("📂 Dataset")

dataset = st.sidebar.selectbox(
    "Select dataset",
    ["GDP", "Population"]
)

topic = dataset.lower()  # gdp / population


# =====================================================
# BIGQUERY LOAD
# =====================================================
@st.cache_data(ttl=3600)
def load_data(topic):
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )

    client = bigquery.Client(
        credentials=credentials,
        project=st.secrets["gcp_service_account"]["project_id"]
    )

    query = f"""
        SELECT
            year,
            indicator_code,
            value
        FROM `mongol-bank-macro-data.Automation_data.fact_macro`
        WHERE topic = '{topic}'
        ORDER BY year
    """

    return client.query(query).to_dataframe()


with st.spinner("⏳ Loading data from BigQuery..."):
    df = load_data(topic)   # ⚠️ ЭНД topic дамжуулна


# =====================================================
# DATA VALIDATION (⚠️ МАШ ЧУХАЛ)
# =====================================================
if df.empty:
    st.error("❌ BigQuery-ээс өгөгдөл ирсэнгүй")
    st.stop()

st.info(f"✅ Loaded rows: {len(df):,}")

# =====================================================
# PREP DATA
# =====================================================
# "2000-1" → 2000.00, "2000-2" → 2000.25
df["year_num"] = (
    df["year"].str.split("-").str[0].astype(int)
    + (df["year"].str.split("-").str[1].astype(int) - 1) / 4
)
st.sidebar.header("📂 Dataset")

dataset = st.sidebar.selectbox(
    "Select dataset",
    ["GDP", "Population"]
)

topic = dataset.lower()  # gdp / population

# =====================================================
# SIDEBAR FILTER
# =====================================================
st.sidebar.header("🔎 Filters")

indicator_list = sorted(df["indicator_code"].unique())

selected_indicator = st.sidebar.selectbox(
    "Select indicator",
    indicator_list
)

filtered_df = df[df["indicator_code"] == selected_indicator]

# =====================================================
# MAIN CHART
# =====================================================
st.subheader(f"📈 Indicator: {selected_indicator}")

if filtered_df.empty:
    st.warning("⚠️ Сонгосон indicator-д өгөгдөл алга")
else:
    st.line_chart(
        filtered_df.set_index("year_num")["value"]
    )

# =====================================================
# DATA PREVIEW (PIVOT)
# =====================================================
with st.expander("📄 Raw data (Pivot – Excel шиг)"):

    df_pivot = (
        df
        .pivot_table(
            index="year",
            columns="indicator_code",
            values="value",
            aggfunc="sum"
        )
        .reset_index()
    )

    GDP_ORDER = [
        "ngdp",
        "ngdp_agri",
        "ngdp_mine",
        "ngdp_manu",
        "ngdp_elec",
        "ngdp_cons",
        "ngdp_trad",
        "ngdp_tran",
        "ngdp_info",
        "ngdp_oser",
        "ngdp_taxe"
    ]

    POP_ORDER = ["population"]

    if topic == "gdp":
        col_order = GDP_ORDER
    elif topic == "population":
        col_order = POP_ORDER
    else:
        col_order = []

    existing_cols = [c for c in col_order if c in df_pivot.columns]

    df_pivot = df_pivot.reindex(
        columns=["year"] + existing_cols
    )

    st.dataframe(
        df_pivot,
        use_container_width=True
    )

