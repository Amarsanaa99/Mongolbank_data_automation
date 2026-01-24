import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import math

# Dash app идэвхжүүлэх
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

# Өгөгдөл унших
BASE_DIR = Path(__file__).resolve().parent
EXCEL_PATH = BASE_DIR / "assets" / "Dashboard_cleaned_data.xlsx"

# Өгөгдөл cache-лах
def read_sheet(sheet):
    return pd.read_excel(EXCEL_PATH, sheet_name=sheet, header=[0, 1])

def get_sheets():
    return [s for s in pd.ExcelFile(EXCEL_PATH).sheet_names 
            if s.lower() in ["month", "quarter"]]

# Өгөгдөл боловсруулах функцууд
def process_data(df, dataset):
    """Өгөгдөл боловсруулах"""
    if isinstance(df.columns, pd.MultiIndex):
        # TIME багануудыг олох
        time_cols = []
        for col in df.columns:
            if col[0] in ["Year", "Month", "Quarter"]:
                time_cols.append(col)
        
        if not time_cols:
            return None, None, None
        
        # TIME ба DATA салгах
        df_time = df[time_cols].copy()
        df_data = df.drop(columns=time_cols)
        
        # TIME багануудыг хялбарчилна
        for i, col in enumerate(df_time.columns):
            if isinstance(col, tuple):
                df_time.columns.values[i] = col[0]
        
        # DATA-ийн header-ыг цэвэрлэх
        level0 = df_data.columns.get_level_values(0)
        level1 = df_data.columns.get_level_values(1)
        
        new_level0 = []
        for val in level0:
            if pd.isna(val) or "Unnamed" in str(val):
                new_level0.append(new_level0[-1] if new_level0 else "Other")
            else:
                new_level0.append(val)
        
        df_data.columns = pd.MultiIndex.from_arrays([new_level0, level1])
        
        # Time цуваа үүсгэх
        series = df_time.copy()
        
        # FIX: Year / Month / Quarter block structure
        for col in ["Year", "Month", "Quarter"]:
            if col in series.columns:
                series[col] = series[col].ffill()
        
        # Time багануудыг тоон утга болгох
        for col in ["Year", "Month", "Quarter"]:
            if col in series.columns:
                values = series[col].values.tolist() if hasattr(series[col], 'values') else series[col]
                if isinstance(values, list) and values and isinstance(values[0], list):
                    values = [v[0] if isinstance(v, list) else v for v in values]
                series[col] = pd.to_numeric(pd.Series(values), errors='coerce')
        
        # CREATE TIME INDEX
        year = series["Year"] if "Year" in series.columns else None
        month = series["Month"] if "Month" in series.columns else None
        quarter = series["Quarter"] if "Quarter" in series.columns else None
        
        if year is not None and month is not None:
            series["time"] = (
                year.astype(int).astype(str) + "-" +
                month.astype(int).astype(str).str.zfill(2)
            )
            freq = "Monthly"
        elif year is not None and quarter is not None:
            series["time"] = (
                year.astype(int).astype(str) + "-Q" +
                quarter.astype(int).astype(str)
            )
            freq = "Quarterly"
        elif year is not None:
            series["time"] = year.astype(int).astype(str)
            freq = "Yearly"
        else:
            return None, None, None
        
        # Өгөгдөл нэмэх
        for group in df_data.columns.get_level_values(0).unique():
            indicators = [col[1] for col in df_data.columns if col[0] == group]
            for indicator in indicators:
                if (group, indicator) in df_data.columns:
                    series[f"{group}||{indicator}"] = df_data[(group, indicator)].values
        
        return series, df_data, freq
    
    return None, None, None

