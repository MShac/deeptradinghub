import pandas as pd

def calculate_indicators(df):
    if df.empty:
        return df

    # Faster SMA
    df['SMA'] = df['Close'].rolling(window=5, min_periods=1).mean()

    # Faster MACD (shorten fast EMA)
    df['MACD'] = df['Close'].ewm(span=8, adjust=False).mean() - df['Close'].ewm(span=21, adjust=False).mean()

    # ATR with shorter window
    df['ATR'] = (df['High'] - df['Low']).rolling(7).mean()

    # Bollinger Bands
    rolling_std = df['Close'].rolling(5).std()
    df['Bollinger_Upper'] = df['SMA'] + (2 * rolling_std)
    df['Bollinger_Lower'] = df['SMA'] - (2 * rolling_std)

    # VWAP
    df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()

    # EMA
    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()

    # Fibonacci Levels
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
