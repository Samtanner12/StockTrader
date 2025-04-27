from ib_insync import *
import pandas as pd
import yfinance as yf

ib = IB()

def fetch_historical_data(symbol, start_date, end_date, interval='1d'):
    return yf.download(symbol, start=start_date, end=end_date, interval=interval)

def fetch_option_historical_price(option_contract, end_date, duration='1 M', bar_size='1 day'):
    try:
        bars = ib.reqHistoricalData(
            option_contract,
            endDateTime=end_date,
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow='MIDPOINT',
            useRTH=True,
            formatDate=1
        )
        return util.df(bars)
    except Exception as e:
        print(f"Error fetching historical data for option {option_contract.symbol}: {e}")
        return None

def pick_atm_option(contracts, underlying_price):
    if not contracts:
        print("Empty contract list passed to pick_atm_option.")
        return None

    # Ensure contracts is a list of Option objects (not a DataFrame or Series)
    if isinstance(contracts, pd.DataFrame):
        contracts = contracts['contract'].tolist()

    # If contracts are still not a list, something is wrong
    if not all(isinstance(c, Option) for c in contracts):
        print("Contracts list is not composed of Option objects.")
        return None

    return min(contracts, key=lambda c: abs(c.strike - underlying_price))

def fetch_options_chain(symbol, expiration):
    print(f"Fetching contracts for {symbol} expiring on {expiration}")
    
    # Get the underlying contract (no market data involved)
    stock = Stock(symbol, 'SMART', 'USD')
    ib.qualifyContracts(stock)

    # Get option chain info
    try:
        opt_params = ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)
    except Exception as e:
        print(f"Error fetching option parameters: {e}")
        return []

    # Filter for our expiration
    params = [p for p in opt_params if p.exchange == 'SMART']
    if not params:
        print(f"No options found for {symbol} on SMART exchange.")
        return []

    params = params[0]

    # Use strikes near the money
    price = yf.Ticker(symbol).history(period="1d")['Close'].iloc[-1]
    strikes = sorted([strike for strike in params.strikes if abs(strike - price) < 10])
    contracts = []
    
    for strike in strikes:
        for right in ['C', 'P']:
            contract = Option(symbol, expiration.replace('-', ''), strike, right, 'SMART')
            contracts.append(contract)

    # Ensure contracts are qualified
    ib.qualifyContracts(*contracts)
    
    return contracts

def trade(symbol, start_date, end_date, expiration):
    print(f"Starting trade execution using historical data.")
    ib.connect('127.0.0.1', 4002, clientId=1)

    # Fetch historical data for the underlying stock (AAPL)
    historical_data = fetch_historical_data(symbol, start_date, end_date)
    if historical_data.empty:
        print(f"No historical data found for {symbol}. Exiting.")
        ib.disconnect()
        return

    last_close = historical_data.iloc[-1]['Close']

    # Fetch the options chain based on historical data
    contracts = fetch_options_chain(symbol, expiration)
    if not contracts:
        print(f"No option contracts found for {symbol} expiring on {expiration}. Exiting.")
        ib.disconnect()
        return

    # Pick the ATM option based on the last close price from historical data
    selected_option = pick_atm_option(contracts, last_close)
    if selected_option is None:
        print("No ATM option found. Exiting.")
        ib.disconnect()
        return

    print(f"Selected Option: {selected_option.symbol} (Strike: {selected_option.strike})")

    # Fetch historical option prices for the selected option (simulating historical trade behavior)
    option_prices = fetch_option_historical_price(selected_option, end_date)
    if option_prices is None:
        print(f"Error fetching historical data for {selected_option.symbol}. Exiting.")
        ib.disconnect()
        return

    print(f"Fetched {len(option_prices)} historical option price bars.")

    # Add any further logic (like strategy classification or decision making here)
    print("Historical data processing complete.")
    
    ib.disconnect()
    print("Trading session completed.")

# Example usage
if __name__ == "__main__":
    symbol = "AAPL"
    start_date = "2025-03-01"
    end_date = "2025-03-25"
    expiration = "2025-04-01"

    trade(symbol, start_date, end_date, expiration)
 