import sys
import time
from datetime import datetime

import logging
import threading

from utils.get_data import get_historical, get_live
from utils.io import append_historical_csv, append_live_csv
from utils.calculate import is_within_market_hours, compute_metrics

import config # Not committed
from ib_insync import IB, Stock
from trading.algorithm import run_trade # Not committed
from trading.price_thread import fetch_live_average_price


dt_today = datetime.now(config.TZ_LOCAL).astimezone(config.TZ_MARKET)

# Logger
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f'logs/trading_log_{dt_today.strftime("%Y-%m-%d")}.txt'),
                        logging.StreamHandler(sys.stdout)
                    ])

# Initialize IB connection
ib = IB()

# Connect to TWS
def connect_to_tws():
    '''Connect to IBKR Trader Workstation (or Gateway)'''
    try:
        # Ensure TWS/IB Gateway is running
        ib.connect('127.0.0.1', config.API_PORT, clientId=1)
        logging.info("Connected to TWS.")
    except Exception as e:
        logging.error(f"Failed to connect to TWS: {e}")
        raise

# Main trading loop
def trading_loop():
    '''Main Trading Loop to Run'''

    stock = Stock(config.STOCK_SYMBOL, config.EXCHANGE, config.CURRENCY)
    ib.qualifyContracts(stock)

    # Fetch historical prices
    hist_data = get_historical(ib, stock, dt_today)
    append_historical_csv(hist_data, 'data/hist.csv')

    opening_prices = None
    metrics = None

    price_updater_thread = threading.Thread(target=fetch_live_average_price, args=(ib, stock), daemon=True)
    price_updater_thread.start()

    try:
        while True:
            dt_now = datetime.now(config.TZ_LOCAL).astimezone(config.TZ_MARKET)

            if not is_within_market_hours(config, dt_now):
                logging.info("Market is closed. Sleeping for 60 seconds.")
                time.sleep(60)
                continue

            # if not opening_prices:
            #     opening_prices = get_live(ib, stock, dt_now, 5)
            #     append_live_csv(opening_prices, 'data/first_five.csv')
            #     metrics = compute_metrics(hist_data, opening_prices)

            # position = [x for x in ib.positions() if x.contract.symbol == config.STOCK_SYMBOL]
            # quantity = position[0].position if position else None
            # price = position[0].position if position else None

            # trade(stock, ib, opening_prices, metrics, quantity, price)
            run_trade(ib, stock)

    except KeyboardInterrupt:
        logging.info("Trading loop interrupted by user.")
    except Exception as e:
        logging.error(f"Error in trading loop: {e}")


# Run the application
if __name__ == '__main__':
    connect_to_tws()
    trading_loop()
    ib.disconnect()
