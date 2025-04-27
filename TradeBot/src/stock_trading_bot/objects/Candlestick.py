from dataclasses import dataclass
from datetime import datetime

@dataclass
class Candlestick:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0  # optional, default is 0
    candleType = 0
    candlePattern = ""

    def is_bullish(self):
        return self.close > self.open

    def is_bearish(self):
        return self.close < self.open

    def body_size(self):
        return abs(self.close - self.open)

    def wick_size(self):
        return (self.high - self.low) - self.body_size()
