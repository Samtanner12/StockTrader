import yfinance as yf

def get_stock_data(symbol, start_date, end_date, interval="1d"):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d", start=start_date, end=end_date, interval=interval)
    return data
