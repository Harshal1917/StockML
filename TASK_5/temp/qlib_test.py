import qlib
from qlib.constant import REG_US
from qlib.data import D

try:
    # Initialize with US data
    print("Initializing US market data...")
    qlib.init(provider_uri='~/.qlib/qlib_data/us_data', region=REG_US)
    
    # Get sample US stock data (using AAPL as example)
    us_data = D.features(
        ["AAPL"],
        ["$close", "$volume"],
        start_time='2010-01-01',
        end_time='2017-12-31'
    )
    print("US market data sample:")
    print(us_data.head())

except Exception as e:
    print(f"Error occurred: {str(e)}")