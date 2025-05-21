# Import necessary libraries
import pandas as pd
import yfinance as yf
import os

# Load the Excel file
file_path = 'test_nse_stock_code.xlsx'
data = pd.read_excel(file_path)

#here add destination folder path
destination_folder = 'E:\Finance Internship\TASK_1_stock_Data_from_yfinance\data'

os.makedirs(destination_folder,exist_ok=True)

# Iterate through each row in the DataFrame
for index, row in data.iterrows():
    stock_symbol = row.iloc[0] + '.NS'  # Append .NS to the stock symbol
    start_date = pd.to_datetime(row.iloc[1])  # Start date
    end_date = pd.to_datetime(row.iloc[2])    # End date
    interval = row.iloc[3]                    # Interval

    # print(start_date," ",end_date," ",interval)
    all_data = pd.DataFrame()

    # Fetch stock data for the specified interval
    stock_data = yf.download(stock_symbol, start=start_date, end=end_date, interval=interval)
    all_data = stock_data

    # Save the data to an Excel file named after the stock symbol
    all_data.to_excel(os.path.join(destination_folder,f"{row.iloc[0]}.xlsx"))  # Save to Excel