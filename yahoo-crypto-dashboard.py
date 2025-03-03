# Cryptocurrency Analysis Dashboard
# This implementation uses Python with Dash, Plotly, and the yfinance library

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import time

# Initialize the Dash app
app = dash.Dash(__name__, title="Crypto Analysis Dashboard")
server = app.server

# Define the layout
app.layout = html.Div([
    html.H1("Cryptocurrency Analysis Dashboard", className="dashboard-title"),
    
    html.Div([
        html.Div([
            html.Label("Select Cryptocurrency"),
            dcc.Dropdown(
                id='crypto-dropdown',
                options=[
                    {'label': 'Bitcoin (BTC-USD)', 'value': 'BTC-USD'},
                    {'label': 'Ethereum (ETH-USD)', 'value': 'ETH-USD'},
                    {'label': 'Cardano (ADA-USD)', 'value': 'ADA-USD'},
                    {'label': 'Solana (SOL-USD)', 'value': 'SOL-USD'},
                    {'label': 'Dogecoin (DOGE-USD)', 'value': 'DOGE-USD'}
                ],
                value='BTC-USD',
                clearable=False
            ),
        ], className="dropdown-container"),
        
        html.Div([
            html.Label("Select Timeframe"),
            dcc.Dropdown(
                id='timeframe-dropdown',
                options=[
                    {'label': '1 Day', 'value': '1d'},
                    {'label': '1 Week', 'value': '7d'},
                    {'label': '1 Month', 'value': '1mo'},
                    {'label': '3 Months', 'value': '3mo'},
                    {'label': '6 Months', 'value': '6mo'},
                    {'label': '1 Year', 'value': '1y'},
                    {'label': '2 Years', 'value': '2y'},
                    {'label': 'Year to Date', 'value': 'ytd'},
                    {'label': 'Custom Range', 'value': 'custom'}
                ],
                value='1mo',
                clearable=False
            ),
        ], className="dropdown-container"),
        
        html.Div([
            html.Label("Custom Date Range"),
            dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=datetime(2010, 1, 1),
                max_date_allowed=datetime.today(),
                start_date=datetime.today() - timedelta(days=30),
                end_date=datetime.today(),
                disabled=True
            ),
        ], className="date-picker-container"),
        
        html.Div([
            html.Button('Update Data', id='update-button', n_clicks=0),
        ], className="button-container"),
    ], className="controls-container"),
    
    html.Div([
        html.Div([
            html.H3("Price Chart", className="chart-title"),
            dcc.Graph(id='price-chart')
        ], className="chart-container"),
        
        html.Div([
            html.H3("Volume Chart", className="chart-title"),
            dcc.Graph(id='volume-chart')
        ], className="chart-container"),
    ], className="charts-row"),
    
    html.Div([
        html.Div([
            html.H3("Technical Indicators", className="chart-title"),
            dcc.Checklist(
                id='indicators-checklist',
                options=[
                    {'label': 'SMA (20)', 'value': 'sma20'},
                    {'label': 'SMA (50)', 'value': 'sma50'},
                    {'label': 'SMA (200)', 'value': 'sma200'},
                    {'label': 'EMA (20)', 'value': 'ema20'},
                    {'label': 'Bollinger Bands', 'value': 'bb'}
                ],
                value=[]
            ),
            dcc.Graph(id='technical-chart')
        ], className="chart-container full-width"),
    ], className="charts-row"),
    
    html.Div([
        html.Div([
            html.H3("Market Statistics", className="chart-title"),
            html.Div(id='market-stats', className="stats-container"),
        ], className="chart-container"),
        
        html.Div([
            html.H3("Price Change", className="chart-title"),
            html.Div(id='price-changes', className="stats-container"),
        ], className="chart-container"),
    ], className="charts-row"),
    
    dcc.Interval(
        id='interval-component',
        interval=300*1000,  # update every 5 minutes (300,000 ms)
        n_intervals=0
    )
], className="dashboard-container")

# Callback to enable/disable date picker based on timeframe selection
@app.callback(
    Output('date-picker-range', 'disabled'),
    Input('timeframe-dropdown', 'value')
)
def toggle_date_picker(selected_timeframe):
    return selected_timeframe != 'custom'

