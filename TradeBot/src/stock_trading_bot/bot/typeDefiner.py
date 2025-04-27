from typing import Dict, Deque
from objects.Candlestick import Candlestick

class TypeDefiner:
    @staticmethod
    def define_types(candle_map: Dict[str, Deque[Candlestick]]):
        for ticker, candles in candle_map.items():
            if len(candles) < 2:
                continue

            prev_candle = None
            prev_bullish = None  # Track if the previous candle was bullish or bearish
            for candle in candles:
                if prev_candle:
                    # Check for Inside bar (1)
                    if candle.high < prev_candle.high and candle.low > prev_candle.low:
                        candle.candleType = 1  # Inside bar

                    # Check for Outside bar (3)
                    elif candle.high > prev_candle.high and candle.low < prev_candle.low:
                        candle.candleType = 3  # Outside bar

                    # Check for 2-Up (4)
                    elif prev_candle.high < candle.high:
                        candle.candleType = 4  # 2-Up candle

                    # Check for 2-Down (5)
                    elif prev_candle.low > candle.low:
                        candle.candleType = 5  # 2-Down candle
           
                    # Check for Directional bar (2)
                    else:
                        candle.candleType = 2  # Directional bar


                # Track if the previous candle was bullish or bearish
                prev_bullish = candle.is_bullish()
                prev_candle = candle
