import pandas as pd

def calculate_indicators(df):
    """Calculate SMA, MACD, ATR, VWAP, Bollinger Bands, EMA, and Fibonacci Levels."""
    if df.empty:
        return df

    # SMA
    df['SMA'] = df['Close'].rolling(window=10, min_periods=1).mean()

    # MACD
    df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()

    # ATR
    df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()

    # VWAP
    df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()

    # Bollinger Bands
    df['Bollinger_Upper'] = df['SMA'] + (2 * df['Close'].rolling(10).std())
    df['Bollinger_Lower'] = df['SMA'] - (2 * df['Close'].rolling(10).std())

    # EMA
    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()

    # Fibonacci Levels (last 50 candles)
    lookback = 50
    df['Fibo_High'] = df['High'].rolling(lookback).max()
    df['Fibo_Low'] = df['Low'].rolling(lookback).min()
    for level in [0.236, 0.382, 0.5, 0.618, 0.786]:
        df[f'Fib_{level}'] = df['Fibo_High'] - ((df['Fibo_High'] - df['Fibo_Low']) * level)

    return df

def find_support_resistance(df, window=20):
    """Find recent support and resistance levels from the last N candles."""
    if df.empty or len(df) < window:
        return None, None

    recent = df.tail(window)
    support = recent['Low'].min()
    resistance = recent['High'].max()
    return support, resistance
