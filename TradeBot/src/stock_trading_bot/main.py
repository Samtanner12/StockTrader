from bot.trader import populate_candlestick_data
from utils.config import SYMBOL, INTERVAL
from objects.Candlestick import Candlestick
from bot.typeDefiner import TypeDefiner
from bot.patternDefiner import PatternDefiner  # Import PatternDefiner

if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "SPY", "MSTR"]

    # Choose duration and interval (bar size)
    duration = "5 D"        # Last 5 days
    bar_size = "1 day"      # 1-day candlesticks

    # Fetch candlestick data
    candlestick_data = populate_candlestick_data(tickers, duration=duration, bar_size=bar_size)

    # Set candle types (1, 2, or 3)
    TypeDefiner.define_types(candlestick_data)

    # Set candle patterns based on "The Strat" method
    PatternDefiner.define_patterns(candlestick_data)

    # Example print for candlesticks and their types & patterns
    for ticker, candles in candlestick_data.items():
        print(f"\n{ticker}:")
        for c in candles:
            print(f"Candle: {c}")
            print(f"Candle Type: {c.candleType}")
            print(f"Candle Pattern: {c.candlePattern}")
