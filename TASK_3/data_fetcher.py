from v3_Historic_candle_provider import HistCandleProvider
import time

def main():
    provider = HistCandleProvider()

    while True:
        # Ask for parameters at runtime
        stock_symbol = input("Enter stock symbol (e.g., AAPL): ")
        start_time = input("Enter start time (YYYY-MM-DD): ")
        end_time = input("Enter end time (YYYY-MM-DD): ")
        interval = input("Enter interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo): ")

        result = provider.init_candles(stock_symbol, start_time, end_time, interval)
        print(result)

        # Wait for the fetch thread to finish
        provider.fetch_thread.join()#stop_candle
        
        print("All data fetched. Please enter new parameters.")

if __name__ == "__main__":
    main()