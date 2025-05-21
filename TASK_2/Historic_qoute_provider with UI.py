import pandas as pd
import yfinance as yf
import threading
import queue
import time
import tkinter as tk
from tkinter import messagebox, ttk

class HistoricQuoteProvider:
    def __init__(self):
        self.data_queue = queue.Queue()
        self.is_running = False
        self.callback = None
        self.fetch_thread = None

    def get_hist_candle_data(self, symbol, start_time, end_time, interval, callback):
        self.callback = callback
        self.is_running = True
        self.fetch_thread = threading.Thread(target=self.fetch_data, args=(symbol, start_time, end_time, interval))
        self.fetch_thread.start()

    def fetch_data(self, symbol, start_time, end_time, interval):
        try:
            data = yf.download(symbol, start=start_time, end=end_time, interval=interval)
            for index, row in data.iterrows():
                # Adjust data types
                candle_data = {
                    'Open': float(row['Open']),
                    'High': float(row['High']),
                    'Low': float(row['Low']),
                    'Close': float(row['Close']),
                    'Adj Close': float(row['Adj Close']),
                    'Volume': int(row['Volume']),
                    'Date': index
                }
                self.data_queue.put(candle_data)  # Put data in the queue
        except Exception as e:
            print(f"Error fetching data: {e}")
        self.is_running = False  # Mark fetching as complete

# GUI Class
class App:
    def __init__(self, root):
        self.provider = HistoricQuoteProvider()
        self.root = root
        self.root.title("Historic Quote Provider")

        # Input fields
        tk.Label(root, text="Symbol:").grid(row=0, column=0)
        self.symbol_entry = tk.Entry(root)
        self.symbol_entry.grid(row=0, column=1)

        tk.Label(root, text="Start Date:").grid(row=1, column=0)
        self.start_entry = tk.Entry(root)
        self.start_entry.grid(row=1, column=1)

        tk.Label(root, text="End Date:").grid(row=2, column=0)
        self.end_entry = tk.Entry(root)
        self.end_entry.grid(row=2, column=1)

        tk.Label(root, text="Interval:").grid(row=3, column=0)
        self.interval_entry = tk.Entry(root)
        self.interval_entry.grid(row=3, column=1)

        # Buttons
        self.start_button = tk.Button(root, text="Start", command=self.start_data_fetching)
        self.start_button.grid(row=4, column=0)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_data_fetching)
        self.stop_button.grid(row=4, column=1)

        # Table for displaying data
        self.tree = ttk.Treeview(root, columns=("Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"), show='headings')
        self.tree.heading("Date", text="Date")
        self.tree.heading("Open", text="Open")
        self.tree.heading("High", text="High")
        self.tree.heading("Low", text="Low")
        self.tree.heading("Close", text="Close")
        self.tree.heading("Adj Close", text="Adj Close")
        self.tree.heading("Volume", text="Volume")
        self.tree.grid(row=5, column=0, columnspan=2)

        # Flag to control data display
        self.display_data_flag = True

    def start_data_fetching(self):
        symbol = self.symbol_entry.get()
        start_time = self.start_entry.get()
        end_time = self.end_entry.get()
        interval = self.interval_entry.get()

        self.provider.get_hist_candle_data(symbol, start_time, end_time, interval, self.display_data)

        # Start a thread to process the fetched data
        threading.Thread(target=self.process_data).start()

    def stop_data_fetching(self):
        self.display_data_flag = False  # Stop displaying data
        messagebox.showinfo("Info", "Data printing stopped.")

    def process_data(self):
        while self.provider.is_running or not self.provider.data_queue.empty():
            if not self.provider.data_queue.empty():
                candle_data = self.provider.data_queue.get()
                if self.display_data_flag:  # Only display data if the flag is True
                    # Insert the candle data into the table
                    self.tree.insert("", "end", values=(candle_data['Date'], 
                                                         candle_data['Open'], 
                                                         candle_data['High'], 
                                                         candle_data['Low'], 
                                                         candle_data['Close'], 
                                                         candle_data['Adj Close'], 
                                                         candle_data['Volume']))
            time.sleep(1)  # Adjust processing frequency as needed

    def display_data(self, candle_data):
        # This method is called to display the fetched candle data
        if self.display_data_flag:  # Only display data if the flag is True
            self.tree.insert("", "end", values=(candle_data['Date'], 
                                                 candle_data['Open'], 
                                                 candle_data['High'], 
                                                 candle_data['Low'], 
                                                 candle_data['Close'], 
                                                 candle_data['Adj Close'], 
                                                 candle_data['Volume']))

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()