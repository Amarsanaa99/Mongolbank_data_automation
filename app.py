import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import altair as alt

chart = (
    alt.Chart(plot_df)
    .mark_line()
    .encode(
        x=alt.X("year_num:Q", title="Year"),
        y=alt.Y("value:Q", title="Population"),
        color=alt.Color(
            "Series:N",
            legend=alt.Legend(orient="right")
        ),
        tooltip=["year", "sex", "age_group", "value"]
    )
    .properties(height=400)
)

st.altair_chart(chart, use_container_width=True)


# =====================================================
# PAGE CONFIG (⚠️ ЗААВАЛ ЭХНИЙ МӨРҮҮДИЙН НЭГ БАЙНА)
# =====================================================
st.set_page_config(
    page_title="Mongolbank Macro Data Dashboard",
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

    # ================= DATASET CARD =================
    with st.container(border=True):
        st.markdown("### 📦 Dataset")

        dataset = st.radio(
            "",
            ["GDP", "Population"],
            horizontal=True
        )

        # 1️⃣ topic ЭХЭЛЖ тодорхойлогдоно
        topic = dataset.lower()

    # 2️⃣ load_data FUNCTION (дуудахаас ӨМНӨ)
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

    # 3️⃣ DATA LOAD
    with st.spinner("⏳ Loading data from BigQuery..."):
        df = load_data(topic)

    # 4️⃣ PREP DATA (year → year_num)
    if topic == "gdp":
        df["year_num"] = (
            df["year"].str.split("-").str[0].astype(int)
            + (df["year"].str.split("-").str[1].astype(int) - 1) / 4
        )
    else:
        df["year_num"] = df["year"].astype(int)
    # ---------- GDP TYPE SELECTOR ----------
    if topic == "gdp":
        with st.container(border=True):
            st.markdown("### 📊 GDP type")
    
            gdp_type = st.radio(
                "",
                ["RGDP2005", "RGDP2010", "RGDP2015", "NGDP", "GROWTH"],
                horizontal=True
            )
    if topic == "gdp":
        prefix_map = {
            "RGDP2005": "rgdp_2005",
            "RGDP2010": "rgdp_2010",
            "RGDP2015": "rgdp_2015",
            "NGDP": "ngdp",
            "GROWTH": "growth"
        }

        prefix = prefix_map[gdp_type]
    
        available_indicators = sorted(
            df.loc[
                df["indicator_code"].str.contains(prefix, case=False, na=False),
                "indicator_code"
            ].unique()
        )


        selected_indicators = st.multiselect(
            "Indicators",
            available_indicators,
            default=available_indicators[:1] if available_indicators else []
        )


        filtered_df = df[df["indicator_code"].isin(selected_indicators)]
    else:
        sex = st.multiselect(
            "Sex",
            sorted(df["sex"].dropna().unique()),
            default=sorted(df["sex"].dropna().unique())
        )
        
        age_group = st.multiselect(
            "Age group",
            sorted(df["age_group"].dropna().unique()),
            default=sorted(df["age_group"].dropna().unique())
        )
        
        filtered_df = df[
            df["sex"].isin(sex) &
            df["age_group"].isin(age_group)
        ]
     # ---------- TIME RANGE ----------
    with st.container(border=True):
        st.markdown("### ⏱ Time range")
        
        if topic == "gdp":
            quarters = sorted(df["year"].unique())
            col1, col2 = st.columns(2)
            with col1:
                start_q = st.selectbox("Start quarter", quarters, index=0)
            with col2:
                end_q = st.selectbox("End quarter", quarters, index=len(quarters)-1)
        else:
            start_y, end_y = st.slider(
                "Year range",
                int(df["year"].min()),
                int(df["year"].max()),
                (int(df["year"].min()), int(df["year"].max()))
            )

    # ---------- ⬅️ TIME FILTER ----------
    if topic == "gdp":
        time_filtered_df = filtered_df[
            (filtered_df["year"] >= start_q) &
            (filtered_df["year"] <= end_q)
        ]
    else:
        time_filtered_df = filtered_df[
            (filtered_df["year_num"] >= start_y) &
            (filtered_df["year_num"] <= end_y)
        ]
    # ---------- SERIES COLUMN (POPULATION) ----------
    if topic == "population":
        time_filtered_df["Series"] = (
            time_filtered_df["sex"].astype(str)
            + " | "
            + time_filtered_df["age_group"].astype(str)
        )


    
# ================= RIGHT COLUMN =================
with right_col:
    with st.container(border=True):
        st.markdown("### 📈 Main chart")

        if time_filtered_df.empty:
            st.warning("No data for selected filters")
        else:
            if topic == "gdp":
                chart_df = (
                    time_filtered_df
                    .pivot_table(
                        index="year_num",
                        columns="indicator_code",
                        values="value",
                        aggfunc="sum"
                    )
                    .sort_index()
                )
                st.line_chart(chart_df)
        else:
            # ---------- POPULATION MULTI-LINE CHART ----------
            plot_df = time_filtered_df.copy()
            plot_df["Series"] = plot_df["sex"] + " | " + plot_df["age_group"]
        
            chart = (
                alt.Chart(plot_df)
                .mark_line()
                .encode(
                    x=alt.X("year_num:Q", title="Year"),
                    y=alt.Y("value:Q", title="Population"),
                    color=alt.Color(
                        "Series:N",
                        legend=alt.Legend(orient="right")
                    ),
                    tooltip=["year", "sex", "age_group", "value"]
                )
                .properties(height=400)
            )
        
            st.altair_chart(chart, use_container_width=True)



# =====================================================
# RAW DATA Preview
# =====================================================
with st.expander("📄 Raw data"):

    # ===================== GDP =====================
    if topic == "gdp":
    
        df_pivot = (
            time_filtered_df
            .pivot_table(
                index="year",
                columns="indicator_code",
                values="value",
                aggfunc="sum"
            )
            .reset_index()
        )
    
        # 🔑 GDP TYPE-д таарсан prefix
        raw_prefix = prefix_map[gdp_type]
    
        ordered_cols = (
            ["year"] +
            sorted([c for c in df_pivot.columns if c.startswith(raw_prefix)])
        )
    
        df_pivot = df_pivot[ordered_cols]
    
        st.dataframe(df_pivot, use_container_width=True)


    # ===================== POPULATION =====================
    else:
        df_pop = time_filtered_df.sort_values("year")[["year", "sex", "age_group", "value"]]


        st.dataframe(df_pop, use_container_width=True)

