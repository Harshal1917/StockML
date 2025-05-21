from tvDatafeed import TvDatafeed, Interval
import pandas as pd

# Create a TvDatafeed object
tv = TvDatafeed(username='harshal197', password='2z7p]k{(Y91a')

# Define the stock symbol and interval
symbol = 'NSE:BANKNIFTY241009C51000 '  # Use 'NSE:INFY' for Infosys on the National Stock Exchange
interval = Interval.in_1_minute   # 1-minute interval

# Fetch historical data for the year 2023
data = tv.get_hist(symbol,exchange='NSE', interval=interval, n_bars=10)  # Adjust n_bars as needed

# Filter data for the year 2023
data = data[data.index.year == 2024]

# Convert to DataFrame if not already
df = pd.DataFrame(data)

# Display the DataFrame
print(df)

# Save to Excel
df.to_excel("stock_data_infy_inr.xlsx", sheet_name='Intraday Data')
print("Data saved to stock_data_infy_inr.xlsx")