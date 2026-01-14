import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import altair as alt

# =====================================================
# PAGE CONFIG (⚠️ ЗААВАЛ ЭХНИЙ МӨРҮҮДИЙН НЭГ БАЙНА)
# =====================================================
st.set_page_config(
    page_title="Mongolbank Macro Data Dashboard",
    layout="wide"
)
# =====================================================
# HEADLINE CONFIG (EXTENSIBLE)
# =====================================================

HEADLINE_CONFIG = [
    {
        "type": "indicator",
        "code": "rgdp_2005",
        "title": "RGDP 2005",
        "subtitle": "Real GDP (2005 prices)",
        "topic": "gdp"
    },
    {
        "type": "indicator",
        "code": "rgdp_2010",
        "title": "RGDP 2010",
        "subtitle": "Real GDP (2010 prices)",
        "topic": "gdp"
    },
    {
        "type": "indicator",
        "code": "rgdp_2015",
        "title": "RGDP 2015",
        "subtitle": "Real GDP (2015 prices)",
        "topic": "gdp"
    },
    {
        "type": "indicator",
        "code": "ngdp",
        "title": "NGDP",
        "subtitle": "Nominal GDP",
        "topic": "gdp"
    },
    {
        "type": "indicator",
        "code": "growth",
        "title": "GDP Growth",
        "subtitle": "YoY growth",
        "topic": "gdp"
    },
    {
        "type": "population_total",   # 🔥 indicator_code биш!
        "title": "Population",
        "subtitle": "Total population",
        "topic": "population"
    }
]



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
# =====================================================
# HEADLINE DATA LOADER (FILTER-INDEPENDENT)
# =====================================================

