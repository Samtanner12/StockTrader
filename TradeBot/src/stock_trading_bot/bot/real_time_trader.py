import time
from datetime import datetime, timedelta
from bot.trader import trade
from utils.logger import logger


def get_next_friday():
    """
    Returns the next Friday from today.
    """
    today = datetime.now()
    next_friday = today + timedelta((4 - today.weekday()) % 7)
    return next_friday.strftime("%Y-%m-%d")

def real_time_trading(symbol, start_date, end_date, interval=0):
    logger.info("real time trading")
    expiration = get_next_friday()  # Calculate the next expiration date dynamically
    while True:
        #logger.info(f"Checking {symbol} at {time.ctime()}")
        trade(symbol, start_date, end_date, expiration)
        """
        try:
            trade(symbol, start_date, end_date, expiration)
        except Exception as e:
            logger.error(f"Error during trade: {e}")
        time.sleep(interval) """

def analyze_data_in_batches(data, batch_size=10):
    """
    Processes the historical data in batches for faster analysis.
    """
    for i in range(0, len(data), batch_size):
        batch = data.iloc[i:i + batch_size]
        for index, row in batch.iterrows():
            pattern = row['Pattern']
            timestamp = index

            if pattern == '2-1-2 Bullish':
                decision_reason = "Detected bullish continuation."
                logger.info(f"{timestamp}: {decision_reason}. Decision: Buy.")
            elif pattern == '2-1-2 Bearish':
                decision_reason = "Detected bearish continuation."
                logger.info(f"{timestamp}: {decision_reason}. Decision: Sell.")
            else:
                logger.info(f"{timestamp}: No actionable pattern detected.")
