import qlib
from qlib.config import REG_CN

# initialize qlib with NSEI data
qlib.init(provider_uri="C:/Users/ASUS/.qlib/qlib_data/NSEI_raw_10yrs", region=REG_CN)

from qlib.data.dataset import DatasetH
from qlib.data import D

# Get NSEI data
instruments = D.instruments(market='all')  # First check available instruments
print("\nAvailable instruments:", instruments)

df = D.features(
    instruments, 
    ["$close", "$open", "$high", "$low", "$volume"], 
    start_time='2015-04-24',
    end_time='2025-04-11'
)

print("\nFirst 5 rows of data:")
print(df.head())

print("\nData shape:")
print(df.shape)

print("\nData info:")
print(df.info())

print("\nData statistics:")
print(df.describe())

# Check for missing values
print("\nMissing values:")
print(df.isnull().sum())

# Check date range
print("\nDate range:")
print("Start:", df.index.get_level_values(1).min())
print("End:", df.index.get_level_values(1).max())
