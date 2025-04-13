import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_fetcher import fetch_crypto_data
from model import predict_signal
from indicators import (
    calculate_sma,
    calculate_ema,
    calculate_macd,
    calculate_rsi,
    calculate_bollinger_bands,
    calculate_atr,
    calculate_vwap,
    calculate_fibonacci_levels,
    get_nearest_level
)
import time

# Page config
st.set_page_config(page_title="DeepTradeAI", layout="wide")

# Custom CSS
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }
        .main {
            background-color: #0f0f0f;
            color: #ffffff;
        }
        .stButton>button {
            background-color: #00adb5;
            color: white;
        }
        h1, h2, h3, h4 {
            background: -webkit-linear-gradient(45deg, #00adb5, #eeeeee);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .block-container {
            padding: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://i.imgur.com/XRdNmtD.png", width=200)
st.sidebar.title("DeepTradeAI")
symbol = st.sidebar.selectbox("Select Coin", ["bitcoin", "ethereum", "dogecoin"], index=0)
interval = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d"], index=0)

# Toggle indicators
show_sma = st.sidebar.checkbox("SMA")
show_ema = st.sidebar.checkbox("EMA")
show_macd = st.sidebar.checkbox("MACD")
show_rsi = st.sidebar.checkbox("RSI")
show_bbands = st.sidebar.checkbox("Bollinger Bands")
show_atr = st.sidebar.checkbox("ATR")
show_vwap = st.sidebar.checkbox("VWAP")
show_fib = st.sidebar.checkbox("Fibonacci Levels", value=True)

# Utility to map interval to CoinGecko-compatible `days`
def timeframe_to_days(interval):
    mapping = {
        "1m": "1",
        "5m": "1",
        "15m": "1",
        "1h": "1",
        "4h": "1",
        "1d": "7"
    }
    return mapping.get(interval, "1")

# Header
st.title("📊 DeepTradeAI - Crypto Predictor")
st.markdown("**Live Crypto Chart + Indicators + Buy/Sell Prediction Engine**")

# Fetch data
days = timeframe_to_days(interval)
df = fetch_crypto_data(symbol, days=days)

if df.empty:
    st.error("No data fetched. Please check your internet connection or try a different coin.")
    st.stop()

# Add indicators
if show_sma:
    df["SMA"] = calculate_sma(df["Close"])
if show_ema:
    df["EMA"] = calculate_ema(df["Close"])
if show_macd:
    df["MACD"], df["Signal Line"] = calculate_macd(df["Close"])
if show_rsi:
    df["RSI"] = calculate_rsi(df["Close"])
if show_bbands:
    df["Upper"], df["Middle"], df["Lower"] = calculate_bollinger_bands(df["Close"])
if show_atr:
    df["ATR"] = calculate_atr(df["High"], df["Low"], df["Close"])
if show_vwap:
    df["VWAP"] = calculate_vwap(df)

# Calculate Fibonacci levels and entry
fib_levels = calculate_fibonacci_levels(df["Close"])
entry = get_nearest_level(df["Close"].iloc[-1], fib_levels)

# Predict Buy/Sell Signal
signal = predict_signal(df)
last_price = df["Close"].iloc[-1]

# Set SL/TP
sl = entry * 0.97
tp = entry * 1.05

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("📈 Entry Price", f"${entry:.2f}")
col2.metric("❌ Stop Loss", f"${sl:.2f}")
col3.metric("✅ Take Profit", f"${tp:.2f}")

st.markdown(f"### 📍 Signal: **{signal}**")
st.success("Buy Now!" if signal == "Buy" else "Sell Now!" if signal == "Sell" else "Hold")

# Chart
fig = go.Figure()

# Candlestick
fig.add_trace(go.Candlestick(
    x=df["Time"],
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="Candles"
))

# Indicators on chart
if show_sma:
    fig.add_trace(go.Scatter(x=df["Time"], y=df["SMA"], mode='lines', name="SMA"))
if show_ema:
    fig.add_trace(go.Scatter(x=df["Time"], y=df["EMA"], mode='lines', name="EMA"))
if show_bbands:
    fig.add_trace(go.Scatter(x=df["Time"], y=df["Upper"], mode='lines', name="Upper Band"))
    fig.add_trace(go.Scatter(x=df["Time"], y=df["Lower"], mode='lines', name="Lower Band"))
if show_vwap:
    fig.add_trace(go.Scatter(x=df["Time"], y=df["VWAP"], mode='lines', name="VWAP"))

# Fibonacci levels on chart
if show_fib:
    for level, price in fib_levels.items():
        fig.add_hline(y=price, line_dash="dot", annotation_text=level, line_color="#aaaaaa")

# Styling
fig.update_layout(
    title=f"{symbol.upper()} Price Chart",
    xaxis_title="Time",
    yaxis_title="Price (USD)",
    template="plotly_dark",
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Mubashir — [DeepTradingHub.com](http://deeptradinghub.com)")
