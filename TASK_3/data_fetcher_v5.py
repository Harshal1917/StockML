from v5_Historic_candle_provider import HistCandleProvider
import time

def main():
    provider = HistCandleProvider()

    # Initialize candles
    symbol = "INFY.NS"  # or any other symbol you want to use
    start_time = "2020-01-01"
    end_time = "2020-02-01"
    interval = "1d"

    print(f"Initializing candles for {symbol} from {start_time} to {end_time}")
    result = provider.init_candles(symbol, start_time, end_time, interval)
    print(f"Initialization result: {result}")

    # Demonstrate get_current_time
    print("\nDemonstrating get_current_time:")
    for _ in range(15):  # Try to get 15 candles
        current_time = provider.get_current_time()
        if current_time:
            print(f"Current Time: {current_time}")
        else:
            print("No more candles available or still fetching.")
        time.sleep(1)  # Wait for 1 second before next call

    # Stop the candle fetching
    print("\nStopping candle fetching...")
    provider.stop_candles()

    # Try get_current_time after stopping
    print("\nTrying get_current_time after stopping:")
    final_time = provider.get_current_time()
    if final_time:
        print(f"Final get_current_time result: {final_time}")
    else:
        print("No more candles available.")

if __name__ == "__main__":
    main()