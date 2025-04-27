from ib_insync import IB, Stock, util
from collections import defaultdict, deque
from dataclasses import dataclass
from objects.Candlestick import Candlestick
import pandas as pd
import logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=1)  # Make sure IB Gateway is running!

def fetch_historical_data(symbol: str, duration: str = '2 D', bar_size: str = '1 day'):
    try:
        # Clean up duration to match IBKR's required format
        duration = duration.upper().replace('D', ' D').replace('W', ' W').replace('M', ' M').replace('Y', ' Y')
        duration = ' '.join(duration.split())  # Remove any extra spaces

        # Create a Stock contract
        contract = Stock(symbol, 'SMART', 'USD')

        # Request historical data
        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1
        )

        # Convert to DataFrame
        df = util.df(bars)
        return df
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()


def create_candlesticks(df: pd.DataFrame):
    candles = []
    for _, row in df.iterrows():
        candle = Candlestick(
            timestamp=row['date'],
            open=row['open'],
            high=row['high'],
            low=row['low'],
            close=row['close'],
            volume=row.get('volume', 0.0),
        )

        # Set candleType based on open and close
        
        candle.candleType = 0  # doji / indecision

        candles.append(candle)
    return candles


def populate_candlestick_data(tickers, duration='2 D', bar_size='1 day'):
    candle_map = defaultdict(lambda: deque(maxlen=4))

    for symbol in tickers:
        logger.info(f"Fetching data for {symbol}")
        df = fetch_historical_data(symbol, duration=duration, bar_size=bar_size)

        if df.empty:
            logger.warning(f"No data for {symbol}")
            continue

        candlesticks = create_candlesticks(df)

        for candle in candlesticks[-4:]:
            candle_map[symbol].append(candle)

        logger.info(f"Added {len(candle_map[symbol])} candles for {symbol}")

    return candle_map

# Example usage:
# tickers = ['AAPL', 'MSFT']
# candles = populate_candlestick_data(tickers)
# ib.disconnect()
