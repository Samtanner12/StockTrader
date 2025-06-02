from ib_insync import IB, Option, MarketOrder

# Configuration
TRAILING_STOP_PERCENT = 10     # % drop from peak
STOP_LOSS_PERCENT = 10        # % loss from entry

def calculate_pnl_percent(entry_price, current_price):
    return (current_price - entry_price) / entry_price * 100

def calculate_drawdown_percent(peak_price, current_price):
    return (peak_price - current_price) / peak_price * 100

def fix_contract(contract: Option) -> Option:
    """Fix missing exchange for market data requests."""
    return Option(
        symbol=contract.symbol,
        lastTradeDateOrContractMonth=contract.lastTradeDateOrContractMonth,
        strike=contract.strike,
        right=contract.right,
        exchange='SMART',
        currency=contract.currency,
        tradingClass=contract.tradingClass
    )

def monitor_positions(ib: IB, peak_prices: dict) -> dict:
    portfolio = ib.portfolio()
    for item in portfolio:
        contract = item.contract
        if not isinstance(contract, Option):
            continue

        position_qty = item.position
        if position_qty <= 0:
            print(f"[{contract.localSymbol}] No position to sell (position={position_qty}). Skipping.")
            continue

        current_price = item.marketPrice
        if current_price is None or current_price <= 0:
            print(f"[{contract.localSymbol}] Market price not available or invalid ({current_price}). Skipping.")
            continue

        entry_price = item.averageCost / 100  # IB uses cents
        if entry_price <= 0:
            print(f"[{contract.localSymbol}] Invalid entry price ({entry_price}). Skipping.")
            continue

        symbol = contract.localSymbol

        # Initialize peak with max(entry, current) to avoid false drawdown = 0
        if symbol not in peak_prices:
            peak_prices[symbol] = max(entry_price, current_price)
            print(f"[{symbol}] Initialized peak: {peak_prices[symbol]:.2f}")

        # Update peak if new high
        if current_price > peak_prices[symbol]:
            peak_prices[symbol] = current_price

        peak = peak_prices[symbol]
        pnl_percent = calculate_pnl_percent(entry_price, current_price)
        drawdown_percent = calculate_drawdown_percent(peak, current_price)

        print(
            f"[{symbol}] Entry: {entry_price:.2f}, Current: {current_price:.2f}, "
            f"Peak: {peak:.2f}, PnL: {pnl_percent:.2f}%, Drawdown: {drawdown_percent:.2f}%"
        )

        # Prepare fixed contract for order placement
        fixed_contract = fix_contract(contract)

        # Check stop loss (from entry)
        if abs(pnl_percent) >= STOP_LOSS_PERCENT and pnl_percent < 0:
            print(f"[EXIT] Stop loss hit for {symbol} ({pnl_percent:.2f}%), selling {position_qty} contracts")
            close_order = MarketOrder('SELL', position_qty)
            ib.placeOrder(fixed_contract, close_order)
            del peak_prices[symbol]
            continue  # Skip trailing stop if already exited

        # Check trailing stop (from peak)
        if drawdown_percent >= TRAILING_STOP_PERCENT:
            print(f"[EXIT] Trailing stop hit for {symbol} ({drawdown_percent:.2f}%), selling {position_qty} contracts")
            close_order = MarketOrder('SELL', position_qty)
            ib.placeOrder(fixed_contract, close_order)
            del peak_prices[symbol]

    return peak_prices


def mainCall(peak):
    ib = IB()
    ib.connect('127.0.0.1', 4002, clientId=123)
    peak_prices = peak  # Persistent across runs

    peak_prices = monitor_positions(ib, peak_prices)
    ib.disconnect()
