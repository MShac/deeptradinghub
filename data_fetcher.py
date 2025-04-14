import pandas as pd
from datetime import datetime
from pycoingecko import CoinGeckoAPI
import requests

cg = CoinGeckoAPI()

# --- FETCH TOP 100 COINS ---
def fetch_top_100_coins(vs_currency='usd'):
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': vs_currency,
        'order': 'market_cap_desc',
        'per_page': 100,
        'page': 1,
        'sparkline': False
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching top 100 coins: {e}")
        return []

# --- FETCH HISTORICAL DATA FOR A GIVEN COIN ---
def fetch_crypto_data(coin_id='bitcoin', interval='1h', limit=100, vs_currency='usd'):
    try:
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

        df = pd.DataFrame(prices, columns=["Time", "Close"])
        df["Volume"] = [v[1] for v in volumes]
        df["Time"] = pd.to_datetime(df["Time"], unit='ms')
        df["Close"] = df["Close"].astype(float)
        df["Volume"] = df["Volume"].astype(float)

        df["Open"] = df["Close"].shift(1).fillna(method='bfill')
        df["High"] = df["Close"].rolling(window=3, min_periods=1).max()
        df["Low"] = df["Close"].rolling(window=3, min_periods=1).min()

        df = df.dropna().tail(limit).reset_index(drop=True)
        return df[["Time", "Open", "High", "Low", "Close", "Volume"]]

    except Exception as e:
        print("❌ Error fetching data from CoinGecko:", e)
        return pd.DataFrame()
