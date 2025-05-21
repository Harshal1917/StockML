import pandas as pd
import yfinance as yf
import threading
import queue
import time
from datetime import datetime, timedelta

class HistoricQuoteProvider:
    def __init__(self):
        self.data_queue = queue.Queue(maxsize=5)  # Limit queue size to 5 data packs
        self.is_running = False
        self.fetch_thread = None
        self.print_thread = None

    def get_hist_candle_data(self, stock_symbol, start_time, end_time, interval):
        self.is_running = True
        self.fetch_thread = threading.Thread(target=self.fetch_data, args=(stock_symbol, start_time, end_time, interval))
        self.print_thread = threading.Thread(target=self.print_data)
        self.fetch_thread.start()
        self.print_thread.start()

    def fetch_data(self, stock_symbol, start_time, end_time, interval):
        # Convert string dates to datetime objects
        start_date = pd.to_datetime(start_time)
        end_date = pd.to_datetime(end_time)

        # Determine the frequency of data fetching based on the interval
        if interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']:
            # Fetch daily data for minute/hour intervals
            current_date = start_date
            while current_date <= end_date and self.is_running:
                next_date = current_date + timedelta(days=1)
                data = yf.download(stock_symbol, start=current_date, end=next_date, interval=interval)
                self.add_to_queue(data)
                current_date = next_date

        elif interval in ['1d', '5d']:
            # Fetch monthly data for daily intervals
            current_date = start_date
            while current_date <= end_date and self.is_running:
                next_month = current_date + pd.DateOffset(months=1)
                data = yf.download(stock_symbol, start=current_date, end=next_month, interval='1d')
                self.add_to_queue(data)
                current_date = next_month

        elif interval == '1wk':
            # Fetch data every 3 months for weekly intervals
            current_date = start_date
            while current_date <= end_date and self.is_running:
                next_quarter = current_date + pd.DateOffset(months=3)
                data = yf.download(stock_symbol, start=current_date, end=next_quarter, interval='1wk')
                self.add_to_queue(data)
                current_date = next_quarter

        elif interval == '1mo':
            # Fetch yearly data for monthly intervals
            current_date = start_date
            while current_date <= end_date and self.is_running:
                next_year = current_date + pd.DateOffset(years=1)
                data = yf.download(stock_symbol, start=current_date, end=next_year, interval='1mo')
                self.add_to_queue(data)
                current_date = next_year

        elif interval == '3mo':
            # Fetch yearly data for quarterly intervals
            current_date = start_date
            while current_date <= end_date and self.is_running:
                next_year = current_date + pd.DateOffset(years=1)
                data = yf.download(stock_symbol, start=current_date, end=next_year, interval='3mo')
                self.add_to_queue(data)
                current_date = next_year

        self.is_running = False  # Mark fetching as complete

    def add_to_queue(self, data):
        if not data.empty:
            # Add the data pack to the queue
            while self.data_queue.full():
                print("Queue is full, waiting for space...")
                time.sleep(1)  # Wait until there is space in the queue
            self.data_queue.put(data)  # Put the entire data pack in the queue

    def print_data(self):
        while self.is_running or not self.data_queue.empty():
            if not self.data_queue.empty():
                data_pack = self.data_queue.get()
                for index, row in data_pack.iterrows():
                    candle_data = {
                        'Date': index,
                        'Open': float(row['Open']),
                        'High': float(row['High']),
                        'Low': float(row['Low']),
                        'Close': float(row['Close']),
                        'Adj Close': float(row['Adj Close']),
                        'Volume': int(row['Volume']),
                    }
                    print(candle_data)  # Print the data as it is consumed from the queue
            else:
                print("Queue is empty, waiting for data...")
                time.sleep(1)  # Wait until there is data in the queue

    def stop_fetching(self):
        self.is_running = False
        if self.fetch_thread:
            self.fetch_thread.join()
        if self.print_thread:
            self.print_thread.join()

# Main execution
if __name__ == "__main__":
    provider = HistoricQuoteProvider()

    while True:
        # Ask for parameters at runtime
        stock_symbol = input("Enter stock symbol (e.g., AAPL): ")
        start_time = input("Enter start time (YYYY-MM-DD): ")
        end_time = input("Enter end time (YYYY-MM-DD): ")
        interval = input("Enter interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo): ")

        provider.get_hist_candle_data(stock_symbol, start_time, end_time, interval)

        # Wait for both threads to finish
        provider.fetch_thread.join()
        provider.print_thread.join()

        print("All data fetched and printed. Please enter new parameters.")