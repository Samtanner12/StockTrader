from bot.real_time_trader import real_time_trading
from utils.config import SYMBOL, START_DATE, END_DATE, INTERVAL

def main():
    real_time_trading(SYMBOL, START_DATE, END_DATE, interval=INTERVAL)

if __name__ == "__main__":
    main()
