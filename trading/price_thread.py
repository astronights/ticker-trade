import logging
from datetime import datetime, timedelta

import asyncio
from threading import Lock

from ib_insync import IB, Stock

live_average_price = None
price_lock = Lock()

async def _calculate_live_average_price(ib: IB, stock: Stock, seconds: int = 60) -> float:
    '''Calculate the volume-weighted average price (VWAP) over the last minute.
    
    Args:
        ib (IB): IBKR TWS API Instance
        stock (Stock): IBKR Stock Contract
        seconds (int): Number of seconds (Default: 60)

    Returns:
        avg_price (float): Stock VWAP
    '''
    try:
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=seconds)

        total_price_volume = 0
        total_volume = 0

        def on_tick_data(tick_data):
            '''Update price and volume on tick'''
            nonlocal total_price_volume, total_volume
            if tick_data.last is not None and tick_data.lastSize is not None:
                total_price_volume += tick_data.last * tick_data.lastSize
                total_volume += tick_data.lastSize

        ticker = ib.reqMktData(stock, '', False, False)
        ticker.updateEvent += on_tick_data

        while datetime.now() < end_time:
            await asyncio.sleep(0.5)

        ib.cancelMktData(stock)

        if total_volume > 0:
            average_price = total_price_volume / total_volume
            logging.info(f"{seconds} second VWAP calculated: {average_price:.2f}")
            return round(average_price, 2)
        else:
            logging.warning("No trades occurred in the last minute.")
            return None

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
    global live_average_price
    while True:
        try:
            avg_price = await _calculate_live_average_price(ib, stock)
            with price_lock:
                live_average_price = avg_price
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
