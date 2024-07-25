# analysis.py
import pandas as pd
from db.database import get_connection
import pandas as pd
import numpy as np

def get_data_from_db(symbol):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM crypto_prices WHERE symbol = '{symbol}'", conn)
    # print(df)
    conn.close()
    return df

def calculate_VI(df, symbol):
    returns = np.log(df / df.shift(1))
    vi = returns.std() * np.sqrt(252)  # Annualizing the standard deviation
    return vi

def calculate_NVT(df, symbol):
    symbol_data = df[df['symbol'] == symbol]
    nvt_ratio = symbol_data['market_cap'] / symbol_data['transaction_volume']
    return nvt_ratio.mean()

def calculate_technical_indicators(df, symbol):
    prices = get_prices(df, symbol)
    prices_series = pd.Series(prices)
    
    sma = prices_series.rolling(window=14).mean()
    ema = prices_series.ewm(span=14, adjust=False).mean()
    
    delta = prices_series.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    exp1 = prices_series.ewm(span=12, adjust=False).mean()
    exp2 = prices_series.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    macdsignal = macd.ewm(span=9, adjust=False).mean()
    macdhist = macd - macdsignal
    # print('sma', sma, 'ema',ema, 'rsi',rsi, 'macd',macd, 'macdsignal',macdsignal, 'macdhist', macdhist)
    
    return sma, ema, rsi, macd, macdsignal, macdhist

def risk_management(df, symbol):
    prices = get_prices(df, symbol)
    prices_series = pd.Series(prices)
    vi = calculate_VI(prices_series, symbol)
    max_loss = prices_series.iloc[-10:].mean() * 0.05  
    stop_loss = max_loss / vi
    return stop_loss

def get_prices(df, symbol):
    symbol_data = df[df['symbol'] == symbol]
    prices = np.array(symbol_data['price'])
    return prices

def get_rsi(df, symbol):
    symbol_data = df[df['symbol'] == symbol]
    prices = np.array(symbol_data['price'], dtype=float)
    rsi = calculate_technical_indicators(pd.Series(prices))[2]
    return rsi

def calculate_position_size(account_balance, risk_per_trade, stop_loss, current_price):
    # print('account_balance',account_balance, 'risk_per_trade',risk_per_trade, 'stop_loss',stop_loss, 'latest_price', current_price)
    risk_amount = account_balance * risk_per_trade
    # print('risk_amount', risk_amount)
    position_size = risk_amount / stop_loss
    return position_size / current_price

def decision_maker(df, symbol, account_balance, risk_per_trade=0.10):
    sma, ema, rsi, macd, macdsignal, macdhist = calculate_technical_indicators(df, symbol)
    
    last_5_rsi_mean = rsi.iloc[-5:].mean()
    last_5_macd_mean = macd.iloc[-5:].mean()
    last_5_macdsignal_mean = macdsignal.iloc[-5:].mean()
    last_5_sma_mean = sma.iloc[-5:].mean()
    last_5_ema_mean = ema.iloc[-5:].mean()

    latest_price = get_prices(df, symbol)[-1]

    # Define weights for each indicator
    rsi_weight = 0.3
    macd_weight = 0.4
    sma_ema_weight = 0.3

    # Calculate confidence scores for buying and selling
    buy_confidence = (
        (last_5_rsi_mean < 30) * rsi_weight +
        (last_5_macd_mean > last_5_macdsignal_mean) * macd_weight +
        ((latest_price > last_5_sma_mean or latest_price > last_5_ema_mean) * sma_ema_weight)
    )
    sell_confidence = (
        (last_5_rsi_mean > 70) * rsi_weight +
        (last_5_macd_mean < last_5_macdsignal_mean) * macd_weight +
        ((latest_price < last_5_sma_mean or latest_price < last_5_ema_mean) * sma_ema_weight)
    )
    
    # Normalize the confidence scores
    buy_confidence = min(buy_confidence, 1)
    sell_confidence = min(sell_confidence, 1)
    
    # Risk management
    stop_loss = risk_management(df, symbol)
    
    # Position size calculation
    
    position_size = calculate_position_size(account_balance, risk_per_trade, stop_loss, latest_price)
    print(position_size)
    
    # Make decision
    if buy_confidence > sell_confidence and buy_confidence > 0.5:
        return "BUY", position_size, buy_confidence
    elif sell_confidence > buy_confidence and sell_confidence > 0.5:
        # Sell a fraction of the position based on confidence
        sell_position_size = (sell_confidence - 0.5) * position_size * 2  # Scale sell position size based on confidence
        return "SELL", sell_position_size, sell_confidence
    else:
        return "HOLD", 0, max(buy_confidence, sell_confidence)