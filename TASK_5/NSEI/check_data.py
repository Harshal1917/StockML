import qlib
from qlib.data import D

def check_data(provider_uri, symbol):
    # Initialize Qlib with the specified data directory
    qlib.init(provider_uri=provider_uri)

    # Check raw data
    print("Checking Raw Data:")
    df_raw = D.features(
        [symbol],
        ["$close", "$open", "$high", "$low", "$volume"],
        start_time='2020-01-01',
        end_time='2023-12-31'
    )
    print("Raw Data Sample:")
    print(df_raw.head())

    # Check data with indicators
    print("\nChecking Data with Indicators:")
    df_indicators = D.features(
        [symbol],
        ["$close", "$rsi", "$macd", "$sma_20", "$bb_high"],
        start_time='2020-01-01',
        end_time='2023-12-31'
    )
    print("Data with Indicators Sample:")
    print(df_indicators.head())

if __name__ == "__main__":
    # Define the provider URIs for raw and indicators data
    raw_provider_uri = "C:/Users/ASUS/.qlib/qlib_data/NSEI_raw"
    indicators_provider_uri = "C:/Users/ASUS/.qlib/qlib_data/NSEI_indicators"
    
    # Define the symbol
    symbol = "^NSEI"
    
    # Check raw data
    check_data(raw_provider_uri, symbol)
    
    # Check data with indicators
    check_data(indicators_provider_uri, symbol)