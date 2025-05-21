import pandas as pd

# Read the original CSV
df = pd.read_csv("E:/Finance Internship/TASK_5/^NSEI/^NSEI_raw_10yrs.csv")

# Prepare data for Qlib format
df['symbol'] = df['symbol'].str.replace('^', '')  # Remove ^ from symbol
df = df.rename(columns={
    'close': '$close',
    'open': '$open',
    'high': '$high',
    'low': '$low',
    'volume': '$volume'
})

# Save in Qlib compatible format
output_path = "E:/Finance Internship/TASK_5/custom_dataset/nsei_prepared.csv"
df.to_csv(output_path, index=False)
print("Original data shape:", df.shape)
print("\nSample data:")
print(df.head())