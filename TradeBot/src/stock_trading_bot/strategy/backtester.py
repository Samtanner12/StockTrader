def backtest_strategy(data, initial_balance=10000):
    balance = initial_balance
    position = 0  # No stock initially
    for i in range(1, len(data)):
        if data['Buy'].iloc[i]:
            position = balance // data['Close'].iloc[i]
            balance -= position * data['Close'].iloc[i]
            print(f"Bought at {data['Close'].iloc[i]} on {data.index[i]}")
        elif data['Sell'].iloc[i] and position > 0:
            balance += position * data['Close'].iloc[i]
            position = 0
            print(f"Sold at {data['Close'].iloc[i]} on {data.index[i]}")

    final_balance = balance + position * data['Close'].iloc[-1]
    print(f"Final balance: {final_balance}")
