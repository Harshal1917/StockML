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

def download_nifty50_data(start_date, end_date, output_dir):
    """
    Download NIFTY50 data from yfinance and save in Qlib-compatible CSV format
    """
    os.makedirs(output_dir, exist_ok=True)
    
    symbol = '^NSEI'
    print(f"Downloading data for {symbol}")
    
    # Download data from yfinance
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start_date, end=end_date)
    
    # Prepare raw data for Qlib format
    df_raw = df.copy()
    df_raw['factor'] = df_raw['Close'] / df_raw['Close']  # Factor will be 1 as we use adjusted prices
    df_raw = df_raw.reset_index()
    df_raw['date'] = df_raw['Date'].dt.strftime('%Y-%m-%d')
    df_raw['symbol'] = symbol
    
    # Rename columns for raw data
    df_raw = df_raw.rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })
    
    # Select columns for raw data
    raw_columns = ['symbol', 'date', 'open', 'close', 'high', 'low', 'volume', 'factor']
    df_raw = df_raw[raw_columns]
    
    # Save raw data
    raw_output_file = os.path.join(output_dir, f"{symbol}_raw.csv")
    df_raw.to_csv(raw_output_file, index=False)
    print(f"Saved raw data to {raw_output_file}")
    
    # Add technical indicators
    df_with_indicators = add_technical_indicators(df.copy())
    
    # Prepare data with indicators for Qlib format
    df_with_indicators['factor'] = df_with_indicators['Close'] / df_with_indicators['Close']
    df_with_indicators = df_with_indicators.reset_index()
    df_with_indicators['date'] = df_with_indicators['Date'].dt.strftime('%Y-%m-%d')
    df_with_indicators['symbol'] = symbol
    
    # Rename columns for data with indicators
    df_with_indicators = df_with_indicators.rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })
    
    # Fill NaN values
    df_with_indicators = df_with_indicators.bfill()
    
    # Select columns for data with indicators
    indicator_columns = ['symbol', 'date', 'open', 'close', 'high', 'low', 'volume', 'factor',
                        'sma_20', 'ema_20', 'macd', 'macd_signal', 'rsi', 'stoch', 'stoch_signal',
                        'bb_high', 'bb_low', 'bb_mid', 'atr', 'obv', 'mfi']
    
    df_with_indicators = df_with_indicators[indicator_columns]
    
    # Save data with indicators
    indicators_output_file = os.path.join(output_dir, f"{symbol}_with_indicators.csv")
    df_with_indicators.to_csv(indicators_output_file, index=False)
    print(f"Saved data with indicators to {indicators_output_file}")

if __name__ == "__main__":
    # Define the output directory
    output_dir = "E:/Finance Internship/TASK_5/^NSEI"
    
    # Define the date range (last ten years)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=3650)).strftime('%Y-%m-%d')  # 3650 days for 10 years
    
    download_nifty50_data(start_date, end_date, output_dir)
