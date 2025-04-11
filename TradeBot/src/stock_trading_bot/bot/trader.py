from ib_insync import IB, Option, util
from strategy.the_strat import classify_candles, detect_strat_patterns
from data.data_processor import add_moving_averages
import pandas as pd
import yfinance as yf
from utils.logger import logger

ib = IB()

def fetch_options_chain(symbol, expiration):
    """
    Fetches the options chain synchronously.
    """
    contracts = ib.reqContractDetails(Option(symbol, expiration, 'C', None))
    return contracts

def fetch_historical_data(symbol, start_date, end_date, interval='1d'):
    """
    Fetches historical stock data using Yahoo Finance.
    """
    data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
    return data

def filter_options_chain(contracts, delta_range=(0.2, 0.4)):
    """
    Filters options contracts based on delta and liquidity criteria.
    """
    options_data = pd.DataFrame([{
        'contract': c.contract,
        'delta': c.delta,
        'volume': c.volume,
        'iv': c.iv,
        'bidAskSpread': c.bidAskSpread()
    } for c in contracts if c.delta and c.volume])

    filtered = options_data[
        (options_data['delta'].abs().between(*delta_range)) &
        (options_data['volume'] > 1000) &
        (options_data['bidAskSpread'] <= 0.10)
    ]
    return filtered.iloc[0]['contract'] if not filtered.empty else None

def trade(symbol, start_date, end_date, expiration):
    """
    Executes trades based on candlestick patterns and options data.
    """
    logger.info("trade called")
    ib.connect('127.0.0.1', 4002, clientId=1)

    logger.info("connected")

    # Fetch historical stock data
    historical_data = fetch_historical_data(symbol, start_date, end_date, '1d')
    options_chain = fetch_options_chain(symbol, expiration)

    # Process stock data
    historical_data = add_moving_averages(historical_data)
    historical_data = classify_candles(historical_data)
    historical_data = detect_strat_patterns(historical_data)

    # Filter and select options contract
    selected_option = filter_options_chain(options_chain)
    if selected_option:
        logger.info(f"Selected Option: {selected_option.symbol}")
    else:
        logger.warning("No suitable options contract found.")
        return

    # Analyze candlestick patterns and execute trades
    for i in range(len(historical_data)):
        pattern = historical_data.iloc[i]['Pattern']
        timestamp = historical_data.index[i]
        decision_reason = ""

        if pattern == '2-1-2 Bullish':
            decision_reason = "Detected a bullish continuation pattern with confirmation from moving averages."
            logger.info(f"{timestamp}: {decision_reason}. Decision: Buy {symbol}.")
            ib.placeOrder(selected_option, ib.MarketOrder('BUY', 1))

        elif pattern == '2-1-2 Bearish':
            decision_reason = "Detected a bearish continuation pattern with confirmation from moving averages."
            logger.info(f"{timestamp}: {decision_reason}. Decision: Sell {symbol}.")
            ib.placeOrder(selected_option, ib.MarketOrder('SELL', 1))

        else:
            decision_reason = "No significant pattern detected or conditions did not align with strategy criteria."
            logger.info(f"{timestamp}: {decision_reason}. Decision: No action taken.")

    logger.info("Trading session completed.")

# If you want to run the trade function
if __name__ == "__main__":
    symbol = "AAPL"
    start_date = "2025-03-01"
    end_date = "2025-03-25"
    expiration = "2025-04-01"

    trade(symbol, start_date, end_date, expiration)