def compute_kpis(df, indicator):
    """KPI тооцоолох"""
    if indicator not in df.columns:
        return {}
    
    series = df[["time", indicator]].copy()
    series[indicator] = pd.to_numeric(series[indicator], errors="coerce")
    series = series.dropna()
    
    if len(series) == 0:
        return {}
    
    return {
        "last": float(series[indicator].iloc[-1]),
        "last_date": str(series["time"].iloc[-1]),
        "mean": float(series[indicator].mean()),
        "median": float(series[indicator].median()),
        "min": float(series[indicator].min()),
        "max": float(series[indicator].max()),
        "std": float(series[indicator].std())
    }

def compute_changes(df, indicator, freq):
    """Өөрчлөлт тооцоолох"""
    s = df[["time", indicator]].dropna().copy()
    s["time"] = s["time"].astype(str).str.strip()
    s = s[s["time"] != ""]
    
    if len(s) < 2:
        return {}
    
    s = s.sort_values("time").reset_index(drop=True)
    latest_val = float(s.iloc[-1][indicator])
    prev_val = float(s.iloc[-2][indicator])
    
    # Prev (QoQ / MoM)
    prev = (latest_val / prev_val - 1) * 100 if prev_val != 0 else None
    
    # YoY
    yoy = None
    if freq == "Quarterly" and len(s) >= 5:
        base_val = float(s.iloc[-5][indicator])
        if base_val != 0:
            yoy = (latest_val / base_val - 1) * 100
    elif freq == "Monthly" and len(s) >= 13:
        base_val = float(s.iloc[-13][indicator])
        if base_val != 0:
            yoy = (latest_val / base_val - 1) * 100
    
    # YTD
    ytd = None
    try:
        current_year = s.iloc[-1]["time"][:4]
        year_data = s[s["time"].str.startswith(current_year)]
        if len(year_data) >= 1:
            year_start = float(year_data.iloc[0][indicator])
            if year_start != 0:
                ytd = (latest_val / year_start - 1) * 100
    except:
        ytd = None
    
    return {
        "latest": latest_val,
        "prev": prev,
        "yoy": yoy,
        "ytd": ytd
    }

# App layout
app.layout = dbc.Container([
    # Header
    html.Div([
        html.H1("🏦 Dashboard", className="mt-4 mb-2"),
        html.P("Macro Indicators", className="text-muted mb-4"),
    ], className="mb-4"),
    
    # Main content
    dbc.Row([
        # Left column - Controls
        dbc.Col([
            # Dataset selection
            dbc.Card([
                dbc.CardHeader("📦 Dataset"),
                dbc.CardBody([
                    dcc.RadioItems(
                        id='dataset-radio',
                        options=[{'label': s, 'value': s} for s in get_sheets()],
                        value=get_sheets()[0] if get_sheets() else None,
                        className="mb-0"
                    )
                ])
            ], className="mb-3"),
            
            # Frequency display
            html.Div(id='frequency-display', className="mb-3"),
            
            # Indicator group
            dbc.Card([
                dbc.CardHeader("🧭 Indicator group"),
                dbc.CardBody([
                    dcc.RadioItems(id='group-radio', className="mb-0")
                ])
            ], className="mb-3"),
            
            # Indicators
            dbc.Card([
                dbc.CardHeader("📌 Indicators"),
                dbc.CardBody([
                    dcc.Dropdown(
                        id='indicators-dropdown',
                        multi=True,
                        placeholder="Select indicators..."
                    )
                ])
            ], className="mb-3"),
            
            # Time range
            dbc.Card([
                dbc.CardHeader("⏳ Time range"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Start Year", className="form-label"),
                            dcc.Dropdown(id='start-year', placeholder="Start Year")
                        ]),
                        dbc.Col([
                            html.Label("End Year", className="form-label"),
                            dcc.Dropdown(id='end-year', placeholder="End Year")
                        ])
                    ], className="mb-2"),
                    
                    html.Div(id='month-quarter-selectors'),
                    
                    html.Div(id='time-range-display', className="mt-2 text-muted small")
                ])
            ], className="mb-3"),
            
        ], width=3, className="pe-3"),
        
        # Right column - Charts and data
        dbc.Col([
            # Main chart
            dbc.Card([
                dbc.CardHeader("📈 Main chart"),
                dbc.CardBody([
                    dcc.Graph(id='main-chart', config={'displayModeBar': True})
                ])
            ], className="mb-4"),
            
            # KPI cards
            dbc.Card([
                dbc.CardHeader("📊 Indicator-level KPIs"),
                dbc.CardBody([
                    html.Div(id='kpi-cards', className="row")
                ])
            ], className="mb-4"),
            
            # Change summary
            dbc.Card([
                dbc.CardHeader("📉 Change summary"),
                dbc.CardBody([
                    html.Div(id='change-summary')
                ])
            ], className="mb-4"),
            
            # All indicator groups
            dbc.Card([
                dbc.CardHeader("📊 All indicator groups"),
                dbc.CardBody([
                    dcc.Graph(id='small-multiples', config={'displayModeBar': False})
                ])
            ], className="mb-4"),
            
            # Raw data
            dbc.Card([
                dbc.CardHeader([
                    "📄 Raw data - ",
                    html.Span(id='raw-data-group', className="text-primary")
                ]),
                dbc.CardBody([
                    html.Div(id='raw-data-table')
                ])
            ], className="mb-4"),
            
        ], width=9)
    ]),
    
    # Hidden data storage
    dcc.Store(id='data-store'),
    dcc.Store(id='freq-store')
], fluid=True, className="p-4")

