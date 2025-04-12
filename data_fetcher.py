# data_fetcher.py
from pycoingecko import CoinGeckoAPI
import pandas as pd
from datetime import datetime

cg = CoinGeckoAPI()

def fetch_crypto_data(coin_id='bitcoin', vs_currency='usd', days='1'):
    data = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency=vs_currency, days=days)
    prices = data['prices']

    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["Time"] = pd.to_datetime(df["timestamp"], unit='ms')
    df["Close"] = df["price"]

    # We'll simulate Open/High/Low to fit the rest of your code
    df["Open"] = df["Close"]
    df["High"] = df["Close"]
    df["Low"] = df["Close"]
    df["Volume"] = 0  # Volume not available in same format

    return df[["Time", "Open", "High", "Low", "Close", "Volume"]]
