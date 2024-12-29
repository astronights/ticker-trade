import pandas as pd 
from ib_insync import IB, Stock, util

import logging
from datetime import datetime, timedelta

cols = ['date', 'day_of_week', 'open', 'high', 'low', 'close', 'volume', 'average', 'barCount']

def get_historical(ib: IB, stock: Stock, cur_date: datetime, n_days: int = 6) -> pd.DataFrame:
    '''Get Historical data
    
    Args:
        ib (IB): IBKR TWS API Instance
        stock (Stock): IBKR Stock Contract
        cur_date (datetime): Current Date
        n_days (int): Trading days to look back (Default: 6)

    Returns:
        df (pd.DataFrame): OHLCV prices of past week
    '''
    try:
        end_date = cur_date - timedelta(days=1)
        end_date_str = end_date.strftime('%Y%m%d %H:%M:%S') + f' {cur_date.tzinfo.zone}'

        bars = ib.reqHistoricalData(stock, endDateTime=end_date_str, durationStr=f'{n_days} D',
                                    barSizeSetting='1 day', whatToShow='TRADES', useRTH=True)
        df = util.df(bars)
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.day_name()

        logging.info(f"Fetched historical data {min(df.date)} - {max(df.date)}")
        return df[cols]
    
    except Exception as e:
        logging.error(f"Error fetching historical data: {e}")
        raise

def get_live(ib: IB, stock: Stock, cur_date: datetime, n_mins: int = 5) -> dict:
    '''Get Live Data
    
    Args:
        ib (IB): IBKR TWS API Instance
        stock (Stock): IBKR Stock Contract
        cur_date (datetime): Current Date
        n_mins (int): Trading window to summarize in minutes (Default: 5)

    Returns:
        live_prices (dict): Summary of live prices
    '''
    try:
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=n_mins)

        ohlcv = {
            # 'open': None,
            # 'close': None,
            'high': float('-inf'),
            'low': float('inf'),
            'volume': 0,
            'weighted_price_volume': 0,
        }

        def on_tick_data(tick_data):
            '''Callback function to process tick data'''
            nonlocal ohlcv

            if tick_data.last is not None:
                price = tick_data.last
                volume = tick_data.lastSize or 0

                ohlcv['open'] = ohlcv.get('open', price)
                ohlcv['close'] = price

                ohlcv['high'] = max(ohlcv['high'], price)
                ohlcv['low'] = min(ohlcv['low'], price)
                
                ohlcv['volume'] += volume
                ohlcv['weighted_price_volume'] += price * volume

        # Subscribe to market data
        ticker = ib.reqMktData(stock, '', False, False)
        ticker.updateEvent += on_tick_data

        # Wait for the specified time window
        while datetime.now() < end_time:
            ib.sleep(1)

        # Unsubscribe from market data
        ib.cancelMktData(stock)

        # Calculate average price
        average_price = (
            ohlcv['weighted_price_volume'] / ohlcv['volume'] if ohlcv['volume'] > 0 else None
        )

        live_prices = {
            'date': start_time.strftime('%Y-%m-%d'),
            'day_of_week': start_time.strftime('%A'),
            'start_time': start_time.strftime('%H:%M:%S'),
            'end_time': end_time.strftime('%H:%M:%S'),
            'open': round(ohlcv['open'], 2),
            'high': round(ohlcv['high'], 2),
            'low': round(ohlcv['low'], 2),
            'close': round(ohlcv['close'], 2),
            'volume': round(ohlcv['volume'], 2),
            'average': round(average_price, 2),
        }

        logging.info(f"Fetched recent {n_mins} minutes of OHLCV data: {live_prices}")
        return live_prices

    except Exception as e:
        logging.error(f"Error fetching recent 5 minutes data: {e}")
        raise