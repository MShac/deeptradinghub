# data_fetcher.py
import pandas as pd
from datetime import datetime
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

def fetch_crypto_data(coin_id='bitcoin', vs_currency='usd', days='1'):
    try:
        data = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency=vs_currency, days=days)
        prices = data.get('prices', [])
        volumes = data.get('total_volumes', [])

        if not prices or not volumes:
            return pd.DataFrame()  # Return empty if data is missing

        # Create DataFrame
        df = pd.DataFrame(prices, columns=["Time", "Close"])
        df["Volume"] = [v[1] for v in volumes]
        df["Time"] = pd.to_datetime(df["Time"], unit='ms')

        # Approximate OHLC from close prices (used for plotting and prediction)
        df["Open"] = df["Close"].shift(1)
        df["High"] = df["Close"].rolling(window=3, min_periods=1).max()
        df["Low"] = df["Close"].rolling(window=3, min_periods=1).min()

        df = df.dropna().reset_index(drop=True)
        return df[["Time", "Open", "High", "Low", "Close", "Volume"]]

    except Exception as e:
        print("❌ Error fetching data from CoinGecko:", e)
        return pd.DataFrame()
