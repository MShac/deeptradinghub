import streamlit as st
from utils import display_header

st.set_page_config(page_title="About - DeepTradeAI", layout="wide")

display_header("About DeepTradeAI", "logo.jpg")

# --- About Box ---
with st.container():
    st.markdown("## 🚀 What is DeepTradeAI?")
    st.markdown("""
    **DeepTradeAI** is a cutting-edge platform that empowers crypto traders with AI-driven predictions, 
    powerful visual insights, and advanced technical analysis. Built by a solo developer passionate about the future 
    of finance and AI, this tool combines **real-time market data**, **technical indicators**, and 
    **machine learning models** to give you high-confidence Buy/Sell signals.
    """)

# --- Features Box ---
with st.container():
    st.markdown("## 💡 Features")
    st.markdown("""
    - 📈 Real-time price data from Binance  
    - 🕯️ Live charting with candlesticks & technical indicators  
    - 🤖 Smart Buy/Sell predictions using XGBoost model  
    - 📐 Fibonacci retracement levels for strategy building  
    - ⏱️ Multi-timeframe support for flexible trading  
    - 🛑🎯 Custom SL/TP calculation based on real indicators  
    """)

# --- Why DeepTradeAI ---
with st.container():
    st.markdown("## 👨‍💻 Why DeepTradeAI?")
    st.markdown("""
    Trading crypto can be overwhelming — DeepTradeAI simplifies your decisions by giving you clean, 
    algorithmically-backed insights that help reduce risk and improve trade timing.

    Whether you're a day trader or a long-term investor, this tool gives you an edge with clarity, speed, and intelligence.
    """)

# --- Footer ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:right;color:gray;'>Created with ❤️ by <strong>Mubashir</strong> – Cybersecurity + AI Enthusiast</p>",
    unsafe_allow_html=True
)
