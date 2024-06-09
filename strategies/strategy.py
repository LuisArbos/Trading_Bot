from okx_files import okx_functions as f
from binance_files import binance_functions as bf

STOP_LOSS_PERCENTAGE = 0.05  

def execute_okx_strategy():
    crypto_pairs = f.get_available_trading_pairs()
    live_crypto_pairs = f.filter_live_trading_pairs(crypto_pairs, "DEMO")
    print("Executing my OKX strategy:")

    for pair_info in live_crypto_pairs:
        pair = pair_info['instId']
        base_currency = pair.split("-")[0]
        quote_currency = pair.split("-")[1]
        acc_balance = f.get_acc_balance()
        
        if base_currency in acc_balance or quote_currency in acc_balance:
            try:
                last_signal = f.get_last_signal(pair)
                match last_signal:
                    case "buy":
                        print(f"{pair} - Buy Signal")
                        for coin, balance_str in acc_balance.items():
                            balance = float(balance_str)
                            if quote_currency in coin:
                                f.buy(pair, balance * 0.1)
                                # Registrar precio de compra para stop-loss
                                purchase_price = f.get_current_price(pair)
                                f.register_stop_loss(pair, purchase_price * (1 - STOP_LOSS_PERCENTAGE))

                    case "sell":
                        print(f"{pair} - Sell Signal")
                        for coin, balance_str in acc_balance.items():
                            balance = float(balance_str)
                            if coin in pair:
                                f.sell(pair, balance)

                # Verificar y ejecutar stop-loss
                stop_loss_price = f.get_stop_loss_price(pair)
                if stop_loss_price and f.get_current_price(pair) <= stop_loss_price:
                    print(f"{pair} - Triggering Stop-Loss")
                    f.sell(pair, f.get_balance(pair.split("-")[0]))

            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error processing {pair}: {e}")

def execute_binance_strategy():
    crypto_pairs = bf.get_available_trading_pairs()
    print("Executing my Binance strategy:")
    acc_balance = bf.get_acc_balance()
    acc_balance_currencies = [balance['asset'] for balance in acc_balance]

    for pair in crypto_pairs.items():
        symbol = pair[0]
        base_currency = pair[1]['baseAsset']
        quote_currency = pair[1]['quoteAsset']
        if base_currency in acc_balance_currencies or quote_currency in acc_balance_currencies:
            try:
                print(f"Fetching signals for {symbol}")
                last_signal = bf.get_last_signal(symbol)
                match last_signal:
                    case "buy":
                        for coin, balance_str in acc_balance.items():
                            balance = float(balance_str)
                            if quote_currency in coin:
                                print(f"This is a buy signal for {symbol}")
                                bf.buy(symbol, balance * 0.1)
                                # Registrar precio de compra para stop-loss
                                purchase_price = bf.get_current_price(symbol)
                                bf.register_stop_loss(symbol, purchase_price * (1 - STOP_LOSS_PERCENTAGE))

                    case "sell":
                        for coin, balance_str in acc_balance.items():
                            balance = float(balance_str)
                            if coin in pair:
                                print(f"This is a sell signal for {symbol}")
                                bf.sell(symbol, balance)

                # Verificar y ejecutar stop-loss
                stop_loss_price = bf.get_stop_loss_price(symbol)
                if stop_loss_price and bf.get_current_price(symbol) <= stop_loss_price:
                    print(f"{symbol} - Triggering Stop-Loss")
                    bf.sell(symbol, bf.get_balance(symbol.split("-")[0]))

            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error processing {pair}: {e}")

