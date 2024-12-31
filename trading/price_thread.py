import logging
from datetime import datetime, timedelta

import asyncio
from threading import Lock

import statistics
from ib_insync import IB, Stock

live_average_price = None
live_volatility = None
price_lock = Lock()

async def _calculate_live_average_price(ib: IB, stock: Stock, seconds: int = 60) -> tuple:
    '''Calculate the volume-weighted average price (VWAP) over the last minute.
    
    Args:
        ib (IB): IBKR TWS API Instance
        stock (Stock): IBKR Stock Contract
        seconds (int): Number of seconds (Default: 60)

    Returns:
        avg_price (float): Stock VWAP
        volatility (float): Standard deviation of prices
    '''
    try:
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=seconds)

        total_price_volume = 0
        total_volume = 0
        prices = []

        def on_tick_data(tick_data):
            '''Update price and volume on tick'''
            nonlocal total_price_volume, total_volume, prices

            if tick_data.last is not None and tick_data.lastSize is not None:
                cur_price = tick_data.last
                cur_volume = tick_data.lastSize

                prices.append(cur_price)

                total_volume += cur_volume
                total_price_volume += cur_price * cur_volume

        ticker = ib.reqMktData(stock, '', False, False)
        ticker.updateEvent += on_tick_data

        while datetime.now() < end_time:
            await asyncio.sleep(0.5)

        ib.cancelMktData(stock)

        if total_volume > 0:
            average_price = total_price_volume / total_volume
            volatility = statistics.stdev(prices) if len(prices) > 1 else 0.0
            logging.info(f"{seconds} second VWAP: {average_price:.2f}, Volatility: {volatility:.2f}")
            return (round(average_price, 2), round(volatility, 2))
        else:
            logging.warning("No trades occurred in the last minute.")
            return (None, None)

    except Exception as e:
        logging.error(f"Error calculating {seconds} second average price: {e}")
        raise

async def _price_updater_loop(ib: IB, stock: Stock, seconds: int = 60):
    '''Loop to calculate the volume-weighted average price (VWAP) over the last minute.
    
    Args:
        ib (IB): IBKR TWS API Instance
        stock (Stock): IBKR Stock Contract
        seconds (int): Number of seconds (Default: 60)
    '''
    global live_average_price, live_volatility
    while True:
        try:
            avg_price, volatility = await _calculate_live_average_price(ib, stock)
            with price_lock:
                live_average_price = avg_price
                live_volatility = volatility
        except Exception as e:
            logging.error(f"Error updating {seconds} second average price: {e}")

def fetch_live_average_price(ib: IB, stock: Stock, seconds: int = 60):
    '''Async runner to calculate the volume-weighted average price (VWAP) over the last minute.
    
    Args:
        ib (IB): IBKR TWS API Instance
        stock (Stock): IBKR Stock Contract
        seconds (int): Number of seconds (Default: 60)
    '''
    asyncio.run(_price_updater_loop(ib, stock))
