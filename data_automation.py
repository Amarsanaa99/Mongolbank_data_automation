# =========================================================
# GDP AUTOMATION PIPELINE (PRODUCTION)
# =========================================================

import requests
import pandas as pd
import itertools
from urllib.parse import quote
import logging
from datetime import datetime
import os
import sys
from google.cloud import bigquery
from google.oauth2 import service_account
import json

# ---------------------------------------------------------
# PATHS (GitHub Actions friendly)
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ---------------------------------------------------------
# LOGGING
# ---------------------------------------------------------
log_file = os.path.join(LOG_DIR, "pipeline.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

# ---------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

TIMEOUT = 30

# ---------------------------------------------------------
# BIGQUERY AUTH (GitHub Secret)
# ---------------------------------------------------------
credentials_info = json.loads(os.environ["DATA_SERVICE_ACCOUNT_KEY"])

credentials = service_account.Credentials.from_service_account_info(
    credentials_info
)

bq_client = bigquery.Client(
    credentials=credentials,
    project=credentials.project_id
)


# ---------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------
def get_table_metadata(table_path):
    encoded_path = quote(table_path, safe="/")
    url = f"https://data.1212.mn/api/v1/mn/NSO/{encoded_path}"
    r = requests.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def get_nso_data(table_path, payload):
    encoded_path = quote(table_path, safe="/")
    url = f"https://data.1212.mn/api/v1/mn/NSO/{encoded_path}"
    r = requests.post(url, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def jsonstat_to_dataframe(data):
    dimensions = data["dimension"]
    values = data["value"]

    dim_names = list(dimensions.keys())
    dim_labels = {}
    dim_sizes = []

    for dim in dim_names:
        labels = dimensions[dim]["category"]["label"]
        dim_labels[dim] = list(labels.values())
        dim_sizes.append(len(labels))

    rows = []
    for idx, combo in enumerate(itertools.product(*[range(s) for s in dim_sizes])):
        row = {}
        for i, dim in enumerate(dim_names):
            row[dim] = dim_labels[dim][combo[i]]
        row["DTVAL_CO"] = values[idx]
        rows.append(row)

    return pd.DataFrame(rows)

# ---------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------
def main():
    logging.info("🚀 GDP pipeline эхэллээ")

    table_path = "Economy, environment/National Accounts/DT_NSO_0500_022V1.px"
    metadata = get_table_metadata(table_path)

    def build_query(stat_code):
        query = {"query": [], "response": {"format": "json-stat2"}}
        for var in metadata["variables"]:
            if var["text"] == "Статистик үзүүлэлт":
                query["query"].append({
                    "code": var["code"],
                    "selection": {"filter": "item", "values": [stat_code]}
                })
            else:
                query["query"].append({
                    "code": var["code"],
                    "selection": {"filter": "item", "values": var["values"]}
                })
        return query

    def pivot_validate(df, mapping, label):
        df["component"] = df["Бүрэлдэхүүн"].replace(mapping)
        pv = (
            df.pivot_table(
            index="ОН", columns="component", values="DTVAL_CO", aggfunc="sum"
        ).reset_index()
        )
        # 👉 COLUMN ORDER-ийг mapping dict-ийн дарааллаар тогтооно
        ordered_cols = ["ОН"] + list(mapping.values())
        pv = pv.reindex(columns=ordered_cols)
        logging.info(f"📊 {label} pivot үүслээ")

        if pv.empty:
            raise ValueError(f"{label} pivot хоосон байна")

        expected = ["ОН"] + list(mapping.values())
        missing = set(expected) - set(pv.columns)
        if missing:
            raise ValueError(f"{label} pivot багана дутуу: {missing}")

        return pv

    # ===================== NGDP =====================
    ngdp_map = {
        "ДНБ": "ngdp",
        "Хөдөө аж ахуй, ойн аж ахуй, загас барилт, ан агнуур": "ngdp_agri",
        "Уул уурхай, олборлолт": "ngdp_mine",
        "Боловсруулах үйлдвэрлэл": "ngdp_manu",
        "Цахилгаан, хий, уур, агааржуулалт": "ngdp_elec",
        "Барилга": "ngdp_cons",
        "Бөөний болон жижиглэн худалдаа, машин, мотоциклийн засвар, үйлчилгээ": "ngdp_trad",
        "Тээвэр ба агуулахын үйл ажиллагаа": "ngdp_tran",
        "Мэдээлэл, холбоо": "ngdp_info",
        "Үйлчилгээний бусад үйл ажиллагаа": "ngdp_oser",
        "Бүтээгдэхүүний цэвэр татвар": "ngdp_taxe"
    }

    df_ngdp = jsonstat_to_dataframe(get_nso_data(table_path, build_query("0")))
    pv_ngdp = pivot_validate(df_ngdp, ngdp_map, "NGDP")

    # ===================== RGDP =====================
    rgdp_map = {k: f"rgdp_2015{v[4:]}" for k, v in ngdp_map.items()}
    df_rgdp = jsonstat_to_dataframe(get_nso_data(table_path, build_query("3")))
    pv_rgdp = pivot_validate(df_rgdp, rgdp_map, "RGDP")

    # ===================== GROWTH =====================
    growth_map = {k: f"growth{v[4:]}" for k, v in ngdp_map.items()}
    df_growth = jsonstat_to_dataframe(get_nso_data(table_path, build_query("6")))
    pv_growth = pivot_validate(df_growth, growth_map, "GDP Growth")

    # ===================== MERGE =====================
    final_df = (
        pv_ngdp
        .merge(pv_rgdp, on="ОН", how="outer")
        .merge(pv_growth, on="ОН", how="outer")
    )

    # ===================== EXPORT =====================
    today = datetime.now().strftime("%Y%m%d")
    output_file = os.path.join(OUTPUT_DIR, f"GDP_pipeline_{today}.xlsx")
    final_df.to_excel(output_file, index=False, float_format="%.2f")

    logging.info(f"✅ Амжилттай дууслаа → {output_file}")

    # ===================== LONG FORMAT FOR BIGQUERY =====================
    id_col = "ОН"
    value_cols = [c for c in final_df.columns if c != id_col]

    long_df = final_df.melt(
        id_vars=id_col,
        value_vars=value_cols,
        var_name="indicator_code",
        value_name="value"
    )

    long_df = long_df.rename(columns={"ОН": "year"})

    long_df["source"] = "NSO / Mongolbank API"
    long_df["loaded_at"] = pd.Timestamp.utcnow()

    # 0 / NULL цэвэрлэгээ
    long_df = long_df.dropna(subset=["value"])

    # ===================== LOAD TO BIGQUERY =====================
    table_id = "mongol-bank-macro-data.Automation_data.fact_macro"

    job = bq_client.load_table_from_dataframe(
        long_df,
        table_id,
        job_config=bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND"
        )
    )

    job.result()
    logging.info("✅ Long macro data BigQuery-д амжилттай нэмэгдлээ")


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    main()
