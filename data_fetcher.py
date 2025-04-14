# data_fetcher.py
import pandas as pd
from datetime import datetime
from pycoingecko import CoinGeckoAPI
from functools import lru_cache

@lru_cache(maxsize=1)  # Cache for performance
def load_coin_symbol_mapping():
    print("🔄 Loading coin list from CoinGecko...")
    try:
        coin_list = cg.get_coins_list()
        mapping = {}

        for coin in coin_list:
            name = coin['name'].lower()
            symbol = coin['symbol'].upper()
            id = coin['id']

            # Build USDT pair like BTCUSDT, ETHUSDT, etc.
            mapping[symbol + "USDT"] = id
            mapping[symbol + "/USDT"] = id
            mapping[symbol] = id  # Also support BTC, ETH, etc.

        return mapping
    except Exception as e:
        print("❌ Error loading coin list:", e)
        return {}


cg = CoinGeckoAPI()
def fetch_crypto_data(symbol='BTCUSDT', interval='1h', limit=100, vs_currency='usd'):
    try:
        symbol = symbol.upper()
        symbol_map = load_coin_symbol_mapping()

        if symbol not in symbol_map:
            raise ValueError(f"❌ Unsupported symbol: {symbol}")
        coin_id = symbol_map[symbol]

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
            raise ValueError(f"❌ Unsupported interval: {interval}")
        
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
        print("❌ Error fetching data:", e)
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
