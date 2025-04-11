def moving_average_strategy(data):
    buy_signal = (data['MA20'] > data['MA50']) & (data['MA20'].shift(1) < data['MA50'].shift(1))
    sell_signal = (data['MA20'] < data['MA50']) & (data['MA20'].shift(1) > data['MA50'].shift(1))

    data['Buy'] = buy_signal
    data['Sell'] = sell_signal
    return data
