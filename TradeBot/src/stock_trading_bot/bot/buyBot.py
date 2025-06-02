from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from datetime import datetime
from ib_insync import IB, Stock, Option, util
from ib_insync import MarketOrder

# Constants
RISK_PER_TRADE = 100

# Logging
def log(level: str, message: str):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{level}] {message}")


class IBKRWrapper:
    def __init__(self, host='127.0.0.1', port=4002, client_id=0):
        self.ib = IB()
        self.host = host
        self.port = port
        self.client_id = client_id

    def connect(self):
        try:
            if not self.ib.isConnected():
                self.ib.connect(self.host, self.port, self.client_id)
                log("INFO", "Connected to IBKR TWS/Gateway")
        except Exception as e:
            log("ERROR", f"Failed to connect: {e}")
            raise


    def disconnect(self):
        try:
            if self.ib.isConnected():
                self.ib.disconnect()
                log("INFO", "Disconnected from IBKR")
        except Exception as e:
            log("ERROR", f"Failed to disconnect: {e}")


    def get_implied_volatility(self, ticker: str, expiry: str, strike: float, right: str):
        self.connect()
        option = Option(ticker, expiry, strike, right, 'SMART', 'USD')
        option.multiplier = '100'

        if not self.ib.qualifyContracts(option):
            raise ValueError(f"Failed to qualify contract for {ticker} {expiry} {strike}{right}")

        ticker_data = self.ib.reqMktData(option, genericTickList='106', snapshot=False)
        self.ib.sleep(2)

        iv = None
        try:
            if ticker_data.modelGreeks and ticker_data.modelGreeks.impliedVol is not None:
                iv = ticker_data.modelGreeks.impliedVol
        except Exception as e:
            log("ERROR", f"Error reading implied volatility: {e}")
        finally:
            self.ib.cancelMktData(ticker_data)

        return iv





    def get_option_price(self, ticker: str, expiry: str, strike: float, right: str):
        self.connect()
        option = Option(ticker, expiry, strike, right, 'SMART', 'USD')
        option.multiplier = '100'

        if not self.ib.qualifyContracts(option):
            raise ValueError(f"Failed to qualify option contract for {ticker}")

        ticker_data = self.ib.reqMktData(option, '', False, False)
        self.ib.sleep(2)

        try:
            price = ticker_data.marketPrice()
            if price is None or price <= 0:
                raise ValueError("Invalid market price received.")
        finally:
            self.ib.cancelMktData(ticker_data)

        return price


    def place_market_order(self, ticker: str, expiry: str, strike: float, right: str, quantity: int, action="BUY"):
        self.connect()
        option = Option(ticker, expiry, strike, right, 'SMART', 'USD')
        option.multiplier = '100'


        if not self.ib.qualifyContracts(option):
            raise ValueError(f"Failed to qualify option contract for {ticker}")

        order = MarketOrder(action, quantity)
        trade = self.ib.placeOrder(option, order)

        self.ib.sleep(2)

        if not trade.orderStatus:
            raise RuntimeError("Order status not received.")

        return {
            "status": trade.orderStatus.status,
            "filled": trade.orderStatus.filled,
            "avgFillPrice": trade.orderStatus.avgFillPrice
        }

    def get_current_price(self, ticker: str):
        self.connect()
        stock_contract = Stock(ticker, 'SMART', 'USD')

        if not self.ib.qualifyContracts(stock_contract):
            raise ValueError(f"Failed to qualify stock contract for {ticker}")

        ticker_data = self.ib.reqMktData(stock_contract, '', False, False)
        self.ib.sleep(2)

        try:
            price = ticker_data.marketPrice()
            if price is None or price <= 0:
                raise ValueError("Invalid current price received.")
        finally:
            self.ib.cancelMktData(ticker_data)

        return price


# Utility functions
def determine_strike_distance(iv):
    if iv is None:
        raise ValueError("Implied volatility is None")
    if iv < 0.4:
        return 0.05
    elif iv < 0.6:
        return 0.1
    elif iv < 0.8:
        return 0.2
    elif iv < 1.0:
        return 0.5
    else:
        return 1.0

def determine_dte(iv):
    if iv is None:
        raise ValueError("Implied volatility is None")
    if iv < 0.4:
        return 7
    elif iv < 0.6:
        return 14
    elif iv < 0.8:
        return 21
    else:
        return 30

def calculate_contracts(entry_price):
    return max(int(RISK_PER_TRADE / (entry_price * 100)), 1)

def get_valid_option_strike_and_expiry(ib: IB, ticker: str, bias: str, base_strike: float):
    stock_contract = Stock(ticker, 'SMART', 'USD')
    ib.qualifyContracts(stock_contract)

    chains = ib.reqSecDefOptParams(stock_contract.symbol, '', stock_contract.secType, stock_contract.conId)

    if not chains:
        raise ValueError(f"No option chain found for {ticker}")

    chain = chains[0]
    strikes = sorted([s for s in chain.strikes if 0 < s < 2000])
    expirations = sorted(chain.expirations)

    if not expirations:
        raise ValueError(f"No expirations found for {ticker}")

    expiry = min(expirations)

    if bias == "Bullish":
        strike = min((s for s in strikes if s >= base_strike), default=strikes[-1])
    else:
        strike = max((s for s in strikes if s <= base_strike), default=strikes[0])

    return expiry, strike


# Main execution function
def execute_market_buy(ticker, bias, candle_data, last_candle):
    log("INFO", f"Executing MARKET BUY for {ticker} ({bias} bias)...")
    ibkr = IBKRWrapper()
    ib = ibkr.ib

    try:
        ibkr.connect()
        base_price = ibkr.get_current_price(ticker)
        expiry, strike = get_valid_option_strike_and_expiry(ib, ticker, bias, base_price)

        right = 'C' if bias == "Bullish" else 'P'
        iv = ibkr.get_implied_volatility(ticker, expiry, strike, right)
        log("INFO", f"Fetched IV: {iv}")

        if iv is None:
            log("ERROR", f"Could not fetch implied volatility for {ticker}, aborting.")
            return

        strike_distance = determine_strike_distance(iv)
        dte = determine_dte(iv)
        log("INFO", f"Strike Distance: {strike_distance}, DTE: {dte}")

        option_price = ibkr.get_option_price(ticker, expiry, strike, right)
        log("INFO", f"Option Price: {option_price}")

        if option_price is None:
            log("ERROR", f"Could not retrieve option price for {ticker}, aborting.")
            return

        contracts = calculate_contracts(option_price)
        log("INFO", f"Contracts to buy: {contracts}")

        trade_response = ibkr.place_market_order(ticker, expiry, strike, right, contracts)
        log("INFO", f"Trade response: {trade_response}")

    except ValueError as e:
        log("ERROR", str(e))
    finally:
        ibkr.disconnect()
