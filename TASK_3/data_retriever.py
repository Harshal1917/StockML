from v3_Historic_candle_provider import HistCandleProvider
import time
import threading

def retrieve_data(provider):
    """Function to continuously retrieve and display candles."""
    while provider.is_running or not provider.data_queue.empty():
        candle = provider.get_candle()
        if candle:
            print("Retrieved Candle:", candle)
        else:
            # If no candle is available, wait a bit before trying again
            time.sleep(1)

    print("Data retrieval completed. No more candles available.")

def main():
    provider = HistCandleProvider()

    # Example parameters
    stock_symbol = "AAPL"
    start_time = "2023-01-01"
    end_time = "2023-01-10"
    interval = "1d"

    # Initialize the candle provider
    provider.init_candles(stock_symbol, start_time, end_time, interval)

    # Start a separate thread to retrieve data
    retrieval_thread = threading.Thread(target=retrieve_data, args=(provider,))
    retrieval_thread.start()

    # Keep the main thread alive while fetching data
    while provider.is_running:
        time.sleep(1)

    # Stop the retrieval thread
    provider.stop_candles()
    retrieval_thread.join()  # Wait for the retrieval thread to finish
    print("Data retrieval stopped.")

if __name__ == "__main__":
    main()