# Function to get data based on timeframe
def get_crypto_data(symbol, timeframe, start_date=None, end_date=None):
    today = datetime.today()
    
    if timeframe == 'custom' and start_date and end_date:
        start = start_date
        end = end_date
    else:
        if timeframe == '1d':
            start = today - timedelta(days=1)
            interval = '5m'
        elif timeframe == '7d':
            start = today - timedelta(days=7)
            interval = '15m'
        elif timeframe == '1mo':
            start = today - timedelta(days=30)
            interval = '1h'
        elif timeframe == '3mo':
            start = today - timedelta(days=90)
            interval = '1d'
        elif timeframe == '6mo':
            start = today - timedelta(days=180)
            interval = '1d'
        elif timeframe == '1y':
            start = today - timedelta(days=365)
            interval = '1d'
        elif timeframe == '2y':
            start = today - timedelta(days=730)
            interval = '1d'
        elif timeframe == 'ytd':
            start = datetime(today.year, 1, 1)
            interval = '1d'
        else:
            start = today - timedelta(days=30)  # default to 1 month
            interval = '1h'
        
        end = today
    
    # Get data using yfinance
    try:
        if timeframe == 'custom':
            data = yf.download(symbol, start=start, end=end)
        else:
            data = yf.download(symbol, start=start, end=end, interval=interval)
        
        # Calculate technical indicators
        if len(data) > 0:
            # Simple Moving Averages
            data['SMA20'] = data['Close'].rolling(window=20).mean()
            data['SMA50'] = data['Close'].rolling(window=50).mean()
            data['SMA200'] = data['Close'].rolling(window=200).mean()
            
            # Exponential Moving Average
            data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()
            
            # Bollinger Bands
            data['BB_middle'] = data['Close'].rolling(window=20).mean()
            data['BB_std'] = data['Close'].rolling(window=20).std()
            data['BB_upper'] = data['BB_middle'] + (data['BB_std'] * 2)
            data['BB_lower'] = data['BB_middle'] - (data['BB_std'] * 2)
            
            # Relative Strength Index (RSI)
            delta = data['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
        
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

# Callback for updating all charts
@app.callback(
    [Output('price-chart', 'figure'),
     Output('volume-chart', 'figure'),
     Output('technical-chart', 'figure'),
     Output('market-stats', 'children'),
     Output('price-changes', 'children')],
    [Input('update-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')],
    [State('crypto-dropdown', 'value'),
     State('timeframe-dropdown', 'value'),
     State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('indicators-checklist', 'value')]
)
def update_charts(n_clicks, n_intervals, symbol, timeframe, start_date, end_date, indicators):
    # Get the data
    df = get_crypto_data(symbol, timeframe, start_date, end_date)
    
    if df.empty:
        # Return empty figures if data retrieval failed
        empty_fig = go.Figure()
        empty_fig.update_layout(title="No data available")
        return empty_fig, empty_fig, empty_fig, "No data available", "No data available"
    
    # Price Chart
    price_fig = go.Figure()
    
    # Candlestick chart
    price_fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Price"
        )
    )
    
    price_fig.update_layout(
        title=f"{symbol} Price Chart",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False,
        template="plotly_dark"
    )
    
    # Volume Chart
    volume_fig = go.Figure()
    
    volume_fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name="Volume",
            marker_color="rgba(46, 134, 193, 0.8)"
        )
    )
    
    volume_fig.update_layout(
        title=f"{symbol} Volume",
        xaxis_title="Date",
        yaxis_title="Volume",
        template="plotly_dark"
    )
    
    # Technical Indicators Chart
    tech_fig = go.Figure()
    
    # Add price line
    tech_fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name="Price",
            line=dict(color='rgba(255, 255, 255, 0.8)')
        )
    )
    
    # Add selected indicators
    if 'sma20' in indicators and 'SMA20' in df.columns:
        tech_fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['SMA20'],
                mode='lines',
                name="SMA 20",
                line=dict(color='rgba(255, 0, 0, 0.7)')
            )
        )
    
    if 'sma50' in indicators and 'SMA50' in df.columns:
        tech_fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['SMA50'],
                mode='lines',
                name="SMA 50",
                line=dict(color='rgba(0, 255, 0, 0.7)')
            )
        )
    
    if 'sma200' in indicators and 'SMA200' in df.columns:
        tech_fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['SMA200'],
                mode='lines',
                name="SMA 200",
                line=dict(color='rgba(0, 0, 255, 0.7)')
            )
        )
    
    if 'ema20' in indicators and 'EMA20' in df.columns:
        tech_fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['EMA20'],
                mode='lines',
                name="EMA 20",
                line=dict(color='rgba(255, 255, 0, 0.7)')
            )
        )
    
    if 'bb' in indicators and 'BB_upper' in df.columns and 'BB_lower' in df.columns:
        tech_fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_upper'],
                mode='lines',
                name="BB Upper",
                line=dict(color='rgba(173, 216, 230, 0.7)')
            )
        )
        
        tech_fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_middle'],
                mode='lines',
                name="BB Middle",
                line=dict(color='rgba(173, 216, 230, 0.7)')
            )
        )
        
        tech_fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_lower'],
                mode='lines',
                name="BB Lower",
                line=dict(color='rgba(173, 216, 230, 0.7)')
            )
        )
    
    tech_fig.update_layout(
        title=f"{symbol} Technical Indicators",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark"
    )
    
    # Market Statistics
    current_price = df['Close'].iloc[-1]
    high_price = df['High'].max()
    low_price = df['Low'].min()
    avg_volume = df['Volume'].mean()
    
    market_stats_html = html.Div([
        html.P(f"Current Price: ${current_price:.2f}"),
        html.P(f"Highest Price: ${high_price:.2f}"),
        html.P(f"Lowest Price: ${low_price:.2f}"),
        html.P(f"Average Volume: {avg_volume:.0f}")
    ])
    
    # Price Changes
    last_price = df['Close'].iloc[-1]
    
    # Calculate different timeframe changes
    changes = {}
    for days, label in [(1, "24 Hours"), (7, "7 Days"), (30, "30 Days")]:
        if len(df) > days:
            earlier_price = df['Close'].iloc[-(days+1)] if days < len(df) else df['Close'].iloc[0]
            change_pct = ((last_price - earlier_price) / earlier_price) * 100
            changes[label] = change_pct
    
    price_changes_html = html.Div([
        html.P([
            f"{label}: ",
            html.Span(
                f"{change:.2f}%", 
                style={'color': 'green' if change >= 0 else 'red'}
            )
        ]) for label, change in changes.items()
    ])
    
    return price_fig, volume_fig, tech_fig, market_stats_html, price_changes_html

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)