import pandas as pd
from types import ModuleType
from datetime import datetime

weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

# Check if the current time is within market hours
def is_within_market_hours(config: ModuleType, cur_date: datetime) -> bool:
    '''Check if within market hours
    
    Args:
        config (ModuleType): Configurations
        cur_date (datetime): Current date
        
    Returns:
        is_market_open (bool): If market is open
    '''
    market_open = datetime.strptime(config.MARKET_OPEN_TIME, "%H:%M").time()
    market_close = datetime.strptime(config.MARKET_CLOSE_TIME, "%H:%M").time()
    return market_open <= cur_date.time() <= market_close

def find_weekday_index(col: pd.Series, cur_date: datetime) -> int:
    '''Get index of weekday in historical data
    
    Args:
        col (pd.Series): Column of dates
        cur_date (datetime): Current date
        
    Returns:
        ix (int): Index of row
    '''
    today_weekday = cur_date.strftime('%A')

    if today_weekday in col.values:
        return col[col == today_weekday].index[-1]
    
    for i in range(len(col) - 1, -1, -1):
        current_day = col.iloc[i]
        next_day = col.iloc[i + 1]
        
        # Find missing index if weekday was holiday in previous week
        if weekdays.index(current_day) + 1 < weekdays.index(next_day):
            missing_weekday = weekdays[weekdays.index(current_day) + 1]
            if missing_weekday == today_weekday:
                return i + 1 
    
    return None

def compute_metrics(hist_df: pd.DataFrame, live_dict: dict) -> dict:
    '''Compute Metrics from Historical and Live data
    
    Args:
        hist_df (pd.DataFrame): Historical Data
        live_dict (dict): Live data
        
    Returns:
        metrics (dict): Metrics
    '''
    overnight_pct = None
    vwap_ret = None

    if (prev_ix := find_weekday_index(hist_df['day_of_week'])):
        last_week = hist_df.iloc[:prev_ix + 1]

        overnight_pct = last_week.iloc[-1]['open'] / last_week.iloc[-2]['close']
        vwap_ret = last_week.iloc[-1]['average'] / last_week.iloc[-2]['average']

    avg_price = sum(hist_df['average'] * hist_df['volume']) / sum(hist_df['volume'])
    today_pct = live_dict['open'] / hist_df.iloc[-1]['close']

    return {'last_week_overnight_pct': round(overnight_pct, 2), 
            'today_overnight_pct': round(today_pct, 2),
            'last_week_vwap_ret': round(vwap_ret, 2),
            'hist_vwap': round(avg_price, 2)}    

    