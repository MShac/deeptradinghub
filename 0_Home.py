import streamlit as st
import base64
import requests
import plotly.graph_objects as go
from data_fetcher import fetch_crypto_datasymbol = st.text_input("🔍 CoinGecko Coin ID (e.g. bitcoin, ethereum, solana):", DEFAULT_SYMBOL).lower()

from indicators import calculate_indicators, find_support_resistance
from model import train_model, predict_trade
from config import DEFAULT_SYMBOL, DEFAULT_INTERVAL, DEFAULT_LIMIT
import pandas as pd 


st.set_page_config(page_title="DeepTradeAI", layout="wide")

# --- LOGO ENCODING ---
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

logo_path = "logo.jpg"
logo_base64 = encode_image(logo_path)

# --- CUSTOM STYLING ---
st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

        /* Global theme overrides */
        html, body, [class*="css"] {{
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: #f5f5f5;
        }}

        /* Header styling */
        .header-container {{
            display: flex;
            align-items: center;
            padding: 1.5rem 0;
            margin-bottom: 2rem;
            border-bottom: 1px solid #333;
        }}
        .header-container img {{
            width: 72px;
            height: 72px;
            border-radius: 50%;
            object-fit: cover;
            margin-right: 20px;
            box-shadow: 0 0 10px rgba(0, 198, 255, 0.8);
        }}
        .header-container h1 {{
            font-size: 3rem;
            background: linear-gradient(to right, #00c6ff, #0072ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.6);
            margin: 0;
        }}

        /* Card styling with hover animation */
        .card {{
            background-color: #1c1f26;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            margin-bottom: 1.5rem;
            transition: transform 0.3s ease;
            animation: fadeIn 1s ease-in-out;
        }}
        .card:hover {{
            transform: scale(1.02);
        }}
        @keyframes fadeIn {{
            0% {{opacity: 0; transform: translateY(20px);}}
            100% {{opacity: 1; transform: translateY(0);}}
        }}

        /* Styling for live price metrics */
        [data-testid="stMetricValue"] {{
            color: #00e5ff;
            font-size: 1.5rem;
            text-shadow: 0 0 6px rgba(0, 229, 255, 0.6);
        }}

        /* Sidebar styling */
        .sidebar .sidebar-content {{
            background-color: #212d38;
            color: #f5f5f5;
            padding: 1.5rem;
            border-radius: 10px;
        }}
        .sidebar h1 {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }}

        /* Footer styling */
        footer {{
            text-align: center;
            color: #bbb;
            margin-top: 2rem;
            font-size: 0.85rem;
        }}
        footer hr {{
            border: 0.5px solid #444;
            margin-bottom: 1rem;
        }}
        footer p {{
            font-weight: 600;
        }}

        /* Mobile responsiveness adjustments */
        @media (max-width: 768px) {{
            .header-container {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .header-container h1 {{
                font-size: 2.5rem;
            }}
            .card {{
                padding: 1rem;
            }}
            .sidebar {{
                display: none;
            }}
            footer {{
                font-size: 1rem;
            }}
        }}
    </style>
    <div class="header-container">
        <img src="data:image/jpeg;base64,{logo_base64}" alt="Logo">
        <h1>DeepTradeAI</h1>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.title("⚙️ Settings")
   symbol = st.text_input("🔍 CoinGecko Coin ID (e.g. bitcoin, ethereum, solana):", DEFAULT_SYMBOL).lower()

    interval = st.selectbox("⏱️ Timeframe:", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)
    show_fib = st.checkbox("📐 Show Fibonacci Levels", value=True)
    show_indicators = st.checkbox("📊 Show Technical Indicators", value=True)
    show_sr = st.checkbox("🔁 Show Support/Resistance", value=True)

   from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()

def get_live_price(symbol):
    try:
        data = cg.get_price(ids=symbol, vs_currencies='usd')
        return data[symbol]['usd']
    except:
        return None


    live_price = get_live_price(symbol)
    if live_price:
        st.metric(label=f"💰 Live Price ({symbol})", value=f"${live_price:.2f}")

    st.markdown("---")
    if st.button("🔄 Get Prediction"):
        st.session_state.run_prediction = True

# --- MAIN SECTION ---
# Keep everything above the same...

# --- MAIN SECTION ---
if st.session_state.get("run_prediction", False):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔮 Prediction Engine")

    # Fetch crypto data
    df = fetch_crypto_data(symbol, interval, limit=DEFAULT_LIMIT)

    # Check if the DataFrame is empty
    if df.empty:
        st.error("❌ Failed to fetch data. Please check the symbol or try again.")
    else:
        df.columns = df.columns.str.strip()
        df['Time'] = pd.to_datetime(df['Time'])

        df = calculate_indicators(df)
        support, resistance = find_support_resistance(df)

        # Calculate Fibonacci retracement levels
        fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
        fib_range = resistance - support
        fib_prices = [support + fib_range * level for level in fib_levels]

        # Fetch live price
        live_price = get_live_price(symbol)
        if live_price:
            nearest_fib = min(fib_prices, key=lambda x: abs(x - live_price))
            entry_level = nearest_fib
            st.write(f"Entry Level (Nearest Fibonacci): ${entry_level:.2f}")

        model, scaler = train_model(df)

        if model:
            prediction, entry_price, (stop_loss, take_profit) = predict_trade(df, model, scaler, support, resistance)
            st.write(f"Prediction: {prediction}")
            entry_price = entry_level
        else:
            prediction, entry_price, stop_loss, take_profit = "No Signal", 0, 0, 0

        col1, col2, col3 = st.columns(3)
        col1.metric("📍 Entry", f"${entry_price:.2f}")
        col2.metric("🛑 Stop Loss", f"${stop_loss:.2f}")
        col3.metric("🎯 Take Profit", f"${take_profit:.2f}")

        # --- CHART ANALYSIS ---
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📈 Chart Analysis")

        last_100 = df.tail(100)
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=last_100['Time'],
            open=last_100['Open'],
            high=last_100['High'],
            low=last_100['Low'],
            close=last_100['Close'],
            name="Candles"
        ))

        if show_fib:
            for level, fib_price in zip(['Fib_0.236', 'Fib_0.382', 'Fib_0.5', 'Fib_0.618', 'Fib_0.786'], fib_prices):
                fig.add_trace(go.Scatter(
                    x=last_100['Time'],
                    y=[fib_price]*len(last_100),
                    name=level,
                    line=dict(dash='dot')
                ))

        if show_indicators:
            if 'EMA_9' in df.columns:
                fig.add_trace(go.Scatter(x=last_100['Time'], y=last_100['EMA_9'], name='EMA 9', line=dict(color='orange')))
            if 'EMA_21' in df.columns:
                fig.add_trace(go.Scatter(x=last_100['Time'], y=last_100['EMA_21'], name='EMA 21', line=dict(color='blue')))

        if show_sr and support and resistance:
            fig.add_hline(y=support, line_color="green", line_dash="dash", annotation_text="Support", annotation_position="bottom left")
            fig.add_hline(y=resistance, line_color="red", line_dash="dash", annotation_text="Resistance", annotation_position="top left")

        fig.update_layout(
            template="plotly_dark",
            xaxis_title="Time",
            yaxis_title="Price",
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown(
    """
    <footer>
        <hr>
        <p>© 2025 DeepTradeAI. Built with ❤️ and AI.</p>
    </footer>
    """,
    unsafe_allow_html=True
)
