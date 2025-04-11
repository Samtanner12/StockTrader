import pandas as pd
import yfinance as yf

def add_moving_averages(data, short_window=20, long_window=50):
    data['MA20'] = data['Close'].rolling(window=short_window).mean()
    data['MA50'] = data['Close'].rolling(window=long_window).mean()
    return data

def get_multi_timeframe_data(symbol, start_date, end_date):
    """
    Fetches data for multiple timeframes (5m, 1d, 1w).
    """
    timeframes = {
        '5m': yf.download(symbol, interval='5m', start=start_date, end=end_date),
        '1d': yf.download(symbol, interval='1d', start=start_date, end=end_date),
        '1w': yf.download(symbol, interval='1wk', start=start_date, end=end_date),
    }

    for key in timeframes:
        timeframes[key] = add_moving_averages(timeframes[key])

    return timeframes

