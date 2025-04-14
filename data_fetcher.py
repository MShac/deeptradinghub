import pandas as pd
import time
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

INTERVAL_MAP = {
    "1d": "daily",
    "1h": "hourly",
    "4h": "hourly",
    "1m": "minutely",
    "5m": "minutely",
    "15m": "minutely"
}

def fetch_crypto_data(symbol_id, interval, limit=100):
    """
    Fetch historical OHLC data for the given coin from CoinGecko.
    :param symbol_id: CoinGecko ID (e.g. 'bitcoin')
    :param interval: e.g. '1m', '5m', '15m', '1h', '4h', '1d'
    :param limit: number of candles to return (max depends on interval)
    :return: DataFrame with OHLCV data
    """
    interval_type = INTERVAL_MAP.get(interval, "daily")
    days = 1 if interval in ["1m", "5m", "15m", "1h", "4h"] else 30

    try:
        market_chart = cg.get_coin_market_chart_by_id(id=symbol_id, vs_currency='usd', days=days)
        prices = market_chart['prices']
        df = pd.DataFrame(prices, columns=['Time', 'Close'])
        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        df['Close'] = df['Close'].astype(float)

        # Simulate OHLC from close prices (since only 'Close' is available from CoinGecko minutely/hourly)
        df['Open'] = df['Close'].shift(1).fillna(method='bfill')
        df['High'] = df[['Close', 'Open']].max(axis=1)
        df['Low'] = df[['Close', 'Open']].min(axis=1)
        df = df[['Time', 'Open', 'High', 'Low', 'Close']]

        # Resample based on interval
        interval_map = {
            '1m': '1T', '5m': '5T', '15m': '15T',
            '1h': '1H', '4h': '4H', '1d': '1D'
        }

        if interval in interval_map:
            df = df.set_index('Time').resample(interval_map[interval]).agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last'
            }).dropna().reset_index()

        df = df.tail(limit).reset_index(drop=True)
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol_id}: {e}")
        return pd.DataFrame()