# Callback: Dataset сонгох -> Data боловсруулах
@app.callback(
    [Output('data-store', 'data'),
     Output('freq-store', 'data'),
     Output('frequency-display', 'children'),
     Output('group-radio', 'options'),
     Output('start-year', 'options'),
     Output('end-year', 'options')],
    [Input('dataset-radio', 'value')]
)
def update_dataset(dataset):
    if not dataset:
        return {}, {}, "", [], [], []
    
    df = read_sheet(dataset)
    series, df_data, freq = process_data(df, dataset)
    
    if series is None:
        return {}, {}, "❌ Error processing data", [], [], []
    
    # Data-г JSON болгох
    series_json = series.to_json(date_format='iso', orient='split')
    
    # Frequency display
    freq_display = html.P(f"Frequency: {freq}", className="text-muted mb-0")
    
    # Group options
    if df_data is not None:
        groups = sorted(df_data.columns.get_level_values(0).unique())
        group_options = [{'label': g, 'value': g} for g in groups]
    else:
        group_options = []
    
    # Year options
    years = sorted(series['Year'].dropna().unique().astype(int).tolist())
    year_options = [{'label': str(y), 'value': y} for y in years]
    
    return series_json, freq, freq_display, group_options, year_options, year_options

# Callback: Group сонгох -> Indicators update
@app.callback(
    [Output('indicators-dropdown', 'options'),
     Output('indicators-dropdown', 'value')],
    [Input('group-radio', 'value'),
     Input('data-store', 'data')]
)
def update_indicators(group, data_json):
    if not group or not data_json:
        return [], []
    
    series = pd.read_json(data_json, orient='split')
    
    # Group-ийн indicators-г олох
    indicators = []
    for col in series.columns:
        if '||' in str(col) and col.startswith(f"{group}||"):
            indicator_name = col.split('||')[1]
            indicators.append(indicator_name)
    
    indicators = sorted(set(indicators))
    options = [{'label': ind, 'value': ind} for ind in indicators]
    
    # Анхны утга
    value = [indicators[0]] if indicators else []
    
    return options, value

