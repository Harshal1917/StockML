
import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
import ta  # Technical Analysis library

def add_technical_indicators(df):
    """
    Add technical indicators to the dataframe
    """
    # Initialize indicators
    # Trend Indicators
    df['sma_20'] = ta.trend.sma_indicator(df['Close'], window=20)
    df['ema_20'] = ta.trend.ema_indicator(df['Close'], window=20)
    df['macd'] = ta.trend.macd(df['Close'])
    df['macd_signal'] = ta.trend.macd_signal(df['Close'])
    
    # Momentum Indicators
    df['rsi'] = ta.momentum.rsi(df['Close'], window=14)
    df['stoch'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'])
    df['stoch_signal'] = ta.momentum.stoch_signal(df['High'], df['Low'], df['Close'])
    
    # Volatility Indicators
    df['bb_high'] = ta.volatility.bollinger_hband(df['Close'])
    df['bb_low'] = ta.volatility.bollinger_lband(df['Close'])
    df['bb_mid'] = ta.volatility.bollinger_mavg(df['Close'])
    df['atr'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])
    
    # Volume Indicators
    df['obv'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])
    df['mfi'] = ta.volume.money_flow_index(df['High'], df['Low'], df['Close'], df['Volume'])
    
    return df

def download_stock_data(symbols, start_date, end_date, output_dir):
    """
    Download stock data from yfinance and save in Qlib-compatible CSV format with technical indicators
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for symbol in symbols:
        print(f"Downloading data for {symbol}")
        # Download data from yfinance
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        
        # Add technical indicators
        df = add_technical_indicators(df)
        
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
        
        # Reset index to get date as column
        df = df.reset_index()
        df['date'] = df['Date'].dt.strftime('%Y-%m-%d')
        df['symbol'] = symbol
        
        # Fill NaN values (some indicators produce NaN for initial periods)
        df = df.fillna(method='bfill')
        
        # Select and reorder columns including new indicators
        columns = ['symbol', 'date', 'open', 'close', 'high', 'low', 'volume', 'factor',
                  'sma_20', 'ema_20', 'macd', 'macd_signal', 'rsi', 'stoch', 'stoch_signal',
                  'bb_high', 'bb_low', 'bb_mid', 'atr', 'obv', 'mfi']
        
        df = df[columns]
        
        # Create CSV directory if it doesn't exist
        csv_dir = "C:/Users/ASUS/.qlib/csv_data/my_data_new"
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
    output_dir = "C:/Users/ASUS/.qlib/qlib_data/my_data_new"
    
    download_stock_data(symbols, start_date, end_date, output_dir)
