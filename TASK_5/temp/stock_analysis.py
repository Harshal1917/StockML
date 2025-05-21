import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_stock_data(symbol, start_date, end_date):
    """Download stock data from Yahoo Finance"""
    stock = yf.Ticker(symbol)
    df = stock.history(start=start_date, end=end_date)
    print(f"\nData loaded successfully for {symbol}")
    return df

def calculate_metrics(df):
    """Calculate basic technical indicators"""
    # Calculate daily returns
    df['Daily_Return'] = df['Close'].pct_change()
    
    # Calculate moving averages
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    
    # Calculate volatility (20-day rolling standard deviation)
    df['Volatility'] = df['Daily_Return'].rolling(window=20).std()
    
    # Calculate RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df

def analyze_stock(symbol, start_date, end_date):
    """Analyze a stock and print results"""
    # Get data
    df = get_stock_data(symbol, start_date, end_date)
    
    # Calculate metrics
    df = calculate_metrics(df)
    
    # Print analysis results
    print("\nStock Analysis Results:")
    print("-" * 50)
    print(f"Symbol: {symbol}")
    print(f"Period: {start_date} to {end_date}")
    print("-" * 50)
    
    # Calculate key statistics
    total_return = (df['Close'][-1] / df['Close'][0] - 1) * 100
    annualized_return = (1 + total_return/100) ** (365 / len(df)) - 1
    daily_returns = df['Daily_Return'].dropna()
    volatility = daily_returns.std() * np.sqrt(252) * 100
    sharpe_ratio = np.sqrt(252) * daily_returns.mean() / daily_returns.std()
    
    print(f"\nKey Statistics:")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Annualized Return: {annualized_return:.2f}%")
    print(f"Annualized Volatility: {volatility:.2f}%")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    
    # Current indicators
    print(f"\nCurrent Technical Indicators:")
    print(f"RSI (14-day): {df['RSI'][-1]:.2f}")
    print(f"5-day MA: {df['MA5'][-1]:.2f}")
    print(f"20-day MA: {df['MA20'][-1]:.2f}")
    print(f"Current Volatility: {df['Volatility'][-1]*100:.2f}%")
    
    return df

def main():
    # Example usage
    symbol = "AAPL"  # Apple Inc.
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # One year of data
    
    try:
        df = analyze_stock(symbol, start_date, end_date)
        print("\nAnalysis completed successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 