# Callback: Year сонгох -> Month/Quarter selectors
@app.callback(
    [Output('month-quarter-selectors', 'children'),
     Output('time-range-display', 'children')],
    [Input('freq-store', 'data'),
     Input('start-year', 'value'),
     Input('end-year', 'value')]
)
def update_time_selectors(freq, start_year, end_year):
    if not freq or not start_year or not end_year:
        return "", ""
    
    if freq == "Monthly":
        selectors = dbc.Row([
            dbc.Col([
                html.Label("Start Month", className="form-label"),
                dcc.Dropdown(
                    id='start-month',
                    options=[{'label': f"{m:02d}", 'value': m} for m in range(1, 13)],
                    value=1
                )
            ]),
            dbc.Col([
                html.Label("End Month", className="form-label"),
                dcc.Dropdown(
                    id='end-month',
                    options=[{'label': f"{m:02d}", 'value': m} for m in range(1, 13)],
                    value=12
                )
            ])
        ], className="mb-2")
        
        time_display = html.Small(f"Range: {start_year}-01 to {end_year}-12")
        
    elif freq == "Quarterly":
        selectors = dbc.Row([
            dbc.Col([
                html.Label("Start Quarter", className="form-label"),
                dcc.Dropdown(
                    id='start-quarter',
                    options=[{'label': f"Q{q}", 'value': q} for q in range(1, 5)],
                    value=1
                )
            ]),
            dbc.Col([
                html.Label("End Quarter", className="form-label"),
                dcc.Dropdown(
                    id='end-quarter',
                    options=[{'label': f"Q{q}", 'value': q} for q in range(1, 5)],
                    value=4
                )
            ])
        ], className="mb-2")
        
        time_display = html.Small(f"Range: {start_year}-Q1 to {end_year}-Q4")
    
    else:
        selectors = html.Div()
        time_display = html.Small(f"Range: {start_year} to {end_year}")
    
    return selectors, time_display

# Callback: Main chart үүсгэх
@app.callback(
    Output('main-chart', 'figure'),
    [Input('data-store', 'data'),
     Input('freq-store', 'data'),
     Input('group-radio', 'value'),
     Input('indicators-dropdown', 'value'),
     Input('start-year', 'value'),
     Input('end-year', 'value'),
     Input('start-month', 'value'),
     Input('end-month', 'value'),
     Input('start-quarter', 'value'),
     Input('end-quarter', 'value')]
)
def update_main_chart(data_json, freq, group, indicators, start_year, end_year,
                      start_month, end_month, start_quarter, end_quarter):
    if not data_json or not group or not indicators:
        return go.Figure()
    
    series = pd.read_json(data_json, orient='split')
    
    # Time range үүсгэх
    if freq == "Monthly":
        start_time = f"{start_year}-{start_month:02d}" if start_month else f"{start_year}-01"
        end_time = f"{end_year}-{end_month:02d}" if end_month else f"{end_year}-12"
    elif freq == "Quarterly":
        start_time = f"{start_year}-Q{start_quarter}" if start_quarter else f"{start_year}-Q1"
        end_time = f"{end_year}-Q{end_quarter}" if end_quarter else f"{end_year}-Q4"
    else:
        start_time = str(start_year)
        end_time = str(end_year)
    
    # Өгөгдөл бэлтгэх
    plot_data = series[['time']].copy()
    for indicator in indicators:
        col_name = f"{group}||{indicator}"
        if col_name in series.columns:
            plot_data[indicator] = series[col_name]
    
    # Time range filter
    plot_data = plot_data[(plot_data['time'] >= start_time) & 
                         (plot_data['time'] <= end_time)].copy()
    
    if plot_data.empty:
        return go.Figure()
    
    # Main chart үүсгэх
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set2
    for i, indicator in enumerate(indicators):
        if indicator in plot_data.columns:
            color = colors[i % len(colors)]
            fig.add_trace(go.Scatter(
                x=plot_data['time'],
                y=plot_data[indicator],
                name=indicator,
                mode='lines+markers',
                line=dict(width=2, color=color),
                marker=dict(size=6, color=color),
                hovertemplate=(
                    f"<b>{indicator}</b><br>" +
                    "Time: %{x}<br>" +
                    "Value: %{y:.2f}<br>" +
                    "<extra></extra>"
                )
            ))
    
    # Layout тохируулах
    fig.update_layout(
        height=400,
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(0, 0, 0, 0.1)',
            borderwidth=1
        ),
        margin=dict(l=0, r=100, t=0, b=0),
        xaxis=dict(
            title=None,
            showgrid=True,
            gridcolor='rgba(0, 0, 0, 0.1)',
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(count=2, label="2y", step="year", stepmode="backward"),
                    dict(count=5, label="5y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        ),
        yaxis=dict(
            title=None,
            showgrid=True,
            gridcolor='rgba(0, 0, 0, 0.1)'
        ),
        plot_bgcolor='white'
    )
    
    return fig

# Callback: KPI картууд үүсгэх
@app.callback(
    [Output('kpi-cards', 'children'),
     Output('raw-data-group', 'children')],
    [Input('data-store', 'data'),
     Input('group-radio', 'value'),
     Input('indicators-dropdown', 'value')]
)
def update_kpi_cards(data_json, group, indicators):
    if not data_json or not group or not indicators:
        return html.Div("Select indicators to see KPIs"), group or ""
    
    series = pd.read_json(data_json, orient='split')
    primary_indicator = indicators[0] if indicators else None
    
    if not primary_indicator:
        return html.Div("No indicator selected"), group
    
    col_name = f"{group}||{primary_indicator}"
    if col_name not in series.columns:
        return html.Div("Indicator data not found"), group
    
    # KPI тооцоолох
    kpis = compute_kpis(series, col_name)
    
    if not kpis:
        return html.Div("No KPI data available"), group
    
    # KPI картууд үүсгэх
    cards = []
    
    kpi_data = [
        ("LAST VALUE", f"{kpis['last']:.2f}", kpis['last_date']),
        ("MEAN", f"{kpis['mean']:.2f}", None),
        ("MEDIAN", f"{kpis['median']:.2f}", None),
        ("MINIMUM VALUE", f"{kpis['min']:.2f}", None),
        ("MAXIMUM VALUE", f"{kpis['max']:.2f}", None),
        ("STD (VOLATILITY)", f"{kpis['std']:.2f}", None),
    ]
    
    for label, value, sublabel in kpi_data:
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div(label, className="kpi-label"),
                    html.H4(value, className="kpi-value mt-2"),
                    html.Div(sublabel or "", className="kpi-sub mt-1")
                ], className="p-3")
            ], className="h-100 border-0 shadow-sm")
        ], width=2, className="mb-3")
        cards.append(card)
    
    return dbc.Row(cards, className="g-2"), f"{group}"

