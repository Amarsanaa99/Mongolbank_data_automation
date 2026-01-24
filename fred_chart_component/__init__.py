import json
import pathlib
import streamlit.components.v1 as components

# Энэ файл байгаа хавтас (fred_chart_component/)
_COMPONENT_DIR = pathlib.Path(__file__).parent

_fred_chart = components.declare_component(
    "fred_chart",
    path=str(_COMPONENT_DIR / "frontend" / "build")  # build гарч ирэх зам
)

def render_fred_chart(time, series, indicators, key=None):
    """
    time: ["2020-01-01", "2020-02-01", ...]
    series: {"Forecast 1": [...], "Forecast 2": [...], ...}
    indicators: ["Forecast 1", "Forecast 2", ...]
    """
    payload = {
        "time": time,
        "series": series,
        "indicators": indicators,
    }
    _fred_chart(data=json.dumps(payload), key=key)
