def explain_trade(df, prediction, confidence):
    explanation = []
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Confidence
    explanation.append(f"Model confidence: **{confidence*100:.2f}%**")

    # EMA Crossover
    if last['EMA_9'] > last['EMA_21'] and prev['EMA_9'] < prev['EMA_21']:
        explanation.append("📈 **Bullish EMA Crossover** detected (EMA 9 crossed above EMA 21)")
    elif last['EMA_9'] < last['EMA_21'] and prev['EMA_9'] > prev['EMA_21']:
        explanation.append("📉 **Bearish EMA Crossover** detected (EMA 9 crossed below EMA 21)")

    # MACD
    explanation.append(f"MACD value: `{last['MACD']:.4f}` - " +
        ("Bullish" if last['MACD'] > 0 else "Bearish"))

    # Bollinger Bands
    if last['Close'] > last['Bollinger_Upper']:
        explanation.append("🚀 Price broke **above** upper Bollinger Band → possible breakout")
    elif last['Close'] < last['Bollinger_Lower']:
        explanation.append("⚠️ Price fell **below** lower Bollinger Band → possible breakdown")

    # VWAP position
    if last['Close'] > last['VWAP']:
        explanation.append("💡 Price is **above VWAP** (bullish)")
    else:
        explanation.append("🔻 Price is **below VWAP** (bearish)")

    # Support/Resistance
    if 'Support' in df.columns and 'Resistance' in df.columns:
        support = last['Support']
        resistance = last['Resistance']
        if abs(last['Close'] - support) / last['Close'] < 0.01:
            explanation.append(f"🛡️ Price is **near support** (${support:.2f})")
        elif abs(last['Close'] - resistance) / last['Close'] < 0.01:
            explanation.append(f"🔼 Price is **near resistance** (${resistance:.2f})")

    return explanation