# Callback: Change summary үүсгэх
@app.callback(
    Output('change-summary', 'children'),
    [Input('data-store', 'data'),
     Input('freq-store', 'data'),
     Input('group-radio', 'value'),
     Input('indicators-dropdown', 'value')]
)
def update_change_summary(data_json, freq, group, indicators):
    if not data_json or not group or not indicators:
        return html.Div("Select indicators to see changes")
    
    series = pd.read_json(data_json, orient='split')
    change_cards = []
    
    for indicator in indicators:
        col_name = f"{group}||{indicator}"
        if col_name in series.columns:
            changes = compute_changes(series, col_name, freq)
            
            if changes:
                card = dbc.Card([
                    dbc.CardBody([
                        html.H6(indicator, className="mb-2"),
                        html.Div([
                            html.Span(f"YoY: {changes.get('yoy', 'N/A'):.1f}%" if changes.get('yoy') is not None else "YoY: N/A", 
                                     className="me-3"),
                            html.Span(f"YTD: {changes.get('ytd', 'N/A'):.1f}%" if changes.get('ytd') is not None else "YTD: N/A", 
                                     className="me-3"),
                            html.Span(f"Prev: {changes.get('prev', 'N/A'):.1f}%" if changes.get('prev') is not None else "Prev: N/A")
                        ], className="small")
                    ], className="p-3")
                ], className="mb-2 shadow-sm")
                change_cards.append(card)
    
    if not change_cards:
        return html.Div("No change data available")
    
    return html.Div(change_cards)

