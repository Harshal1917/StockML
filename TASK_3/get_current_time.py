from v3_Historic_candle_provider import HistCandleProvider
import threading
import time

def demonstrate_get_current_time(provider):
    print("Demonstrating get_current_time functionality:")
    while provider.is_session_active or not provider.data_queue.empty():
        current_time = provider.get_current_time()
        if current_time:
            print(f"Current Time: {current_time}")
        time.sleep(0.5)
    
    print("\nSession ended. Trying get_current_time one more time:")
    final_time = provider.get_current_time()
    print(f"Final get_current_time result: {final_time}")

def main():
    provider = HistCandleProvider()
    
    # Initialize candles
    result = provider.init_candles("AAPL", "2023-01-01", "2023-05-05", "1d")
    print(f"Initialization result: {result}")

    # Start demonstration in a separate thread
    demo_thread = threading.Thread(target=demonstrate_get_current_time, args=(provider,))
    demo_thread.start()

    # Let the session run for a while
    time.sleep(5)

    # Stop the candle fetching
    provider.stop_candles()
    
    # Wait for demonstration to complete
    demo_thread.join()

if __name__ == "__main__":
    main()