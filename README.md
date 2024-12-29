# Ticker Trade

High-Frequency Trading Bot utilizing the Interactive Brokers (IBKR) Python API.

## Overview

Ticker Trade is a high-frequency trading (HFT) bot designed to execute trades on the Interactive Brokers platform using their Python API. The bot aims to capitalize on short-term market inefficiencies by placing rapid buy and sell orders based on real-time data.

## Features

- **Real-Time Market Data**: Fetches live market data to make informed trading decisions.
- **Automated Trading**: Executes trades automatically based on predefined strategies.
- **Customizable Parameters**: Allows users to adjust trading parameters such as trade size, polling intervals, and price thresholds.
- **Concurrency**: Utilizes threading to handle multiple tasks simultaneously, ensuring efficient performance.

## Installation

1. **Clone the repository**:

```bash
git clone https://github.com/astronights/ticker-trade.git
```

2. **Navigate to the project directory**

```bash
cd ticker-trade
```

3. **Install the required dependencies**

```bash
pip install -r requirements.txt
```

Create a virtual environment if necessary

## Usage

> **NOTE**: The `config.py` and the `trading/algorithm.py` in this section need to be manually created. These are not committed to avoid open sourcing proprietary trading algorithms.

1. **Configure the project**

Ensure that your Interactive Brokers account credentials and desired trading parameters are correctly set in the `config.py`.

Create a `config.py` file as the following

```python
import pytz

TZ_MARKET = pytz.timezone("<market_time_zone>")
TZ_LOCAL = pytz.timezone("<your_time_zone>")

EXCHANGE = 'SMART'
CURRENCY = 'USD'

MARKET_OPEN_TIME = "<trading_start_time (HH:MM)>"
MARKET_CLOSE_TIME = "<trading_start_time (HH:MM)>"

STOCK_SYMBOL = '<ticker_symbol>'

API_PORT = 7497 # 7496 - Live; 7497 - Paper
```

2. **Start IBKR**

Start your instance of the IBKR Trader Workstation or the Gateway program downloaded. Ensure you have the subscriptions to market data enabled and API permissions configured.

3. **Add your trade logic**

Add your trade logic in the `trading/algorithm.py` file. A sample logic would include a loop polling at certain intervals.

```python
import time
import logging

import math
from ib_insync import IB, Stock

from .price_thread import live_average_price, price_lock
from .orders import place_market_order

def run_trade(ib: IB, stock: Stock, opening: dict = None, metrics: dict = None, quantity: int = 0, price: float = 0):
    '''Trade Loop
    
    Args:
        ib (IB): IBKR TWS API Instance
        stock (Stock): IBKR Stock Contract
        opening (dict): Opening prices
        metrics (dict): Other statistics
        quantity (int): Current position quantity (Default: 0)
        price (float): Current position average price (Default: 0)
    '''
    while True:
        # Get Last Traded Price
        ticker = ib.reqMktData(stock, '', False, False)
        ib.sleep(2)
        latest_price = ticker.last
        
        # Get 1 Minute average price
        with price_lock:
            avg_price_live_snapshot = live_average_price

        purchase_quantity = 100
        buy_trade = place_limit_order(ib, stock, 'BUY', purchase_quantity, latest_price)

        time.sleep(5) # Poll interval
```

4. **Run the script**

Run the script with Python.

```bash
python main.py
```

## Project Structure

- `main.py`: The main script to run the trading bot.
- `trading/`: Contains modules related to trading strategies and execution.
- `utils/`: Utility functions and helpers.
- `requirements.txt`: Lists the Python dependencies required for the project.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your proposed changes.

## Disclaimer
This software is for educational and experimental purposes only. Trading in financial markets involves risk. The author is not responsible for any financial losses incurred through the use of this software. Use it at your own risk.