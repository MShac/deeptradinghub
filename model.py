import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Detect local support and resistance levels
def find_support_resistance(df, window=20):
    support = []
    resistance = []
    for i in range(window, len(df) - window):
        is_support = all(df['Low'][i] < df['Low'][i - j] and df['Low'][i] < df['Low'][i + j] for j in range(1, window))
        is_resistance = all(df['High'][i] > df['High'][i - j] and df['High'][i] > df['High'][i + j] for j in range(1, window))
        if is_support:
            support.append(df['Low'][i])
        if is_resistance:
            resistance.append(df['High'][i])
    return sorted(set(support)), sorted(set(resistance))

# Exponential Moving Average
def calculate_ema(df, window=9):
    return df['Close'].ewm(span=window, adjust=False).mean()

# Nearest level from current price
def get_nearest_level(price, levels, direction="support"):
    if levels is None or not isinstance(levels, (list, np.ndarray)) or len(levels) == 0:
        return price  # fallback if levels list is empty or invalid

    levels = sorted(levels)
    if direction == "support":
        levels_below = [lvl for lvl in levels if lvl < price]
        return levels_below[-1] if levels_below else price
    else:
        levels_above = [lvl for lvl in levels if lvl > price]
        return levels_above[0] if levels_above else price * 1.005  # fallback 0.5% higher

# Train the model
def train_model(df):
    if df.empty or len(df) < 50:
        return None, None

    df = df.dropna()

    # Indicators
    df['EMA_9'] = calculate_ema(df, 9)
    df['EMA_21'] = calculate_ema(df, 21)

    features = ['SMA', 'MACD', 'ATR', 'VWAP', 'Bollinger_Upper', 'Bollinger_Lower', 'EMA_9', 'EMA_21']
    if not all(f in df.columns for f in features):
        return None, None

    # Target label
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)

    # Balance dataset
    min_count = df['Target'].value_counts().min()
    df_buy = df[df['Target'] == 1].sample(min_count, random_state=42)
    df_sell = df[df['Target'] == 0].sample(min_count, random_state=42)
    df_balanced = pd.concat([df_buy, df_sell]).sample(frac=1, random_state=42)

    X = df_balanced[features]
    y = df_balanced['Target']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    return model, scaler

# Predict signal + entry + SL/TP
def predict_trade(df, model, scaler, support, resistance):
    if df.empty or 'Close' not in df.columns:
        return "No Data", None, None

    # Ensure EMA exists
    if 'EMA_9' not in df.columns:
        df['EMA_9'] = calculate_ema(df, 9)
    if 'EMA_21' not in df.columns:
        df['EMA_21'] = calculate_ema(df, 21)

    # Feature columns
    feature_columns = ['SMA', 'MACD', 'ATR', 'VWAP', 'Bollinger_Upper', 'Bollinger_Lower', 'EMA_9', 'EMA_21']
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0  # fallback

    # Prepare latest data
    latest_data = df[feature_columns].tail(1).fillna(0)
    scaled_input = scaler.transform(latest_data)
    prediction = model.predict(scaled_input)[0]

    current_price = df['Close'].iloc[-1]

    # Validate resistance/support
    if resistance is not None and resistance <= current_price:
        resistance = current_price * 1.005  # fallback 0.5% higher
    if support is not None and support >= current_price:
        support = current_price * 0.995  # fallback 0.5% lower

    # ATR filter to avoid whipsaw
    atr_threshold = df['ATR'].iloc[-1] * 1.5  # example factor
    if df['ATR'].iloc[-1] > atr_threshold:
        return "No Trade", None, None

    # Determine entry price
    if prediction == 1:  # Buy
        entry_price = get_nearest_level(current_price, support, direction="support")
        if entry_price > current_price:
            entry_price = current_price
    else:  # Sell
        entry_price = get_nearest_level(current_price, resistance, direction="resistance")
        if entry_price < current_price:
            entry_price = current_price

    # Determine SL/TP
    if support is not None and resistance is not None:
        if prediction == 1:
            stop_loss = support
            take_profit = resistance
        else:
            stop_loss = resistance
            take_profit = support
    else:
        stop_loss = entry_price * 0.98
        take_profit = entry_price * 1.02

    return ("Buy" if prediction == 1 else "Sell"), entry_price, (stop_loss, take_profit)
