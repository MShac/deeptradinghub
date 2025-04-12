import streamlit as st
from utils import display_header

st.set_page_config(page_title="Team - DeepTradeAI", layout="wide")
display_header("Meet the Team", "logo.jpg")

# --- Team Section ---
st.markdown("## 👥 Our Team")
st.markdown("""
- **Mubashir** — *Lead Developer, Data Scientist & Cybersecurity Expert*  
  Responsible for the development, data science, and security implementation of DeepTradeAI. Mubashir combines his expertise in **cybersecurity**, **AI**, and **machine learning** to build secure, accurate, and reliable crypto trading prediction systems. His skills in data processing, algorithm development, and securing web applications ensure DeepTradeAI's effectiveness in delivering real-time trading insights to users.

  **Key Responsibilities:**
  - **Crypto Trading Prediction Model Development:** Designing and training machine learning models, including XGBoost, for predicting buy/sell signals.
  - **Data Processing & Feature Engineering:** Collecting and processing data from various sources (e.g., Binance API) and engineering features to optimize model performance.
  - **Security Implementation:** Ensuring the application is secure and free of vulnerabilities, particularly from cyber threats.
  - **Backend Development:** Building the backend to handle data fetching, processing, and prediction execution.

  **Skills & Technologies:**
  - **Languages:** Python, SQL, C++
  - **Tools & Libraries:** Streamlit, XGBoost, pandas, scikit-learn, Plotly
  - **Cybersecurity Expertise:** Knowledge in penetration testing, vulnerability analysis, and secure application development.
  
  Mubashir's passion for **cybersecurity** and **AI-driven trading** comes from his dedication to improving trading experiences while maintaining robust security.
  .
""")

# --- Footer ---
st.markdown("""
<p style='color:#888888; font-size: 0.9rem; margin-top: 2rem; text-align: right;'>
Created with ❤️ by Mubashir – Cybersecurity + AI Enthusiast
</p>
""", unsafe_allow_html=True)
