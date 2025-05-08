from datetime import datetime
from typing import Dict, Deque
from objects.Candlestick import Candlestick
from bot.buyBot import *

# Define the valid patterns, their directional bias, and signal role
PATTERN_DEFINITIONS = {
    "2-1-2 Pattern": {"type": "Reversal", "bias": {"Bullish"}, "role": "Entry/Exit"},
    "2-1-2 Reversal Pattern": {"type": "Reversal", "bias": {"Bearish"}, "role": "Entry/Exit"},
    "2-1-2 Mixed Reversal Pattern": {"type": "Reversal", "bias": {"Bearish"}, "role": "Entry/Exit"},
    "2-1-2 Mixed Pattern": {"type": "Reversal", "bias": {"Bullish"}, "role": "Entry/Exit"},
    "2-Up Continuation Pattern": {"type": "Continuation", "bias": {"Bullish"}, "role": "Entry"},
    "2-Down Continuation Pattern": {"type": "Continuation", "bias": {"Bearish"}, "role": "Entry"},
    "Directional Bar to 2-Up": {"type": "Continuation", "bias": {"Directional"}, "role": "Entry"},
    "Outside Bar to 2-Down": {"type": "Reversal", "bias": {"Bearish"}, "role": "Entry"},
    "Outside Bar to 2-Up": {"type": "Reversal", "bias": {"Bullish"}, "role": "Entry"},
    "Inside Bars Pattern": {"type": "Continuation", "bias": {"Neutral"}, "role": "Consolidation"},
}



# Log function
def log(level: str, message: str):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{level}] {message}")

# Extract the bias from the pattern
def extract_bias_from_pattern(pattern: str) -> str:
    for key, details in PATTERN_DEFINITIONS.items():
        if pattern.startswith(key):
            if len(details['bias']) == 1:
                bias = next(iter(details['bias']))
                log("DEBUG", f"Extracted bias '{bias}' for pattern '{pattern}' (single bias)")
                return bias
            if "Up" in pattern or "Bullish" in pattern:
                log("DEBUG", f"Extracted bias 'Bullish' for pattern '{pattern}' (from name)")
                return "Bullish"
            if "Down" in pattern or "Bearish" in pattern:
                log("DEBUG", f"Extracted bias 'Bearish' for pattern '{pattern}' (from name)")
                return "Bearish"
            log("DEBUG", f"Extracted default bias 'Directional' for pattern '{pattern}' (ambiguous)")
            return "Directional"
    log("DEBUG", f"No matching pattern found for bias extraction: '{pattern}'")
    return "None"

# Check if the pattern is an entry pattern
def is_entry_pattern(pattern: str) -> bool:
    for key, details in PATTERN_DEFINITIONS.items():
        if pattern.startswith(key) and details['role'] in {"Entry", "Entry/Exit"}:
            log("DEBUG", f"Pattern '{pattern}' is a valid entry pattern.")
            return True
    log("DEBUG", f"Pattern '{pattern}' is NOT a valid entry pattern.")
    return False

# Entry signal logic
def check_entry_signals(short_term_data, mid_term_data, long_term_data):
    for ticker in short_term_data.keys():
        if not (short_term_data[ticker] and mid_term_data.get(ticker) and long_term_data.get(ticker)):
            continue

        last_short = short_term_data[ticker][-1]
        last_mid = mid_term_data[ticker][-1]
        last_long = long_term_data[ticker][-1]

        short_pattern = last_short.candlePattern
        mid_pattern = last_mid.candlePattern
        long_pattern = last_long.candlePattern

        if not short_pattern or short_pattern == "NONE":
            continue

        if not is_entry_pattern(short_pattern):
            continue

        short_bias = extract_bias_from_pattern(short_pattern)
        mid_bias = extract_bias_from_pattern(mid_pattern)
        long_bias = extract_bias_from_pattern(long_pattern)

        if short_bias == mid_bias == long_bias and short_bias != "None":
            log("INFO", f"TRADE SIGNAL: {ticker} | Pattern: {short_pattern} | Bias: {short_bias}")
            execute_market_buy(ticker, short_bias, short_term_data[ticker], last_short)