# Callback: Small multiples үүсгэх
@app.callback(
    Output('small-multiples', 'figure'),
    [Input('data-store', 'data'),
     Input('freq-store', 'data')]
)
def update_small_multiples(data_json, freq):
    if not data_json:
        return go.Figure()
    
    series = pd.read_json(data_json, orient='split')
    
    # Бүх group-уудыг олох
    groups = set()
    indicators_by_group = {}
    
    for col in series.columns:
        if '||' in str(col):
            group, indicator = col.split('||')
            if group not in groups:
                groups.add(group)
                indicators_by_group[group] = []
            indicators_by_group[group].append(indicator)
    
    groups = sorted(groups)
    
    if not groups:
        return go.Figure()
    
    # Subplot үүсгэх
    n_cols = 4
    n_rows = math.ceil(len(groups) / n_cols)
    
    fig = make_subplots(
        rows=n_rows, 
        cols=n_cols,
        subplot_titles=groups,
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    colors = px.colors.qualitative.Set2
    
    for idx, group in enumerate(groups):
        row = (idx // n_cols) + 1
        col = (idx % n_cols) + 1
        
        indicators = indicators_by_group.get(group, [])[:5]  # Зөвхөн эхний 5-г харуулах
        
        for i, indicator in enumerate(indicators):
            col_name = f"{group}||{indicator}"
            if col_name in series.columns:
                color = colors[i % len(colors)]
                
                # 2020 оноос хойшх өгөгдөл
                plot_data = series[['time', col_name]].copy()
                plot_data = plot_data[plot_data['time'] >= "2020"]
                
                fig.add_trace(
                    go.Scatter(
                        x=plot_data['time'],
                        y=plot_data[col_name],
                        name=indicator,
                        mode='lines',
                        line=dict(width=1.5, color=color),
                        showlegend=False,
                        hovertemplate=(
                            f"<b>{indicator}</b><br>" +
                            "Time: %{x}<br>" +
                            "Value: %{y:.2f}<br>" +
                            "<extra></extra>"
                        )
                    ),
                    row=row, col=col
                )
        
        # Subplot layout тохируулах
        fig.update_xaxes(
            title_text="",
            showgrid=True,
            gridcolor='rgba(0, 0, 0, 0.1)',
            row=row, col=col
        )
        
        fig.update_yaxes(
            title_text="",
            showgrid=True,
            gridcolor='rgba(0, 0, 0, 0.1)',
            row=row, col=col
        )
    
    # Ерөнхий layout
    fig.update_layout(
        height=300 * n_rows,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

# Callback: Raw data table үүсгэх
@app.callback(
    Output('raw-data-table', 'children'),
    [Input('data-store', 'data'),
     Input('group-radio', 'value')]
)
def update_raw_data(data_json, group):
    if not data_json or not group:
        return html.Div("Select a group to see raw data")
    
    series = pd.read_json(data_json, orient='split')
    
    # Group-ийн өгөгдлүүдийг олох
    group_columns = [col for col in series.columns if str(col).startswith(f"{group}||")]
    
    if not group_columns:
        return html.Div("No data available for this group")
    
    # DataFrame үүсгэх
    raw_df = pd.DataFrame({'time': series['time']})
    for col in group_columns:
        indicator = col.split('||')[1]
        raw_df[indicator] = series[col]
    
    # Table үүсгэх
    table = dbc.Table(
        # Header
        [html.Thead(html.Tr([html.Th("Time")] + [html.Th(ind.split('||')[1]) for ind in group_columns]))] +
        # Body
        [html.Tbody([
            html.Tr([html.Td(row['time'])] + [html.Td(f"{row[ind.split('||')[1]]:.2f}" if not pd.isna(row[ind.split('||')[1]]) else "") 
                    for ind in group_columns])
            for _, row in raw_df.head(20).iterrows()  # Зөвхөн эхний 20 мөр
        ])],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
        className="small"
    )
    
    return table

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
