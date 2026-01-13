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
# MAIN LAYOUT
# =====================================================
left_col, right_col = st.columns([1.4, 4.6], gap="large")

# ================= LEFT COLUMN =================
with left_col:

    # ---------- DATASET ----------
    st.markdown("### 📦 Dataset")
    dataset_box = st.container(border=True)
    with dataset_box:
        dataset = st.radio(
            "",
            ["GDP", "Population"],
            horizontal=True
        )

    topic = dataset.lower()

    # ---------- LOAD DATA (ЗӨВ ГАЗАР) ----------
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
        df = load_data(topic)

    if topic == "gdp":
        df["year_num"] = (
            df["year"].str.split("-").str[0].astype(int)
            + (df["year"].str.split("-").str[1].astype(int) - 1) / 4
        )
    else:
        df["year_num"] = df["year"].astype(int)

    # ---------- TIME RANGE ----------
    st.markdown("### ⏱ Time range")
    time_box = st.container(border=True)
    with time_box:
        if topic == "gdp":
            start_y, end_y = st.slider(
                "Quarter range",
                float(df["year_num"].min()),
                float(df["year_num"].max()),
                (float(df["year_num"].min()), float(df["year_num"].max())),
                step=0.25
            )
        else:
            start_y, end_y = st.slider(
                "Year range",
                int(df["year_num"].min()),
                int(df["year_num"].max()),
                (int(df["year_num"].min()), int(df["year_num"].max()))
            )

    # ---------- FILTERS ----------
    st.markdown("### 🔎 Filters")
    filter_box = st.container(border=True)
    with filter_box:
        if topic == "gdp":
            selected_indicators = st.multiselect(
                "Indicators",
                sorted(df["indicator_code"].dropna().unique()),
                default=["ngdp"]
            )
            filtered_df = df[df["indicator_code"].isin(selected_indicators)]
        else:
            sex = st.selectbox("Sex", sorted(df["sex"].dropna().unique()))
            age_group = st.selectbox("Age group", sorted(df["age_group"].dropna().unique()))
            filtered_df = df[
                (df["sex"] == sex) &
                (df["age_group"] == age_group)
            ]

# ================= RIGHT COLUMN =================
with right_col:

    st.subheader("📈 Main chart")

    time_filtered_df = filtered_df[
        (filtered_df["year_num"] >= start_y) &
        (filtered_df["year_num"] <= end_y)
    ]

    if time_filtered_df.empty:
        st.warning("No data")
    else:
        if topic == "gdp":
            chart_df = time_filtered_df.pivot(
                index="year_num",
                columns="indicator_code",
                values="value"
            )
            st.line_chart(chart_df.sort_index())
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

