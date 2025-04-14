# data_fetcher.py
import pandas as pd
from datetime import datetime
from pycoingecko import CoinGeckoAPI
import streamlit as st

cg = CoinGeckoAPI()

@st.cache_data(show_spinner="📡 Fetching all coin names from CoinGecko...")
def get_all_coins_dict():
    coins = cg.get_coins_list()
    return {f"{coin['name']} ({coin['symbol'].upper()})": coin['id'] for coin in coins}

def fetch_crypto_data(coin_id='bitcoin', interval='1h', limit=100, vs_currency='usd'):
    try:
        # Map interval to CoinGecko 'days' param
        interval_map = {
            '1m': '1',
            '5m': '1',
            '15m': '1',
            '30m': '1',
            '1h': '7',
            '4h': '14',
            '1d': '30'
        }

        if interval not in interval_map:
            raise ValueError(f"Unsupported interval: {interval}")

        days = interval_map[interval]
        data = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency=vs_currency, days=days)

        prices = data.get('prices', [])
        volumes = data.get('total_volumes', [])

        if not prices or not volumes:
            return pd.DataFrame()

        # Build DataFrame
        df = pd.DataFrame(prices, columns=["Time", "Close"])
        df["Volume"] = [v[1] for v in volumes]
        df["Time"] = pd.to_datetime(df["Time"], unit='ms')
        df["Close"] = df["Close"].astype(float)
        df["Volume"] = df["Volume"].astype(float)

        # Approximate OHLC
        df["Open"] = df["Close"].shift(1).fillna(method='bfill')
        df["High"] = df["Close"].rolling(window=3, min_periods=1).max()
        df["Low"] = df["Close"].rolling(window=3, min_periods=1).min()

        # Limit rows to `limit`
        df = df.dropna().tail(limit).reset_index(drop=True)

        return df[["Time", "Open", "High", "Low", "Close", "Volume"]]

    except Exception as e:
        print("❌ Error fetching data from CoinGecko:", e)
        return pd.DataFrame()
