# cd E:\Finance Internship\TASK_5\qlib
# python scripts/dump_bin.py dump_all --csv_path C:/Users/ASUS/.qlib/csv_data/my_data --qlib_dir C:/Users/ASUS/.qlib/qlib_data/my_data --include_fields open,close,high,low,volume,factor --date_field_name date --symbol_field_name symbol


import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

def download_stock_data(symbols, start_date, end_date, output_dir):
    """
    Download stock data from yfinance and save in Qlib-compatible CSV format
    
    Args:
        symbols (list): List of stock symbols
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        output_dir (str): Directory to save CSV files
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for symbol in symbols:
        print(f"Downloading data for {symbol}")
        # Download data from yfinance
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        
        # Calculate factor before renaming columns
        # Factor = adjusted close / unadjusted close
        df['factor'] = df['Close'] / df['Close']  # This will be 1 as yfinance provides adjusted prices
        
        # Rename columns to match Qlib format
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Reset index to get date as column
        df = df.reset_index()
        df['date'] = df['Date'].dt.strftime('%Y-%m-%d')
        df['symbol'] = symbol
        
        # Select and reorder columns
        df = df[['symbol', 'date', 'open', 'close', 'high', 'low', 'volume', 'factor']]
        
        # Create CSV directory if it doesn't exist
        csv_dir = "C:/Users/ASUS/.qlib/csv_data/my_data"
        os.makedirs(csv_dir, exist_ok=True)
        
        # Save to CSV
        output_file = os.path.join(csv_dir, f"{symbol}.csv")
        df.to_csv(output_file, index=False)
        print(f"Saved data to {output_file}")

if __name__ == "__main__":
    # Example usage
    symbols = ['AAPL', 'MSFT']  # Add your desired symbols
    start_date = '2020-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')
    output_dir = "C:/Users/ASUS/.qlib/qlib_data/my_data"
    
    download_stock_data(symbols, start_date, end_date, output_dir)
