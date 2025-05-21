import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from v7_Historic_candle_provider import HistCandleProvider
import threading
from datetime import datetime

class SimpleFetcherApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Simple Stock Data Fetcher")
        self.master.geometry("600x500")

        self.provider = HistCandleProvider()
        self.create_widgets()
    
    def create_widgets(self):
        # Input fields
        tk.Label(self.master, text="Symbol:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.symbol_entry = tk.Entry(self.master)
        self.symbol_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        tk.Label(self.master, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.start_date_entry = tk.Entry(self.master)
        self.start_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        tk.Label(self.master, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.end_date_entry = tk.Entry(self.master)
        self.end_date_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        tk.Label(self.master, text="Interval:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.interval_combo = ttk.Combobox(self.master, values=['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'])
        self.interval_combo.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        self.interval_combo.set("1d")

        # Fetch button
        self.fetch_button = tk.Button(self.master, text="Fetch Data", command=self.fetch_data)
        self.fetch_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Operation buttons
        self.get_candle_button = tk.Button(self.master, text="Get Candle", command=self.get_candle, state=tk.DISABLED)
        self.get_candle_button.grid(row=5, column=0, pady=5)

        self.pop_candle_button = tk.Button(self.master, text="Pop Candle", command=self.pop_candle, state=tk.DISABLED)
        self.pop_candle_button.grid(row=5, column=1, pady=5)

        self.get_time_button = tk.Button(self.master, text="Get Current Time", command=self.get_current_time, state=tk.DISABLED)
        self.get_time_button.grid(row=6, column=0, pady=5)

        self.move_time_button = tk.Button(self.master, text="Move to Time", command=self.move_to_time, state=tk.DISABLED)
        self.move_time_button.grid(row=6, column=1, pady=5)

        self.stop_button = tk.Button(self.master, text="Stop Candles", command=self.stop_candles, state=tk.DISABLED)
        self.stop_button.grid(row=7, column=0, columnspan=2, pady=10)

        # Display area
        self.display = tk.Text(self.master, height=15, width=70, wrap=tk.WORD)
        self.display.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        scrollbar = tk.Scrollbar(self.master, command=self.display.yview)
        scrollbar.grid(row=8, column=2, sticky='ns')
        self.display['yscrollcommand'] = scrollbar.set

        # Configure grid weights for resizing
        self.master.grid_rowconfigure(8, weight=1)  # Allow the display area to expand
        self.master.grid_columnconfigure(1, weight=1)  # Allow the entry fields to expand

    def fetch_data(self):
        symbol = self.symbol_entry.get()
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        interval = self.interval_combo.get()

        if not all([symbol, start_date, end_date, interval]):
            messagebox.showerror("Error", "Please fill in all fields")
            return

        self.display.delete('1.0', tk.END)
        self.display.insert(tk.END, "Fetching data...\n")
        self.fetch_button.config(state=tk.DISABLED)

        def fetch_thread():
            result = self.provider.init_candles(symbol, start_date, end_date, interval)
            if result == "ERROR":
                self.display.insert(tk.END, "Failed to initialize candles. A session might already be active.\n")
            else:
                self.display.insert(tk.END, "Data fetched successfully. You can now use the operation buttons.\n")
                self.enable_buttons()

            self.fetch_button.config(state=tk.NORMAL)

        threading.Thread(target=fetch_thread, daemon=True).start()

    def enable_buttons(self):
        for button in [self.get_candle_button, self.pop_candle_button, self.get_time_button, 
                       self.move_time_button, self.stop_button]:
            button.config(state=tk.NORMAL)

    def get_candle(self):
        candle = self.provider.get_candle()
        if candle:
            self.display.insert(tk.END, f"Current Candle: {candle}\n")
        else:
            self.display.insert(tk.END, "No candle available.\n")

    def pop_candle(self):
        self.provider.pop_candle()
        self.display.insert(tk.END, "Candle popped.\n")

    def get_current_time(self):
        time = self.provider.get_current_time()
        if time:
            # Convert the datetime object to a string for display
            time_str = time.strftime("%Y-%m-%d %H:%M:%S")
            self.display.insert(tk.END, f"Current Time: {time_str}\n")
        else:
            self.display.insert(tk.END, "No current time available.\n")

    def move_to_time(self):
        target_time_str = simpledialog.askstring("Input", "Enter target date (YYYY-MM-DD):")
        if target_time_str:
            try:
                target_time = datetime.strptime(target_time_str, "%Y-%m-%d")
                self.display.insert(tk.END, f"Attempting to move to date: {target_time_str}\n")
                result = self.provider.move_to_time(target_time)
                
                if result == "SUCCESS":
                    current_candle = self.provider.get_candle()
                    if current_candle:
                        candle_date = current_candle['Date'].strftime("%Y-%m-%d")
                        self.display.insert(tk.END, f"Moved to date: {candle_date}\n")
                        self.display.insert(tk.END, f"Next available candle: {current_candle}\n")
                    else:
                        self.display.insert(tk.END, "Moved successfully, but no candle data available.\n")
                else:
                    self.display.insert(tk.END, f"Failed to move to date: {target_time_str}. This date may be outside the available data range.\n")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")

    def stop_candles(self):
        self.provider.stop_candles()
        self.display.insert(tk.END, "Candles stopped.\n")
        for button in [self.get_candle_button, self.pop_candle_button, self.get_time_button, 
                       self.move_time_button, self.stop_button]:
            button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleFetcherApp(root)
    root.mainloop()