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
st.title("🏦 Mongolbank Macro Dashboard")
st.caption("Quarterly GDP indicators (2000–2025)")
st.success("🔥 APP STARTED — UI rendering OK")

# =====================================================
# SIDEBAR — DATASET SELECTOR (⚠️ ХАМГИЙН ЧУХАЛ)
# =====================================================
st.sidebar.markdown("## 📊 Dataset")

dataset = st.sidebar.radio(
    label="",
    options=["GDP", "Population"],
    horizontal=True,
    key="dataset_selector"
)

topic = dataset.lower()# gdp / population


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
            value,
            sex,
            age_group
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
if topic == "gdp":
    df["year_num"] = (
        df["year"].str.split("-").str[0].astype(int)
        + (df["year"].str.split("-").str[1].astype(int) - 1) / 4
    )
else:
    df["year_num"] = df["year"].astype(int)

st.sidebar.markdown("---")

if topic == "gdp":
    st.sidebar.markdown("### 📈 GDP Filters")
elif topic == "population":
    st.sidebar.markdown("### 👥 Population Filters")

# =====================================================
# SIDEBAR FILTER (CONTEXT-AWARE)
# =====================================================


# ===================== GDP =====================
if topic == "gdp":
    indicator_list = sorted(
        df["indicator_code"].dropna().unique()
    )

    selected_indicator = st.sidebar.selectbox(
        "Select indicator",
        indicator_list
    )

    filtered_df = df[
        df["indicator_code"] == selected_indicator
    ]

# ===================== POPULATION =====================
elif topic == "population":
    sex = st.sidebar.selectbox(
        "Select sex",
        sorted(df["sex"].unique())
    )

    age_group = st.sidebar.selectbox(
        "Select age group",
        sorted(df["age_group"].unique())
    )

    filtered_df = df[
        (df["sex"] == sex) &
        (df["age_group"] == age_group)
    ]

# ===================== FALLBACK =====================
else:
    filtered_df = df

# =====================================================
# MAIN CHART
# =====================================================
if topic == "gdp":
    st.subheader(f"📈 Indicator: {selected_indicator}")
else:
    st.subheader(
        f"👥 Population trend — {sex} · Age {age_group}"
    )


if filtered_df.empty:
    st.warning("⚠️ Сонгосон indicator-д өгөгдөл алга")
else:
    st.line_chart(
        filtered_df.set_index("year_num")["value"]
    )

# =====================================================
# DATA PREVIEW (PIVOT)
# =====================================================
with st.expander("📄 Raw data"):

    # ===================== GDP =====================
    if topic == "gdp":
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

        existing_cols = [c for c in GDP_ORDER if c in df_pivot.columns]
        df_pivot = df_pivot.reindex(columns=["year"] + existing_cols)

        st.dataframe(df_pivot, use_container_width=True)

    # ===================== POPULATION =====================
    else:
        df_pop = (
            df
            .sort_values("year")
            [["year", "sex", "age_group", "value"]]
        )

        st.dataframe(df_pop, use_container_width=True)

