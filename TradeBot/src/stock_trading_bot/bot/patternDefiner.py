from typing import Dict, Deque
from objects.Candlestick import Candlestick

class PatternDefiner:
    @staticmethod
    def define_patterns(candle_map: Dict[str, Deque[Candlestick]]):
        print("Defining patterns...")
        for ticker, candles in candle_map.items():
            if len(candles) < 3:
                continue  # Need at least 3 candles to detect a pattern

            # Iterate over the candles, starting from the third to check patterns
            for i in range(2, len(candles)):
                # Get the candle types of the previous, middle, and last candles
                prev_candle_type = candles[i-2].candleType
                middle_candle_type = candles[i-1].candleType
                last_candle_type = candles[i].candleType

                # Check if the pattern should be applied based on the candle types
                if prev_candle_type == 4 and middle_candle_type == 1 and last_candle_type == 4:  # 2-1-2 Pattern
                    candles[i].candlePattern = "2-1-2 Pattern"
                    print(f"Pattern detected for {ticker}: 2-1-2 Pattern at candle {i}")
                elif prev_candle_type == 5 and middle_candle_type == 1 and last_candle_type == 5:  # 2-1-2 Reversal Pattern
                    candles[i].candlePattern = "2-1-2 Reversal Pattern"
                    print(f"Pattern detected for {ticker}: 2-1-2 Reversal Pattern at candle {i}")
                elif prev_candle_type == 4 and middle_candle_type == 1 and last_candle_type == 5:  # 2-1-2 Reversal Pattern (mixed)
                    candles[i].candlePattern = "2-1-2 Mixed Reversal Pattern"
                    print(f"Pattern detected for {ticker}: 2-1-2 Mixed Reversal Pattern at candle {i}")
                elif prev_candle_type == 5 and middle_candle_type == 1 and last_candle_type == 4:  # 2-1-2 Mixed Pattern
                    candles[i].candlePattern = "2-1-2 Mixed Pattern"
                    print(f"Pattern detected for {ticker}: 2-1-2 Mixed Pattern at candle {i}")
                elif prev_candle_type == 4 and middle_candle_type == 4 and last_candle_type == 4:  # 2-Up Candles (Continuing)
                    candles[i].candlePattern = "2-Up Continuation Pattern"
                    print(f"Pattern detected for {ticker}: 2-Up Continuation Pattern at candle {i}")
                elif prev_candle_type == 5 and middle_candle_type == 5 and last_candle_type == 5:  # 2-Down Candles (Reversal)
                    candles[i].candlePattern = "2-Down Continuation Pattern"
                    print(f"Pattern detected for {ticker}: 2-Down Cont Pattern at candle {i}")
                elif prev_candle_type == 2 and middle_candle_type == 1 and last_candle_type == 4:  # Directional bar to 2-Up
                    candles[i].candlePattern = "Directional Bar to 2-Up"
                    print(f"Pattern detected for {ticker}: Directional Bar to 2-Up at candle {i}")
                elif prev_candle_type == 3 and middle_candle_type == 1 and last_candle_type == 5:  # Outside bar to 2-Down
                    candles[i].candlePattern = "Outside Bar to 2-Down"
                    print(f"Pattern detected for {ticker}: Outside Bar to 2-Down at candle {i}")
                elif prev_candle_type == 3 and middle_candle_type == 1 and last_candle_type == 4:  # Outside bar to 2-Down
                    candles[i].candlePattern = "Outside Bar to 2-Up"
                    print(f"Pattern detected for {ticker}: Outside Bar to 2-Up at candle {i}")
                elif prev_candle_type == 1 and middle_candle_type == 1 and last_candle_type == 1:  # Inside bars pattern
                    candles[i].candlePattern = "Inside Bars Pattern"
                    print(f"Pattern detected for {ticker}: Inside Bars Pattern at candle {i}")
                else:
                    candles[i].candlePattern = "NONE"

    # The pattern-checking functions are now incorporated into the logic directly via the candleType checks
    # Therefore, no additional functions are required for checking specific patterns based on high/low comparisons.
