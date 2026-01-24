import pandas as pd
from pathlib import Path
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import altair as alt
from dash_extensions import DashProxy
from dash_extensions.enrich import Output, Input, State

# App init
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server  # For deployment (Heroku, etc.)

# Base directory
BASE_DIR = Path(__file__).resolve().parent
EXCEL_PATH = BASE_DIR / "Dashboard_cleaned_data.xlsx"

# Read sheet
def read_sheet(sheet):
    return pd.read_excel(EXCEL_PATH, sheet_name=sheet, header=[0, 1])

sheets = [s for s in pd.ExcelFile(EXCEL_PATH).sheet_names
          if s.lower() in ["month", "quarter"]]

available_groups = []
available_indicators = []

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3("📦 Dataset"),
            dcc.RadioItems(
                id='dataset-radio',
                options=[{'label': s, 'value': s} for s in sheets],
                value=sheets[0],
                inline=True
            ),
            html.Div(id='freq-output', style={'marginTop': '10px'}),
        ], width=3),

        dbc.Col([
            html.H3("📈 Main chart"),
            dcc.Graph(id='main-chart'),
            html.Div(id='kpi-cards')
        ], width=9)
    ])
], fluid=True)
@app.callback(
    Output('main-chart', 'figure'),
    Output('kpi-cards', 'children'),
    Input('dataset-radio', 'value'),
)
def update_chart(dataset):
    df = read_sheet(dataset)
    # ... Streamlit data prep кодыг энд ашиглана ...
    # Altair chart бэлтгэх
    chart = alt.Chart(df).mark_line().encode(
        x='time:T',
        y='Value:Q'
    )
    return chart.to_dict(), generate_kpi_cards(df)
def generate_kpi_cards(df):
    cards = []
    for ind in df.columns[1:4]:  # Жишээ
        cards.append(
            dbc.Card([
                dbc.CardHeader(ind),
                dbc.CardBody(html.P(f"{df[ind].iloc[-1]:.2f}"))
            ], color="primary", inverse=True)
        )
    return dbc.Row(cards, className="mb-2")
if __name__ == "__main__":
    app.run_server(debug=True)
