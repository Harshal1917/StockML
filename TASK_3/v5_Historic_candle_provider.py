import pandas as pd
import yfinance as yf
import threading
import queue
import time
from datetime import datetime, timedelta

class HistCandleProvider:
    def __init__(self):
        self.data_queue = queue.Queue()  # Initialize the queue
        self.symbol = None
        self.start_time = None
        self.end_time = None
        self.interval = None
        self.is_running = False
        self.fetch_thread = None

    def init_candles(self, symbol, start_time, end_time, interval):
        if self.is_running:
            return "ERROR"  # Session is already active
        # empty the queue
        self.symbol = symbol
        self.start_time = pd.to_datetime(start_time)
        self.end_time = pd.to_datetime(end_time)
        self.interval = interval
        self.is_running = True

        # Start the fetcher thread
        self.fetch_thread = threading.Thread(target=self.fetch_data)
        self.fetch_thread.daemon = True  # Set the thread as a daemon
        self.fetch_thread.start()

        return "SUCCESS"

    def fetch_data(self):
        current_date = self.start_time

        if self.interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']:
            # Fetch daily data for minute/hour intervals
            while current_date <= self.end_time and self.is_running:
                next_date = current_date + timedelta(days=1)
                data = yf.download(self.symbol, start=current_date, end=next_date, interval=self.interval)
                self.add_to_queue(data)
                current_date = next_date

        elif self.interval in ['1d', '5d']:
            # Fetch data every 5 days for daily intervals
            while current_date <= self.end_time and self.is_running:
                next_date = current_date + timedelta(days=5) if self.interval == '5d' else current_date + timedelta(days=1)
                data = yf.download(self.symbol, start=current_date, end=next_date, interval='1d')
                self.add_to_queue(data)
                current_date = next_date

        elif self.interval == '1wk':
            # Fetch data every week
            while current_date <= self.end_time and self.is_running:
                next_date = current_date + timedelta(weeks=1)
                data = yf.download(self.symbol, start=current_date, end=next_date, interval='1wk')
                self.add_to_queue(data)
                current_date = next_date

        elif self.interval == '1mo':
            # Fetch data every month
            while current_date <= self.end_time and self.is_running:
                next_date = current_date + pd.DateOffset(months=1)
                data = yf.download(self.symbol, start=current_date, end=next_date, interval='1mo')
                self.add_to_queue(data)
                current_date = next_date

        elif self.interval == '3mo':
            # Fetch data every 3 months
            while current_date <= self.end_time and self.is_running:
                next_date = current_date + pd.DateOffset(months=3)
                data = yf.download(self.symbol, start=current_date, end=next_date, interval='3mo')
                self.add_to_queue(data)
                current_date = next_date

        self.is_running = False  # Mark session as inactive when done

    def add_to_queue(self, data):
        if not data.empty:
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
                print("Candle added to queue:", candle_data)  # Show the candle data to the user
    
    def get_candle(self):
        if not self.data_queue.empty():
            return self.data_queue.queue[0]  # Peek at the first candle without removing it
        return None  # Return None if the queue is empty

    def pop_candle(self):
        if not self.data_queue.empty():
            self.data_queue.get()  # Remove the first candle from the queue

    def get_current_time(self):  # get_candle
        candle = self.get_candle()  # Use get_candle to retrieve the current candle
        return candle['Date'] if candle else None  # Return the date if candle exists, else None

    def move_to_time(self, target_time):
        if not self.is_running:
            return "ERROR"  # Session is not active

        target_time = pd.Timestamp(target_time)

    def move_to_time(self, target_time):
        if not self.is_running and self.data_queue.empty():
            return "ERROR"  # No data available

        target_time = pd.Timestamp(target_time).floor('D')  # Floor to start of day

        # Check if target_time is within the fetched date range
        if target_time < self.start_time or target_time > self.end_time:
            return "ERROR"  # Target time is outside the fetched date range

        candles_popped = 0
        while not self.data_queue.empty():
            candle = self.data_queue.queue[0]
            candle_date = pd.Timestamp(candle['Date']).floor('D')
            
            if candle_date >= target_time:
                print(f"Moved to date: {candle_date.strftime('%Y-%m-%d')}")
                print(f"Candles popped: {candles_popped}")
                return "SUCCESS"  # Found a candle on or after the target date
            
            self.pop_candle()  # Remove candles before the target date
            candles_popped += 1

        return "ERROR"  # Reached end of queue without finding a suitable candle

    def stop_candles(self):
        self.is_running = False
        if self.fetch_thread and self.fetch_thread.is_alive():
            self.fetch_thread.join(timeout=5)  # Wait for up to 5 seconds for the thread to finish
            if self.fetch_thread.is_alive():
                print("Warning: Fetch thread did not terminate within the timeout period.")