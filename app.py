import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import altair as alt
# =====================================================
# MACRO / CENTRAL BANK PALETTE
# =====================================================
COLOR_PALETTE = [
    "#1F2937",  # Almost black (primary)
    "#2563EB",  # Deep blue
    "#DC2626",  # Dark red
    "#047857",  # Dark green
    "#7C3AED",  # Deep purple
    "#B45309",  # Brown / gold
    "#0F766E",  # Teal
    "#374151"   # Gray
]

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
        start_num = (
            int(start_q.split("-")[0])
            + (int(start_q.split("-")[1]) - 1) / 4
        )
        end_num = (
            int(end_q.split("-")[0])
            + (int(end_q.split("-")[1]) - 1) / 4
        )
    
        time_filtered_df = filtered_df[
            (filtered_df["year_num"] >= start_num) &
            (filtered_df["year_num"] <= end_num)
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
            # ===== GDP =====
            if topic == "gdp":
            
                plot_df = (
                    time_filtered_df
                    .groupby(["year_num", "indicator_code"], as_index=False)
                    .agg({"value": "sum"})
                    .rename(columns={"indicator_code": "Series"})
                )
            
                chart = (
                    alt.Chart(plot_df)
                    .mark_line(
                        interpolate="linear",   # 🔑 SHARP
                        strokeWidth=1.8         # 🔑 CRISP
                    )
                    .encode(
                        x=alt.X(
                            "year_num:Q",
                            title="",
                            axis=alt.Axis(
                                grid=False,
                                tickSize=3,
                                labelColor="#111827"
                            )
                        ),
                        y=alt.Y(
                            "value:Q",
                            title="",
                            axis=alt.Axis(
                                grid=True,
                                gridColor="#E5E7EB",
                                labelColor="#111827"
                            )
                        ),
                        color=alt.Color(
                            "Series:N",
                            scale=alt.Scale(range=COLOR_PALETTE),
                            legend=alt.Legend(
                                orient="bottom",
                                title=None,
                                labelLimit=220
                            )
                        ),
                        tooltip=[
                            alt.Tooltip("Series:N", title="Indicator"),
                            alt.Tooltip("value:Q", format=",.1f")
                        ]
                    )
                    .properties(height=420)
                    .configure_view(stroke=None)
                    .configure_axis(domain=True)
                )
            
                st.altair_chart(chart, use_container_width=True)



            # ===== POPULATION =====
            else:
                plot_df = time_filtered_df.copy()

                hover = alt.selection_point(
                    fields=["Series"],
                    on="mouseover",
                    nearest=True,
                    clear="mouseout"
                )
                
                chart = (
                    alt.Chart(plot_df)
                    .mark_line(
                        interpolate="linear",
                        strokeWidth=1.6
                    )
                    .encode(
                        x=alt.X(
                            "year_num:Q",
                            title="",
                            axis=alt.Axis(grid=False, labelColor="#111827")
                        ),
                        y=alt.Y(
                            "value:Q",
                            title="",
                            axis=alt.Axis(
                                grid=True,
                                gridColor="#E5E7EB",
                                labelColor="#111827"
                            )
                        ),
                        color=alt.Color(
                            "Series:N",
                            scale=alt.Scale(range=COLOR_PALETTE),
                            legend=alt.Legend(
                                orient="bottom",
                                title=None
                            )
                        ),
                        tooltip=[
                            alt.Tooltip("Series:N", title="Group"),
                            alt.Tooltip("value:Q", format=",.0f")
                        ]
                    )
                    .properties(height=420)
                    .configure_view(stroke=None)
                    .configure_axis(domain=True)
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

