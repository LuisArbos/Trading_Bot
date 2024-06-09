import requests
import pandas as pd
import sys, os
import ta
import json
from ta.utils import dropna
from dotenv import load_dotenv

import okx.Trade as Trade
import okx.PublicData as PublicData
import okx.Account as Account

stop_loss_prices = {}
flag = "1"  # live trading: 0, demo trading: 1
credentials = {}
DEMO_PAIRS = ["AGIX-EUR", "FET-EUR", "XRP-EUR", "APT-EUR", "TON-EUR", "MATIC-EUR", "ICP-EUR", "IMX-EUR", "ATOM-EUR", "AGIX-TRY", "QTUM-USDC", "KLAY-USDC", "BTM-USDC", "BSV-USDC", "LQTY-USDC", "DYDX-USDC", "ARB-USDC", "SPELL-USDC", "INJ-USDC", "CRV-USDC", "TIA-USDC", "COMPI-USDC", "WIF-USDC", "FET-USDC", "RACA-USDC", "NEAR-USDC", "CFX-USDC", "FLOKU-USDC", "AGIX-USDC", "RNDR-USDC", "MKR-USDC", "UNI-USDC", "XLM-USDC", "USDT-USDC", "ETC-USDC", "ALGO-USDC", "TRX-USDC", "AAVE-USDC", "ADA-USDC", "ETHW-USDC", "APT-USDC", "ATOM-USDC", "LINK-USDC", "FTM-USDC", "DOT-USDC", "BCH-USDC", "AVAX-USDC", "SHIB-USDC", "TON-USDC", "XRP-USDC", "FIL-USDC", "MATIC-USDC", "DOGE-USDC", "LTC-USDC", "SOL-USDC", "ETH-USDC", "BTC-USDC"]
REAL_PAIRS = ["BTC-EUR", "ETH-EUR", "MATIC-EUR", "XRP-EUR", "SOL-EUR", "DOGE-EUR", "TON-EUR", "1INCH-EUR", "AAVE-EUR", "ADA-EUR", "ALGO-EUR", "APE-EUR", "APT-EUR", "ARB-EUR", "ASTR-EUR", "ATOM-EUR", "AVAX-EUR", "AXS-EUR", "BAL-EUR", "BAT-EUR", "CHZ-EUR", "COMP-EUR", "CRO-EUR", "CRV-EUR", "DOT-EUR", "DYDX-EUR", "EGLD-EUR", "EOS-EUR", "FET-EUR", "FLOW-EUR", "FLR-EUR", "FTM-EUR", "FXS-EUR", "GAL-EUR", "GRT-EUR", "HBAR-EUR", "ICP-EUR", "IMX-EUR", "INJ-EUR", "JTO-EUR", "LDO-EUR", "LINK-EUR", "LTC-EUR", "LUNC-EUR", "MANA-EUR", "MINA-EUR", "MKR-EUR", "OP-EUR", "SAND-EUR", "SHIB-EUR", "SNX-EUR", "STX-EUR", "SUI-EUR", "SUSHI-EUR", "TRX-EUR", "UNI-EUR", "USDT-EUR", "USDC-EUR", "WIF-EUR", "WOO-EUR", "XLM-EUR", "XTZ-EUR", "YGG-EUR", "BTC-USDC", "ETH-USDC", "MATIC-USDC", "XRP-USDC", "SOL-USDC", "DOGE-USDC", "TON-USDC", "AAVE-USDC", "ACE-USDC", "ADA-USDC", "AGIX-USDC", "AGLD-USDC", "ALGO-USDC", "APE-USDC", "APT-USDC", "AR-USDC", "ASTR-USDC", "ATOM-USDC", "AUCTION-USDC", "AVAX-USDC", "BCH-USDC", "BLUR-USDC", "BNB-USDC", "BSV-USDC", "CETUS-USDC", "CFX-USDC", "CHZ-USDC", "COMP-USDC", "CRO-USDC", "CRV-USDC", "CSPR-USDC", "CTXC-USDC", "DOT-USDC", "DYDX-USDC", "EGLD-USDC", "EOS-USDC", "ETC-USDC", "ETHW-USDC", "FIL-USDC", "FLOKI-USDC", "FLR-USDC", "FLR-USDC", "FTM-USDC", "GALA-USDC", "GLM-USDC", "GRT-USDC", "HBAR-USDC", "ICP-USDC", "IOTA-USDC", "JTO-USDC", "KDA-USDC", "KLAY-USDC", "LINK-USDC", "LOOKS-USDC", "LRC-USDC", "LTC-USDC", "LUNA-USDC", "MAGIC-USDC", "MANA-USDC", "MASK-USDC", "METIS-USDC", "MINA-USDC", "MKR-USDC", "NEAR-USDC", "NEO-USDC", "OM-USDC", "OP-USDC", "ORDI-USDC", "RON-USDC", "RPL-USDC", "RVN-USDC", "SAND-USDC", "SHIB-USDC", "SNX-USDC", "STORJ-USDC", "STRK-USDC", "STX-USDC", "SUI-USDC", "SUSHI-USDC", "SWEAT-USDC", "TRX-USDC", "UNI-USDC", "USDT-USDC", "VELO-USDC", "VENOM-USDC", "WAXP-USDC", "WIF-USDC", "XLM-USDC", "ZIL-USDC"]

