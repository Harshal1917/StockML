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

        self.symbol = symbol
        self.start_time = pd.to_datetime(start_time)
        self.end_time = pd.to_datetime(end_time)
        self.interval = interval
        self.is_running = True

        # Start the fetcher thread
        self.fetch_thread = threading.Thread(target=self.fetch_data)
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

    def stop_candles(self):
        self.is_running = False
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