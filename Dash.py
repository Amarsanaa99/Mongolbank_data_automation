import pathlib

import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, ctx
import plotly.graph_objects as go

# ========= 1. DATA LOADING (ТАНЫ LOGIC-ООС АВАВ) =========

BASE_DIR = pathlib.Path(__file__).resolve().parent
EXCEL_PATH = BASE_DIR / "Dashboard_cleaned_data.xlsx"


def read_sheet(sheet: str) -> pd.DataFrame:
    return pd.read_excel(EXCEL_PATH, sheet_name=sheet, header=[0, 1])


def prepare_dataframe(dataset: str):
    df = read_sheet(dataset)

    if not isinstance(df.columns, pd.MultiIndex):
        raise ValueError("Unexpected data format - expected MultiIndex columns")

    # TIME баганууд
    time_cols = [c for c in df.columns if c[0] in ["Year", "Month", "Quarter"]]

    if not time_cols:
        raise ValueError("No time columns found")

    df_time = df[time_cols].copy()
    df_data = df.drop(columns=time_cols)

    # frequency
    freq = "Monthly" if "Month" in df_time.columns.get_level_values(0) else "Quarterly"

    # TIME header-ыг хялбарчлах
    for i, col in enumerate(df_time.columns):
        if isinstance(col, tuple):
            df_time.columns.values[i] = col[0]

    # DATA header clean
    level0 = df_data.columns.get_level_values(0)
    level1 = df_data.columns.get_level_values(1)

    new_level0 = []
    for val in level0:
        if pd.isna(val) or "Unnamed" in str(val):
            new_level0.append(new_level0[-1] if new_level0 else "Other")
        else:
            new_level0.append(val)

    df_data.columns = pd.MultiIndex.from_arrays([new_level0, level1])

    # TIME series бэлтгэх
    series = df_time.copy()

    def as_series(col):
        if isinstance(col, pd.DataFrame):
            return col.iloc[:, 0]
        return col

    # FIX: fillna
    for col in ["Year", "Month", "Quarter"]:
        if col in series.columns:
            series[col] = series[col].ffill()

    # to numeric
    for col in ["Year", "Month", "Quarter"]:
        if col in series.columns:
            values = series[col].values.tolist() if hasattr(series[col], "values") else series[col]

            if isinstance(values, list) and values and isinstance(values[0], list):
                values = [v[0] if isinstance(v, list) else v for v in values]

            series[col] = pd.to_numeric(pd.Series(values), errors="coerce")

    year = as_series(series["Year"]) if "Year" in series.columns else None
    month = as_series(series["Month"]) if "Month" in series.columns else None
    quarter = as_series(series["Quarter"]) if "Quarter" in series.columns else None

    if year is not None and month is not None:
        series["time"] = (
            year.astype(int).astype(str) + "-" +
            month.astype(int).astype(str).str.zfill(2)
        )
    elif year is not None and quarter is not None:
        series["time"] = (
            year.astype(int).astype(str) + "-Q" +
            quarter.astype(int).astype(str)
        )
    elif year is not None:
        series["time"] = year.astype(int).astype(str)
    else:
        raise ValueError("No valid time columns found")

    # year_label
    series["year_label"] = series["Year"].astype(int).astype(str)

    for col in ["Year", "Month", "Quarter"]:
        if col in series.columns:
            series[col] = as_series(series[col])

    return series, df_data, freq


# ========= 2. DASH APP =========

app = Dash(__name__)
app.title = "Mongolbank Macro Dashboard (Dash)"


if __name__ == "__main__":
    app.run_server(debug=True)
