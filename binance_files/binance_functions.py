import requests
import pandas as pd
import sys, os
import ta
import json
from ta.utils import dropna
from dotenv import load_dotenv

from binance.spot import Spot
from binance.client import Client as BinanceClient

stop_loss_prices = {}
flag = "1"  # live trading: 0, demo trading: 1
credentials = {}

#Load cretentials from env file.
load_dotenv("credentials.env")
credentials['API_KEY'] = os.getenv('API_BINANCE_API_KEY')
credentials['SECRET_KEY'] = os.getenv('API_BINANCE_SECRET_KEY')

client = Spot(api_key=credentials['API_KEY'], api_secret=credentials['SECRET_KEY'])
#print(client.account())

def get_acc_balance():
    balance_dict = {}
    for item in client.account()['balances']:
        coin = item['asset']
        free = item['free']
        #locked = item['locked'] #Not necessary right now
        if float(free) != 0:
            balance_dict[coin] = free    
    return balance_dict

def get_available_trading_pairs():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(url)

    if response.status_code == 200:
        exchange_info = response.json()
        crypto_pairs = {}
        for item in exchange_info['symbols']:
            if "SPOT" in item['permissionSets'][0]:
                crypto_pairs[item['symbol']] = {"baseAsset": item['baseAsset'], "quoteAsset": item['quoteAsset']}
        return crypto_pairs
    else:
        print("Request failed with status code:", response.status_code)
        return None

