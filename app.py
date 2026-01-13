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
# DATASET SELECTOR
st.markdown("## 📦 Dataset")

dataset_box = st.container(border=True)
with dataset_box:
    dataset = st.radio(
        "",
        ["GDP", "Population"],
        horizontal=True
    )

topic = dataset.lower()


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

# =====================================================
# MAIN GRID
# =====================================================
left_col, right_col = st.columns(
    [1.2, 3.8],
    gap="large"
)
with left_col:

    # ---------------- TIME RANGE ----------------
    st.markdown("### ⏱ Time range")

    time_box = st.container(border=True)
    with time_box:
        if topic == "gdp":
            start_q, end_q = st.slider(
                "Quarterly period",
                min_value=float(df["year_num"].min()),
                max_value=float(df["year_num"].max()),
                value=(
                    float(df["year_num"].min()),
                    float(df["year_num"].max())
                ),
                step=0.25
            )
        else:
            start_y, end_y = st.slider(
                "Yearly period",
                min_value=int(df["year_num"].min()),
                max_value=int(df["year_num"].max()),
                value=(
                    int(df["year_num"].min()),
                    int(df["year_num"].max())
                )
            )

    # ---------------- FILTERS ----------------
    st.markdown("### 🔎 Filters")

    filter_box = st.container(border=True)
    with filter_box:
        if topic == "gdp":
            selected_indicator = st.selectbox(
                "Indicator",
                sorted(df["indicator_code"].dropna().unique())
            )

            filtered_df = df[
                df["indicator_code"] == selected_indicator
            ]
        else:
            sex = st.selectbox(
                "Sex",
                sorted(df["sex"].dropna().unique())
            )

            age_group = st.selectbox(
                "Age group",
                sorted(df["age_group"].dropna().unique())
            )

            filtered_df = df[
                (df["sex"] == sex) &
                (df["age_group"] == age_group)
            ]

with right_col:

    # ---------------- TIME FILTER APPLY ----------------
    if topic == "gdp":
        time_filtered_df = filtered_df[
            (filtered_df["year_num"] >= start_q) &
            (filtered_df["year_num"] <= end_q)
        ]
        st.subheader(f"📈 {selected_indicator}")
    else:
        time_filtered_df = filtered_df[
            (filtered_df["year_num"] >= start_y) &
            (filtered_df["year_num"] <= end_y)
        ]
        st.subheader(f"📈 Population — {sex}, {age_group}")

    if time_filtered_df.empty:
        st.warning("⚠️ No data in selected range")
    else:
        st.line_chart(
            time_filtered_df
            .sort_values("year_num")
            .set_index("year_num")["value"]
        )

# =====================================================
# RAW DATA Preview
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

