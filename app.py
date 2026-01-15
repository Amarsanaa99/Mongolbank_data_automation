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
                period,
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
    # ⏱ Frequency (GLOBAL, SINGLE)
    #=====================================
    with st.container(border=True):
        st.markdown("### ⏱ Frequency")
    
        freq = st.radio(
            "",
            ["Yearly", "Quarterly", "Monthly"],
            horizontal=True
        )
    
    freq_map = {
        "Yearly": "Y",
        "Quarterly": "Q",
        "Monthly": "M"
    }
    selected_freq = freq_map[freq]
    
    # ==============================
    # 🔎 DATA-AWARE FILTER (SAFE)
    # ==============================
    if filtered_df.empty:
        st.warning("⚠️ No data available for selected filters.")
        time_filtered_df = pd.DataFrame()
    
    elif selected_freq not in filtered_df["time_freq"].unique():
        st.warning(
            f"⚠️ This dataset does not contain {freq.lower()} data."
        )
        time_filtered_df = pd.DataFrame()
    
    else:
        time_filtered_df = (
            filtered_df
            .loc[filtered_df["time_freq"] == selected_freq]
            .copy()
        )
    # ⏳ TIME RANGE (FREQUENCY-AWARE)
    # ==============================
    if not time_filtered_df.empty:
    
        with st.container(border=True):
            st.markdown("### ⏳ Time range")
    
            if selected_freq == "Y":
                year_list = sorted(time_filtered_df["year"].unique())
            
                start_y = st.selectbox(
                    "Start year",
                    year_list,
                    index=0
                )
            
                end_y = st.selectbox(
                    "End year",
                    year_list,
                    index=len(year_list) - 1
                )
            
                # 🔒 SAFETY CHECK
                if start_y > end_y:
                    st.error("❌ Start year must be before End year")
                    time_filtered_df = pd.DataFrame()
                else:
                    time_filtered_df = time_filtered_df[
                        (time_filtered_df["year"] >= start_y) &
                        (time_filtered_df["year"] <= end_y)
                    ]

            elif selected_freq == "Q":
                time_filtered_df["t"] = (
                    time_filtered_df["year"].astype(str)
                    + "-Q"
                    + time_filtered_df["period"].astype(str)
                )
            
                t_list = sorted(time_filtered_df["t"].unique())
            
                start_q = st.selectbox("Start quarter", t_list, index=0)
                end_q = st.selectbox("End quarter", t_list, index=len(t_list)-1)
            
                if start_q > end_q:
                    st.error("❌ Start quarter must be before End quarter")
                    time_filtered_df = pd.DataFrame()
                else:
                    time_filtered_df = time_filtered_df[
                        (time_filtered_df["t"] >= start_q) &
                        (time_filtered_df["t"] <= end_q)
                    ]

            elif selected_freq == "M":
                # 🧱 Temporary time key
                time_filtered_df["t"] = (
                    time_filtered_df["year"].astype(str)
                    + "-"
                    + time_filtered_df["period"].astype(str).str.zfill(2)
                )
            
                t_list = sorted(time_filtered_df["t"].unique())
            
                start_m = st.selectbox("Start month", t_list, index=0)
                end_m = st.selectbox("End month", t_list, index=len(t_list) - 1)
            
                # 🔒 SAFETY CHECK
                if start_m > end_m:
                    st.error("❌ Start month must be before End month")
                    time_filtered_df = pd.DataFrame()
                else:
                    time_filtered_df = time_filtered_df[
                        (time_filtered_df["t"] >= start_m) &
                        (time_filtered_df["t"] <= end_m)
                    ]
                                # 🧹 REMOVE TEMP COLUMN
    time_filtered_df = time_filtered_df.drop(columns=["t"], errors="ignore")
    





    # =============================
    # CREATE TIME LABEL (STANDARD)
    # =============================
    if not time_filtered_df.empty:
    
        if selected_freq == "Y":
            time_filtered_df["time_label"] = time_filtered_df["year"].astype(str)
    
        elif selected_freq == "Q":
            time_filtered_df["time_label"] = (
                time_filtered_df["year"].astype(str)
                + "-Q"
                + time_filtered_df["period"].astype(str)
            )
    
        elif selected_freq == "M":
            time_filtered_df["time_label"] = (
                time_filtered_df["year"].astype(str)
                + "-"
                + time_filtered_df["period"].astype(str).str.zfill(2)
            )

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
                # ===== GDP (HEADLINE ONLY) =====
                if topic == "gdp":
                
                    plot_df = time_filtered_df.copy()
                
                    # =============================
                    # 🔒 DEFENSIVE CHECK — ЯГ ЭНД
                    # =============================
                    if "time_label" not in plot_df.columns:
                        st.error("❌ time_label is missing — check frequency logic")
                
                    else:
                        chart_df = (
                            plot_df
                            .pivot_table(
                                index="time_label",
                                columns="indicator_code",
                                values="value",
                                aggfunc="mean"
                            )
                        )
                
                        st.line_chart(chart_df)





    
                # ===== POPULATION =====
                else:
                    plot_df = time_filtered_df.copy()
    
                    chart = (
                        alt.Chart(plot_df)
                        .mark_line()
                        .encode(
                            x=alt.X("time_label:N", title="Time"),
                            y=alt.Y("value:Q", title="Population"),
                            color=alt.Color(
                                "Series:N",
                                legend=alt.Legend(orient="right")
                            ),
                            tooltip=["time_label", "sex", "age_group", "value"]
                        )
                        .properties(height=400)
                    )

                    st.altair_chart(chart, use_container_width=True)

                    # ⬇️ CSV DOWNLOAD (ICON ONLY)
                    csv = plot_df[
                        ["time_label", "sex", "age_group", "value"]
                    ].to_csv(index=False).encode("utf-8")
                    
                    st.download_button(
                        label="⬇️",
                        data=csv,
                        file_name="main_chart_population.csv",
                        mime="text/csv",
                        help="Download chart data as CSV"
                    )

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

                # ===== GDP INDICATOR (SMART HEADLINE) =====
                if cfg["type"] == "indicator":
                
                    base_df = headline_df[
                        headline_df["indicator_code"]
                        .fillna("")
                        .str.lower()
                        .str.startswith(cfg["code"])
                    ].copy()
                
                    # 🔥 RGDP / NGDP → yearly SUM (4 улирал)
                    if cfg["code"] in ["rgdp_2005", "rgdp_2010", "rgdp_2015", "ngdp"]:
                        plot_df = (
                            base_df
                            .groupby("year_num", as_index=True)["value"]
                            .sum()
                            .to_frame()
                            .sort_index()
                        )
                
                    # 🔥 GROWTH → yearly MEAN
                    elif cfg["code"] == "growth":
                        plot_df = (
                            base_df
                            .groupby("year_num", as_index=True)["value"]
                            .mean()
                            .to_frame()
                            .sort_index()
                        )
                
                    # fallback (аюулгүй)
                    else:
                        plot_df = (
                            base_df
                            .drop_duplicates(subset=["year_num"])
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
