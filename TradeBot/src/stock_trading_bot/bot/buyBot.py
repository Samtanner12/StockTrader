from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickType
import threading
import time
from typing import Deque
from objects.Candlestick import Candlestick


class buyBot(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.implied_volatility = None
        self.option_order_response = None

    def tickOptionComputation(self, reqId: int, tickType: TickType, impliedVol: float, delta: float, optPrice: float, pvDividend: float, gamma: float, vega: float, theta: float, undPrice: float):
        """This function processes the implied volatility from market data"""
        if tickType == 10:  # Implied Volatility tick type
            self.implied_volatility = impliedVol
            print(f"Implied Volatility: {self.implied_volatility}")

    def place_option_order(self, ticker: str, strike: float, stop_loss: float, take_profit: float):
        """Place the option order through IBKR"""
        contract = Contract()
        contract.symbol = ticker
        contract.secType = "OPT"
        contract.exchange = "SMART"
        contract.currency = "USD"
        contract.strike = strike
        contract.right = "C"  # Call option
        contract.lastTradeDateOrContractMonth = "20230519"  # Example expiration date
        contract.multiplier = "100"
        
        order = Order()
        order.action = "BUY"
        order.totalQuantity = 1
        order.orderType = "MKT"
        
        # For this example, we'll place a market order (no limit/stop)
        self.placeOrder(1, contract, order)
        print("Placing option order...")

    def get_implied_volatility(self, ticker: str, expiry: str, strike: float, right: str):
        """Fetch the implied volatility for a specific option using IBKR API."""
        contract = Contract()
        contract.symbol = ticker
        contract.secType = "OPT"
        contract.exchange = "SMART"
        contract.currency = "USD"
        contract.lastTradeDateOrContractMonth = expiry
        contract.strike = strike
        contract.right = right
        contract.multiplier = "100"
        
        # Request market data
        self.reqMktData(1, contract, "", False, False, [])
        time.sleep(2)  # Wait for the response to be processed
        
        return self.implied_volatility

def log(level: str, message: str):
    """Simple logger using print with timestamp and level."""
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{level}] {message}")

# Function to determine the strike distance based on IV
def determine_strike_distance(iv):
    if iv < 40:
        return 0.05  # +/- 5%
    elif iv < 60:
        return 0.10  # +/- 10%
    elif iv < 80:
        return 0.15  # +/- 15%
    elif iv < 100:
        return 0.20  # +/- 20%
    else:
        return 0.25  # +/- 25%

# Fetch implied volatility using IBKR client
def get_implied_volatility(ticker: str, expiry: str, strike: float, right: str):
    """Wrapper function to start IBKR client and fetch implied volatility"""
    ibkr_client = IBKRClient()
    
    # Connect to the IBKR TWS or IB Gateway (replace '127.0.0.1' with the correct IP if needed)
    ibkr_client.connect("127.0.0.1", 7497, 0)
    
    # Start a new thread for the IBKR client to avoid blocking the main thread
    client_thread = threading.Thread(target=ibkr_client.run)
    client_thread.start()
    
    # Fetch implied volatility (this blocks until the data is returned)
    iv = ibkr_client.get_implied_volatility(ticker, expiry, strike, right)
    
    # Disconnect after getting the data
    ibkr_client.disconnect()
    
    # Return the implied volatility
    return iv

# Main function to execute market buy
def execute_market_buy(ticker: str, bias: str, short_data: Deque[Candlestick], last_candle: Candlestick):
    log("INFO", f"Executing MARKET BUY for {ticker} ({bias} bias)...")

    # Determine OTM strike based on current IV bracket
    iv = get_implied_volatility(ticker, "20230519", 150, "C")  # Example expiry and strike for calls
    strike_distance = determine_strike_distance(iv)

    # Fetch the OTM strike and ensure it's a valid option
    option_strike = get_otm_strike(ticker, strike_distance, bias)
    
    # Ensure stop loss and take profit logic is handled based on candle data
    stop_loss = calculate_stop_loss(last_candle, bias)
    take_profit = calculate_take_profit(bias)

    # Execute market buy for the selected option
    buy_bot = buyBot()
    buy_bot.place_option_order(ticker, option_strike, stop_loss, take_profit)


# Calculate stop loss based on previous candle
def calculate_stop_loss(last_candle, bias):
    if bias == "Bullish":
        return last_candle.low  # For Calls: stop loss is previous candle's low
    elif bias == "Bearish":
        return last_candle.high  # For Puts: stop loss is previous candle's high

# Calculate take profit based on reversal pattern or wick breakout
def calculate_take_profit(bias):
    if bias == "Bullish":
        return "Take Profit for Bullish"  # Define logic for take profit in your strategy
    elif bias == "Bearish":
        return "Take Profit for Bearish"  # Define logic for take profit in your strategy

# Placeholder for fetching the OTM option strike
def get_otm_strike(ticker: str, strike_distance: float, bias: str):
    current_price = get_current_price(ticker)
    if bias == "Bullish":
        return current_price * (1 + strike_distance)
    else:
        return current_price * (1 - strike_distance)

# Placeholder for getting the current price of a ticker
def get_current_price(ticker: str):
    return 100  # Example price (this would need to be fetched from an API like IBKR)

