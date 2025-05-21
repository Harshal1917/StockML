import pandas as pd
import yfinance as yf
import threading
import queue
import time
from datetime import datetime, timedelta

class HistCandleProvider:
    def __init__(self):
        self.data_queue = None
        self.queue_size = 0
        self.symbol = None
        self.start_time = None
        self.end_time = None
        self.interval = None
        self.is_session_active = False
        self.fetch_thread = None

    def init_candles(self, symbol, start_time, end_time, interval):
        if self.is_session_active:
            return "ERROR"  # Session is already active

        self.symbol = symbol
        self.start_time = pd.to_datetime(start_time)
        self.end_time = pd.to_datetime(end_time)
        self.interval = interval
        self.is_session_active = True

        # Determine queue size based on the interval and time range
        self.queue_size = self.calculate_queue_size()
        self.data_queue = queue.Queue(maxsize=self.queue_size)

        # Start the fetcher thread
        self.fetch_thread = threading.Thread(target=self.fetch_data)
        self.fetch_thread.start()

        return "SUCCESS"

    def calculate_queue_size(self):
        total_minutes = (self.end_time - self.start_time).total_seconds() / 60
        if self.interval in ['1m', '2m', '5m', '15m', '30m', '60m']:
            return int(total_minutes / int(self.interval[:-1]))  # Convert interval to minutes
        elif self.interval in ['1d', '5d', '1wk', '1mo', '3mo']:
            return int(total_minutes / (1440 if self.interval == '1d' else 7200))  # Daily or longer intervals
        return 0

    def fetch_data(self):
        current_date = self.start_time
        while current_date <= self.end_time and self.is_session_active:
            next_date = current_date + timedelta(days=1)

            try:
                # Fetch data based on the interval
                data = yf.download(self.symbol, start=current_date, end=next_date, interval=self.interval)
                if data.empty:
                    print(f"No data found for {self.symbol} on {current_date.date()}.")
                else:
                    self.add_to_queue(data)

            except Exception as e:
                print(f"Error fetching data for {self.symbol} on {current_date.date()}: {e}")

            current_date = next_date

        self.is_session_active = False  # Mark session as inactive when done

    def add_to_queue(self, data):
        if not data.empty:
            while self.data_queue.full():
                print("Queue is full, waiting for space...")
                time.sleep(1)  # Wait until there is space in the queue
            for index, row in data.iterrows():
                candle_data = {
                    'Date': index,
                    'Open': float(row['Open']),
                    'High': float(row['High']),
                    'Low': float(row['Low']),
                    'Close': float(row['Close']),
                    'Adj Close': float(row['Adj Close']),
                    'Volume': int(row['Volume']),
                }
                self.data_queue.put(candle_data)  # Put the entire data pack in the queue

    def get_candle(self):
        if self.is_session_active:
            return self.data_queue.get()  # This will block if the queue is empty
        return None  # Return None if session is not active

    def pop_candle(self):
        if not self.data_queue.empty():
            self.data_queue.get()  # Remove the first candle from the queue

    def get_current_time(self):
        if self.is_session_active:
            candle = self.data_queue.get()  # This will block if the queue is empty
            return candle['Date'] if candle else None
        return None  # Return None if session is not active

    def move_to_time(self, target_time):
        if not self.is_session_active:
            return "ERROR"  # Session is not active

        while not self.data_queue.empty():
            candle = self.data_queue.queue[0]  # Peek at the first candle
            if candle['Date'] >= target_time:
                break
            self.pop_candle()  # Remove the candle if it's before the target time

        if self.data_queue.empty() or self.data_queue.queue[0]['Date'] != target_time:
            return "ERROR"  # Target time not found in the queue
        return "SUCCESS"

    def stop_candles(self):
        self.is_session_active = False
        if self.fetch_thread:
            self.fetch_thread.join()  # Wait for the fetch thread to finish

# Example usage
if __name__ == "__main__":
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
        provider.fetch_thread.join()

        print("All data fetched. Please enter new parameters.")