@st.cache_data(ttl=3600)
def load_headline_data():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(
        credentials=credentials,
        project=st.secrets["gcp_service_account"]["project_id"]
    )
    query = """
    SELECT
        topic,
        indicator_code,
        value,
        year,
        period,
        time_freq,
        year_num,
        sex,
        age_group
    FROM `mongol-bank-macro-data.Automation_data.fact_macro_clean`
    WHERE topic IN ('gdp','population')
    ORDER BY year_num
    """
    df = client.query(query).to_dataframe()
    return df

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
                year_num,
                time_freq,
                indicator_code,
                value,
                sex,
                age_group
            FROM `mongol-bank-macro-data.Automation_data.fact_macro_clean`
            WHERE topic = '{topic}'
            ORDER BY year_num
        """
        return client.query(query).to_dataframe()

    # 3️⃣ DATA LOAD
    with st.spinner("⏳ Loading data from BigQuery..."):
        df = load_data(topic)

    # ---------- GDP TYPE SELECTOR ----------
    if topic == "gdp":
    
        with st.container(border=True):
            st.markdown("### 📊 GDP type")
            gdp_type = st.radio(
                "",
                ["RGDP2005", "RGDP2010", "RGDP2015", "NGDP", "GROWTH"],
                horizontal=True
            )
    
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
    
        # ✅ Indicators container GDP-ийн ДООР
        with st.container(border=True):
            st.markdown("### 📌 Indicators")
    
            selected_indicators = st.multiselect(
                "",
                available_indicators,
                default=available_indicators[:1] if available_indicators else []
            )
    
        filtered_df = df[df["indicator_code"].isin(selected_indicators)]
    
    # ---------- POPULATION ----------
    else:
        sex = st.multiselect(
            "Sex",
            sorted(df["sex"].dropna().unique()),
            default=[]
        )
    
        age_group = st.multiselect(
            "Age group",
            sorted(df["age_group"].dropna().unique()),
            default=[]
        )
    
        if sex and age_group:
            filtered_df = df[
                df["sex"].isin(sex) &
                df["age_group"].isin(age_group)
            ]
        else:
            filtered_df = df.copy()

    #=====================================
    #Time filter
    #=====================================
    with st.container(border=True):
        st.markdown("### ⏱ Frequency")
    
        freq = st.radio(
            "",
            ["Yearly", "Quarterly", "Monthly"],
            horizontal=True
        )
    
    freq_map_rev = {
        "Quarterly": "Q",
        "Monthly": "M",
        "Yearly": "Y"
    }
    selected_freq_code = freq_map_rev[freq]
    
    if selected_freq_code not in filtered_df["time_freq"].unique():
        st.warning(
            f"⚠️ This dataset does not contain {freq.lower()} data."
        )
        time_filtered_df = pd.DataFrame()   # хоосон
    else:
        filtered_df = filtered_df[
            filtered_df["time_freq"] == selected_freq_code
        ]


    
        # ===== QUARTERLY =====
        if freq == "Quarterly":
            options = sorted(filtered_df["year"].unique())
        
            col1, col2 = st.columns(2)
            with col1:
                start = st.selectbox(
                    "Start quarter",
                    options,
                    index=0
                )
            with col2:
                end = st.selectbox(
                    "End quarter",
                    options,
                    index=len(options) - 1
                )
        
            # 🔥 STRING COMPARE БИШ — year_num
            start_num = filtered_df.loc[
                filtered_df["year"] == start, "year_num"
            ].iloc[0]
        
            end_num = filtered_df.loc[
                filtered_df["year"] == end, "year_num"
            ].iloc[0]
        
            time_filtered_df = filtered_df[
                (filtered_df["year_num"] >= start_num) &
                (filtered_df["year_num"] <= end_num)
            ]
    
    
        # ===== MONTHLY =====
        elif freq == "Monthly":
            options = sorted(filtered_df["year"].unique())
        
            col1, col2 = st.columns(2)
            with col1:
                start = st.selectbox(
                    "Start month",
                    options,
                    index=0
                )
            with col2:
                end = st.selectbox(
                    "End month",
                    options,
                    index=len(options) - 1
                )
        
            time_filtered_df = filtered_df[
                (filtered_df["year"] >= start) &
                (filtered_df["year"] <= end)
            ]
        
        # ===== YEARLY =====
        else:
            years = sorted(filtered_df["year"].astype(int).unique())
        
            start_y, end_y = st.slider(
                "Year range",
                min(years),
                max(years),
                (min(years), max(years))
            )
        
            time_filtered_df = filtered_df[
                (filtered_df["year"].astype(int) >= start_y) &
                (filtered_df["year"].astype(int) <= end_y)
            ]


    # ---------- SERIES COLUMN (POPULATION) ----------
    if topic == "population":
        time_filtered_df = time_filtered_df.copy()
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
                # ===== GDP =====   👈👈👈 ЭНЭ ХЭСЭГ
                if topic == "gdp":
                    chart_df = (
                        time_filtered_df
                        .pivot_table(
                            index="year_num",
                            columns="indicator_code",
                            values="value",
                            aggfunc="sum"   # ❌ ЯГ ЭНЭ МӨР
                        )
                        .sort_index()
                    )
                    st.line_chart(chart_df)


    
                # ===== POPULATION =====
                else:
                    plot_df = time_filtered_df.copy()
    
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
# HEADLINE INDICATORS (EXTENSIBLE, FILTER-INDEPENDENT)
# =====================================================

headline_df = load_headline_data()

st.markdown("## 📊 Headline indicators")

N_COLS = 4
rows = [
    HEADLINE_CONFIG[i:i + N_COLS]
    for i in range(0, len(HEADLINE_CONFIG), N_COLS)
]

for row in rows:
    cols = st.columns(N_COLS)
    for col, cfg in zip(cols, row):
        with col:
            with st.container(border=True):
    
                st.markdown(f"""
                <div style="text-align:center">
                    <div style="font-weight:600">{cfg["title"]}</div>
                    <div style="font-size:12px;opacity:0.6">{cfg["subtitle"]}</div>
                </div>
                """, unsafe_allow_html=True)
    
                # ===== GDP INDICATOR =====
                if cfg["type"] == "indicator":
                    plot_df = (
                        headline_df[
                            headline_df["indicator_code"]
                            .fillna("")                              # 🔥 ЭНЭ ЧУХАЛ
                            .str.lower()
                            .str.startswith(cfg["code"])
                        ]
                        .set_index("year_num")[["value"]]
                        .sort_index()
                    )

                # ===== POPULATION TOTAL =====
                elif cfg["type"] == "population_total":
                    plot_df = (
                        headline_df[
                            (headline_df["topic"] == "population") &
                            (headline_df["sex"] == "Бүгд") &
                            (headline_df["age_group"] == "Бүгд")
                        ]
                        .set_index("year_num")[["value"]]
                        .sort_index()
                    )

                st.line_chart(plot_df, height=160)
                
# =====================================================
# RAW DATA Preview
# =====================================================
with st.expander("📄 Raw data"):

    # ===================== GDP =====================
    if topic == "gdp":
    
        # 🔑 GDP TYPE-д таарах prefix
        raw_prefix = prefix_map[gdp_type]
    
        raw_df = df[
            df["indicator_code"].str.lower().str.startswith(raw_prefix)
        ].copy()
    
        df_pivot = (
            raw_df
            .pivot_table(
                index="year",
                columns="indicator_code",
                values="value",
                aggfunc="sum"
            )
            .reset_index()
        )
    
        ordered_cols = (
            ["year"] +
            sorted([c for c in df_pivot.columns if c.startswith(raw_prefix)])
        )
    
        df_pivot = df_pivot[ordered_cols]
    
        st.dataframe(df_pivot, use_container_width=True)

    # ===================== POPULATION =====================
    else:
    # 🔑 Зөвхөн sex filter
        if sex:
            raw_pop = df[df["sex"].isin(sex)].copy()
        else:
            raw_pop = df.copy()
        df_pop = (
            raw_pop
            .sort_values(["year", "sex", "age_group"])
            [["year", "sex", "age_group", "value"]]
        )
    
        st.dataframe(df_pop, use_container_width=True)
