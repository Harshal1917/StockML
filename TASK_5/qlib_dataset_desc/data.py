import qlib
import pandas as pd
from qlib.data import D
from qlib.contrib.data.handler import Alpha158, Alpha360

# Initialize Qlib with the data directory
# For China market
qlib.init(provider_uri="~/.qlib/qlib_data/cn_data")  
# For US market
# qlib.init(provider_uri="~/.qlib/qlib_data/us_data")

def explore_dataset(handler, dataset_name):
    """
    Explore and analyze a dataset handler
    """
    print(f"\n=== Exploring {dataset_name} Dataset ===")
    
    # 1. Get features
    df_feature = handler.fetch(selector="feature")
    print(f"\nFeature Shape: {df_feature.shape}")
    print(f"Number of Features: {len(df_feature.columns)}")
    print("\nSample Features:")
    print(df_feature.head())
    
    # 2. Get labels
    df_label = handler.fetch(selector="label")
    print(f"\nLabel Shape: {df_label.shape}")
    print("\nSample Labels:")
    print(df_label.head())
    
    # 3. Feature Statistics
    print("\nFeature Statistics:")
    print(df_feature.describe())
    
    # 4. Check for missing values
    missing_stats = df_feature.isnull().sum()
    print("\nMissing Values per Feature:")
    print(missing_stats[missing_stats > 0])
    
    return df_feature, df_label

def main():
    # Initialize Qlib
    qlib.init(provider_uri="~/.qlib/qlib_data/cn_data")
    
    # Time range for analysis
    start_time = "2010-01-01"
    end_time = "2020-12-31"
    fit_start_time = "2010-01-01"
    fit_end_time = "2019-12-31"
    
    # Initialize handlers for both datasets
    alpha158_handler = Alpha158(
        instruments="csi300",  # or "sp500" for US market
        start_time=start_time,
        end_time=end_time,
        fit_start_time=fit_start_time,
        fit_end_time=fit_end_time,
        freq="day"
    )
    
    alpha360_handler = Alpha360(
        instruments="csi300",  # or "sp500" for US market
        start_time=start_time,
        end_time=end_time,
        fit_start_time=fit_start_time,
        fit_end_time=fit_end_time,
        freq="day"
    )
    
    # Explore both datasets
    features158, labels158 = explore_dataset(alpha158_handler, "Alpha158")
    features360, labels360 = explore_dataset(alpha360_handler, "Alpha360")
    
    # Compare datasets
    print("\n=== Dataset Comparison ===")
    print(f"Alpha158 Features: {len(features158.columns)}")
    print(f"Alpha360 Features: {len(features360.columns)}")
    
    # Sample analysis for a single stock
    stock_code = "SH600000"  # Example stock code
    print(f"\n=== Sample Analysis for {stock_code} ===")
    
    # Get stock data using Qlib's D API
    stock_data = D.features(
        [stock_code], 
        ["$close", "$volume", "$factor", "$vwap"],
        start_time=start_time,
        end_time=end_time,
        freq="day"
    )
    print("\nRaw Stock Data:")
    print(stock_data.head())
    
    # Calculate some basic statistics
    print("\nBasic Statistics for Close Price:")
    close_prices = stock_data["$close"]
    print(close_prices.describe())

if __name__ == "__main__":
    main()
