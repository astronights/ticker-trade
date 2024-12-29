import os
import logging
import pandas as pd

def append_historical_csv(ohlcv: pd.DataFrame, fpath: str):
    '''Append Historical Data to CSV
    
    Args:
        ohlcv (pd.DataFrame): OHLCV Data
        fpath (str): File Path
    '''
    try:
        existing_data = pd.read_csv(fpath)
    except FileNotFoundError:
        existing_data = pd.DataFrame()
    
    ohlcv['date'] = pd.to_datetime(ohlcv['date'])
    
    if not existing_data.empty:
        existing_data['date'] = pd.to_datetime(existing_data['date'])
        new_data = ohlcv[~ohlcv['date'].isin(existing_data['date'])]
    else:
        new_data = ohlcv
    
    if not new_data.empty:
        new_data.to_csv(fpath, mode='a', header=existing_data.empty, index=False)
        logging.info(f"Appended {len(new_data)} new rows to {fpath}")
    else:
        logging.info("No new data to append.")


def append_live_csv(ohlcv: dict, fpath: str):
    '''Append Live Data to CSV
    
    Args:
        ohlcv (dict): OHLCV Data
        fpath (str): File Path
    '''
    ohlcv_df = pd.DataFrame([ohlcv])
    ohlcv_df['date'] = pd.to_datetime(ohlcv_df['date'])

    try:
        ohlcv_df.to_csv(fpath, mode='a', header=not os.path.exists(fpath), index=False)
        logging.info(f"Appended new row to {fpath}")
    except Exception as e:
        logging.error(f"Error appending to CSV: {e}")