def get_binance_kline_data(symbol, interval, limit=1000):
    url="https://api.binance.com/api/v3/klines"
    params={
        "symbol":symbol,
        "interval":interval,
        "limit":limit
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to fetch kline data:", response.status_code)
        return None

def get_current_price(symbol):
    kline_data = get_binance_kline_data(symbol, '1m', 1)
    if kline_data is not None and len(kline_data) > 0:
        return float(kline_data[0][4])
    return None

def register_stop_loss(symbol, stop_loss_price):
    stop_loss_prices[symbol] = stop_loss_price

def get_stop_loss_price(symbol):
    return stop_loss_prices.get(symbol, None)

def get_balance(currency):
    balance = get_acc_balance()
    return float(balance.get(currency, 0))

#DATA FUNCTIONS:
def process_data(data):
    df =  pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"]= pd.to_datetime(df["timestamp"], unit="ms")

    #Convert columns to numeric data types
    for col in ["open", "high", "low", "close", "volume"]:
        df[col]=pd.to_numeric(df[col], errors='coerce')

    #Clean NaN values
    df = dropna(df)

    #Add all ta features
    #df = add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume")
    df = add_indicators(df)

    #Keep only the columns we're interested in
    # old version df = df[["timestamp", "open", "high", "low", "close", "volume", "momentum_rsi", "volatility_bbh", "volatility_bbl", "trend_macd", "trend_macd_signal", "trend_macd_diff"]]
    df = df[["timestamp", "open", "high", "low", "close", "volume", "rsi", "bb_high", "bb_low", "macd", "macd_signal", "macd_diff"]]      
    return df

def add_indicators(df):
    #RSI
    df["rsi"] = ta.momentum.RSIIndicator(close=df["close"], window=14, fillna=True).rsi()

    #Bollinger Bands
    bb = ta.volatility.BollingerBands(close=df["close"], window=20)
    df["bb_high"] = bb.bollinger_hband()
    df["bb_low"] = bb.bollinger_lband()

    #MACD
    macd=ta.trend.MACD(close=df["close"], window_slow=26, window_fast=12, window_sign=9)
    df["macd"]=macd.macd()
    df["macd_signal"]=macd.macd_signal()
    df["macd_diff"]=macd.macd_diff()

    #print(df)
    return df

#SIGNAL FUNCTIONS:
def generate_signals(df):
    df=df.reset_index(drop=True)

    #Initialize the variables
    df['buy_signal']=False
    df['sell_signal']=False

    #Buy when MACD crosses above the MACD signal and RSI is below 30 (oversold), and price touches lower Bollinger Band
    #Sell when MACD crosses below the MACD signal and RSI is above 70 (overbought), and price touches upper Bollinger Band
    for i in range(1, len(df)):
        if(df['macd'][i]> df['macd_signal'][i]) and (df['macd'][i-1] <= df['macd_signal'][i-1]) and (df['rsi'][i]<30) and (df['close'][i]<=df['bb_low'][i]):
            df.at[i, 'buy_signal'] = True
        elif (df['macd'][i] < df['macd_signal'][i]) and (df['macd'][i-1] >= df['macd_signal'][i-1]) and (df['rsi'][i]>70) and (df['close'][i] >= df['bb_high'][i]):
            df.at[i, 'sell_signal'] = True
    return df

def get_signals_for_pair(symbol, interval="1m", limit=1000):
    response = get_binance_kline_data(symbol, interval, limit)
    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Failed to fetch data for {symbol}")
        return None
    
    if isinstance(data, list) and all(isinstance(item, list) for item in data):
        raw_data = [item[:6] for item in data]
    else:
        print(f"Unexpected data format for {symbol}")
        return None
    df = process_data(raw_data)
    df_with_indicators = add_indicators(df)
    df_with_signals = generate_signals(df_with_indicators)
    return df_with_signals[["timestamp","close","buy_signal","sell_signal"]]

def get_last_signal(symbol):
    signals = get_signals_for_pair(symbol)
    if signals is None or len(signals) == 0:
        return "hold"

    buy_signals = signals[signals["buy_signal"]]
    sell_signals = signals[signals["sell_signal"]]

    if not buy_signals.empty and not sell_signals.empty:
        last_buy_signal_index = buy_signals.index[-1]
        last_sell_signal_index = sell_signals.index[-1]
        if last_buy_signal_index > last_sell_signal_index:
            return "buy"
        else:
            return "sell"
    elif not buy_signals.empty:
        return "buy"
    elif not sell_signals.empty:
        return "sell"

def plot(df):
    import matplotlib.pyplot as plt

    fig, ax1 = plt.subplots(figsize = (12, 8))

    ax1.plot(df["timestamp"], df["close"], label = "Close", alpha = 0.35)
    ax1.plot(df["timestamp"], df["bb_high"], label = "Bollinger High", alpha = 0.35)
    ax1.plot(df["timestamp"], df["bb_low"], label = "Bollinger Low", alpha = 0.35)

    ax1.set_title("BTC-USDC Trading Signals")
    ax1.set_xlabel("Timestamp")
    ax1.set_ylabel("Close Price (USDc)")
    plt.xticks(rotation=450)
    plt.show()

#BUY/SELL FUNCTIONS
def buy(symbol, amount):
    client = BinanceClient(api_key=credentials['API_KEY'], api_secret=credentials['SECRET_KEY'])
    base_currency = symbol.split("-")[0]
    quote_currency = symbol.split("-")[1]

    # Check if the quote currency balance is sufficient
    balance = get_acc_balance()
    if quote_currency in balance and float(balance[quote_currency]) >= amount:
        # Place a market buy order
        try:
            order = client.create_order(
                symbol=symbol,
                side="BUY",
                type="MARKET",
                quantity=amount
            )
            print(f"Successfully bought {base_currency} at market price")
        except Exception as e:
            print(f"Failed to execute buy order: {e}")
    else:
        print(f"Insufficient {quote_currency} balance to execute buy order")

def sell(symbol, amount):
    client = BinanceClient(api_key=credentials['API_KEY'], api_secret=credentials['SECRET_KEY'])
    base_currency = symbol.split("-")[0]
    quote_currency = symbol.split("-")[1]

    # Check if the base currency balance is sufficient
    balance = get_acc_balance()
    if base_currency in balance and float(balance[base_currency]) >= amount:
        # Place a market sell order
        try:
            order = client.create_order(
                symbol=symbol,
                side="SELL",
                type="MARKET",
                quantity=amount
            )
            print(f"Successfully sold {amount} {base_currency} at market price")
        except Exception as e:
            print(f"Failed to execute sell order: {e}")
    else:
        print(f"Insufficient {base_currency} balance to execute sell order")

