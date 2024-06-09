from strategies import strategy
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

def main():
    while True:
        strategy.execute_okx_strategy()
        strategy.execute_binance_strategy()
        print("done")
        #time.sleep(10*60)
    
if __name__ == "__main__":
    main()
