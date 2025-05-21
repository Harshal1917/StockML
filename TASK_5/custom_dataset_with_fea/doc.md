## Step 1: Download Data from Yahoo Finance

The `yfinance_data.py` script downloads stock data and saves it in CSV format compatible with Qlib.

```python
# yfinance_data.py
import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

def download_stock_data(symbols, start_date, end_date, output_dir):
    """
    Download stock data from yfinance and save in Qlib-compatible CSV format
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for symbol in symbols:
        print(f"Downloading data for {symbol}")
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        
        # Calculate factor
        df['factor'] = df['Close'] / df['Close']
        
        # Rename columns to match Qlib format
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Format date and add symbol
        df = df.reset_index()
        df['date'] = df['Date'].dt.strftime('%Y-%m-%d')
        df['symbol'] = symbol
        
        # Select required columns
        df = df[['symbol', 'date', 'open', 'close', 'high', 'low', 'volume', 'factor']]
        
        # Save to CSV
        csv_dir = "C:/Users/ASUS/.qlib/csv_data/my_data"
        os.makedirs(csv_dir, exist_ok=True)
        output_file = os.path.join(csv_dir, f"{symbol}.csv")
        df.to_csv(output_file, index=False)
        print(f"Saved data to {output_file}")

if __name__ == "__main__":
    symbols = ['AAPL', 'MSFT']  # Add your desired symbols
    start_date = '2020-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')
    output_dir = "C:/Users/ASUS/.qlib/qlib_data/my_data"
    
    download_stock_data(symbols, start_date, end_date, output_dir)
```

Run the script:
```bash
python yfinance_data.py
```

## Step 2: Convert CSV to Qlib Format

After downloading the data, convert it to Qlib format using the `dump_bin.py` script:

```bash
cd path/to/qlib
python scripts/dump_bin.py dump_all \
    --csv_path C:/Users/ASUS/.qlib/csv_data/my_data \
    --qlib_dir C:/Users/ASUS/.qlib/qlib_data/my_data \
    --include_fields open,close,high,low,volume,factor \
    --date_field_name date \
    --symbol_field_name symbol
```

## Step 3: Verify the Data

Create a test script (`test_data.py`) to verify the converted data:

```python
import qlib
from qlib.data import D

# Initialize Qlib with your data
qlib.init(provider_uri="C:/Users/ASUS/.qlib/qlib_data/my_data")

# Try to load some data
df = D.features(
    ["AAPL"], 
    ["$close", "$open", "$high", "$low", "$volume"], 
    start_time='2020-01-01', 
    end_time='2023-12-31'
)
print(df.head())
```

## Directory Structure

After running all steps, your data will be organized as follows:

C:/Users/ASUS/.qlib/
├── csv_data/
│ └── my_data/
│ ├── AAPL.csv
│ └── MSFT.csv
└── qlib_data/
└── my_data/
├── calendars/
├── instruments/
└── features/

## Notes

1. The factor calculation is simplified (set to 1) since yfinance provides adjusted prices by default
2. Make sure all required directories exist before running the scripts
3. The CSV files must include all required fields: open, close, high, low, volume, factor
4. Date format must be YYYY-MM-DD
5. Symbol names must be consistent across all files

## Troubleshooting

1. If you get a "KeyError" for column names, check that the CSV files have the correct column names
2. If directories don't exist, the scripts will create them automatically
3. Make sure you have write permissions in the output directories

## References

- [Qlib Documentation](https://qlib.readthedocs.io/en/latest/component/data.html)
- [YFinance Documentation](https://pypi.org/project/yfinance/)

