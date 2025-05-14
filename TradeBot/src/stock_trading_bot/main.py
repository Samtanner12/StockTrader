from bot.trader import populate_candlestick_data
from utils.config import SYMBOL, INTERVAL
from objects.Candlestick import Candlestick
from bot.typeDefiner import TypeDefiner
from bot.patternDefiner import PatternDefiner  # Import PatternDefiner
from bot.entryBot import check_entry_signals


from typing import Dict, Deque

if __name__ == "__main__":
    tickers = [
    "TSLA",  # Tesla
    "AMD",   # Advanced Micro Devices
    "NVDA",  # Nvidia
    "META",  # Meta Platforms
    "AMZN",  # Amazon
    "AAPL",  # Apple
    "MSFT",  # Microsoft
    "NFLX",  # Netflix
    "GOOGL", # Alphabet
    "BABA",  # Alibaba
    "BA",    # Boeing
    "SPCE",  # Virgin Galactic
    "PLTR",  # Palantir
    "COIN",  # Coinbase
    "SHOP",  # Shopify
    "ROKU",  # Roku
    "MARA",  # Marathon Digital
    "RIOT",  # Riot Platforms
    "FUBO",  # FuboTV
    "LCID",  # Lucid Motors
    "RBLX",  # Roblox
    "SNAP",  # Snap Inc.
    "AFRM",  # Affirm
    "GME",   # GameStop
    "AMC",   # AMC Entertainment
    "FSLR",  # First Solar
    "UPST",  # Upstart
    "ENPH",  # Enphase
    "TLRY",  # Tilray
    "PYPL",  # PayPal
    "NIO",   # NIO Inc.
    "CCL",   # Carnival
    "UAL",   # United Airlines
    "AAL",   # American Airlines
    "DIS",   # Disney
    "CVNA",  # Carvana
    "ARKK",  # ARK Innovation ETF
    "SPY",   # S&P500 ETF (not volatile but a benchmark)
    "QQQ",
    "A",
    "AA",
    "AACB",
    "AACG",
    "AACT",
    "AAL",
    "AAM",
    "AAME",
    "AAMI",
    "AAOI",
    "AAON",
    "AAP",
    "AAPG"
    ]


    short_term_data: Dict[str, Deque[Candlestick]] = populate_candlestick_data(tickers, duration="1200 S", bar_size="5 mins")
    mid_term_data: Dict[str, Deque[Candlestick]] = populate_candlestick_data(tickers, duration="3600 S", bar_size="15 mins")
    long_term_data: Dict[str, Deque[Candlestick]] = populate_candlestick_data(tickers, duration="7200 S", bar_size="30 mins")


    # Classify candle types
    TypeDefiner.define_types(short_term_data)
    TypeDefiner.define_types(mid_term_data)
    TypeDefiner.define_types(long_term_data)

    # Define patterns based on candle types
    PatternDefiner.define_patterns(short_term_data)
    PatternDefiner.define_patterns(mid_term_data)
    PatternDefiner.define_patterns(long_term_data)

    # Output results
    print("\n--- SHORT TERM (5-min chart) ---")
    for ticker, candles in short_term_data.items():
        print(f"\n{ticker}:")
        for c in candles:
            print(f"Time: {c.timestamp}, Type: {c.candleType}, Pattern: {c.candlePattern}")

    print("\n--- MID TERM (15-min chart) ---")
    for ticker, candles in mid_term_data.items():
        print(f"\n{ticker}:")
        for c in candles:
            print(f"Time: {c.timestamp}, Type: {c.candleType}, Pattern: {c.candlePattern}")

    print("\n--- LONG TERM (30-min chart) ---")
    for ticker, candles in long_term_data.items():
        print(f"\n{ticker}:")
        for c in candles:
            print(f"Time: {c.timestamp}, Type: {c.candleType}, Pattern: {c.candlePattern}")
            

# After printing patterns:
    check_entry_signals(short_term_data, mid_term_data, long_term_data)