#Load cretentials from env file.
load_dotenv("credentials.env")
credentials['API_KEY_DEMO'] = os.getenv('API_OKX_API_KEY_DEMO')
credentials['SECRET_KEY_DEMO'] = os.getenv('API_OKX_SECRET_KEY_DEMO')
credentials['PASSPHRASE'] = os.getenv('API_OKX_PASSPHRASE')

credentials['API_KEY_REAL'] = os.getenv('API_OKX_API_KEY_REAL')
credentials['SECRET_KEY_REAL'] = os.getenv('API_OKX_SECRET_KEY_REAL')

def get_acc_balance():
    if flag == "1":
        accountAPI = Account.AccountAPI(credentials['API_KEY_DEMO'], credentials['SECRET_KEY_DEMO'], credentials['PASSPHRASE'], False,  flag)
    else:
        accountAPI = Account.AccountAPI(credentials['API_KEY_REAL'], credentials['SECRET_KEY_REAL'], credentials['PASSPHRASE'], False,  flag)
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    result = accountAPI.get_account_balance()
    sys.stdout = original_stdout
    balances = result['data'][0]['details']
    balance_dict = {}

    for balance in balances:
        currency = balance['ccy']
        available_balance = balance['availBal']
        balance_dict[currency] = available_balance
    return balance_dict

def get_available_trading_pairs():
    PublicDataAPI = PublicData.PublicAPI(flag=flag)
    resultPublicData = PublicDataAPI.get_instruments(instType="SPOT")
    if 'data' in resultPublicData:
        live_pairs = [pair for pair in resultPublicData['data'] if pair.get('state') == 'live']
        return live_pairs
    else:
        return []

def filter_live_trading_pairs(pairs, flag):
    if flag == "DEMO":
        return [pair for pair in pairs if pair['instId'] in DEMO_PAIRS]
    elif flag == "REAL":
        return [pair for pair in pairs if pair['instId'] in REAL_PAIRS]
    else:
        print("There is no valid flag in the filter_live_trading_pairs function")
        return []

def get_okx_kline_data(symbol, interval, limit=100):
    base_url="https://www.okx.com/api/v5/market/candles"
    params={
        "instId":symbol,
        "bar":interval,
        "limit":limit
    }
    try:
        response = requests.get(base_url,params=params)
        response.raise_for_status()
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Failed to fetch data for {symbol}: {e}")
        return None

def get_current_price(symbol):
    kline_data = get_okx_kline_data(symbol, '1m', 1)
    if kline_data is not None and len(kline_data.json()['data']) > 0:
        return float(kline_data.json()['data'][0][4])
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
    df =  pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "u1", "u2", "u3"])
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

def get_signals_for_pair(pair, interval="1m", limit=100):
    response = get_okx_kline_data(pair, interval, limit)
    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Failed to fetch data for {pair}")
        return None
    raw_data = data["data"]
    df = process_data(raw_data)
    df_with_indicators = add_indicators(df)
    df_with_signals = generate_signals(df_with_indicators)
    return df_with_signals[["timestamp","close","buy_signal","sell_signal"]]

def get_last_signal(pair):
    signals = get_signals_for_pair(pair)
    if signals is None or signals.empty:
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

    else:
        return "hold"

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
def buy(pair, amount):
    balance = get_acc_balance()
    base_currency = pair.split("-")[0]
    quote_currency = pair.split("-")[1]

    if quote_currency in balance and float(balance[quote_currency]) >= amount:
        if flag == "1":
            tradeAPI = Trade.TradeAPI(credentials['API_KEY_DEMO'], credentials['SECRET_KEY_DEMO'], credentials['PASSPHRASE'], False,  flag)
        else:
            tradeAPI = Trade.TradeAPI(credentials['API_KEY_REAL'], credentials['SECRET_KEY_REAL'], credentials['PASSPHRASE'], False,  flag)
        tradeAPI.place_order(
            instId=pair,
            tdMode="cash",
            side="buy",
            ordType="market",
            sz=amount,
        )
        print(f"Bought {base_currency} at market price")
    else:
        print(f"Insufficient {quote_currency} to execute buy order")

def sell(pair, amount):
    balance = get_acc_balance()
    base_currency = pair.split("-")[0]
    quote_currency = pair.split("-")[1]

    if base_currency in balance and float(balance[base_currency]) >= amount:
        if flag == "1":
            tradeAPI = Trade.TradeAPI(credentials['API_KEY_DEMO'], credentials['SECRET_KEY_DEMO'], credentials['PASSPHRASE'], False,  flag)
        else:
            tradeAPI = Trade.TradeAPI(credentials['API_KEY_REAL'], credentials['SECRET_KEY_REAL'], credentials['PASSPHRASE'], False,  flag)

        tradeAPI.place_order(
            instId=pair,
            tdMode="cash",
            side="sell",
            ordType="market",
            sz=amount,
        )
        print(f"Sold {amount} {base_currency} at market price")
    else:
        print(f"Insufficient {base_currency} to execute sell order")

