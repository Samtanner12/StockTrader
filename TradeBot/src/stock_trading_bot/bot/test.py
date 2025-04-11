from ib_insync import *

# Connect to TWS or IB Gateway
ib = IB()
ib.connect('127.0.0.1', 4002, clientId=1)

# Define the AAPL stock contract
contract = Stock('AAPL', 'SMART', 'USD')

# Request historical data: 1 day of 1-minute bars
bars = ib.reqHistoricalData(
    contract,
    endDateTime='',
    durationStr='1 D',
    barSizeSetting='1 min',
    whatToShow='MIDPOINT',  # Can also be 'TRADES', 'BID', 'ASK', etc.
    useRTH=True,            # Regular Trading Hours only
    formatDate=1
)

# Print the latest few bars
for bar in bars[-5:]:
    print(f"{bar.date} | Open: {bar.open} | High: {bar.high} | Low: {bar.low} | Close: {bar.close} | Volume: {bar.volume}")

# Disconnect
ib.disconnect()
