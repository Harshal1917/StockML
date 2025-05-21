from v3_Historic_candle_provider import HistCandleProvider
import time
import pandas as pd

def run_data_fetcher():
    provider = HistCandleProvider()

    # Ask for parameters at runtime only once
    stock_symbol = input("Enter stock symbol (e.g., AAPL): ")
    start_time = input("Enter start time (YYYY-MM-DD): ")
    end_time = input("Enter end time (YYYY-MM-DD): ")
    interval = input("Enter interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo): ")

    result = provider.init_candles(stock_symbol, start_time, end_time, interval)
    print(result)

    if result == "SUCCESS":
        # Wait for the fetching process to complete
        while provider.is_running:
            time.sleep(1)  # Sleep for a short time to avoid busy waiting

        # Retrieve and store the fetched data
        fetched_data = []
        while not provider.data_queue.empty():
            candle = provider.data_queue.get()
            fetched_data.append(candle)
            # print("Fetched candle data:", candle)

        # Save the fetched data to an Excel file
        if fetched_data:
            df = pd.DataFrame(fetched_data)  # Convert the list of candles to a DataFrame
            # Add parameters as additional columns
            df['Stock Symbol'] = stock_symbol
            df['Start Time'] = start_time
            df['End Time'] = end_time
            df['Interval'] = interval
            
            # Save to Excel
            output_file = f"{stock_symbol}_data.xlsx"
            df.to_excel(output_file, index=False)
            print(f"Fetched data saved to {output_file}")

    # Stop the fetching process explicitly
    provider.stop_candles()  # Ensure the thread is stopped after fetching

if __name__ == "__main__":
    run_data_fetcher()