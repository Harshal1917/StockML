import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Define the ticker symbols
stock_ticker = 'INFY'  # Example: Infosys on NSE
stock_option_ticker = 'INFY.NS220818C1840'  # Example: Infosys stock option
index_option_ticker = '^NSEI22000PE'  # Example: NIFTY index option

def fetch_data(ticker, period='1d', interval='5m'):
    try:
        data = yf.download(ticker, period=period, interval=interval)
        if data.empty:
            print(f"No data found for {ticker}")
        return data
    except Exception as e:
        print(f"Failed to download data for {ticker}: {e}")
        return None

# Fetch live data with 1 min resolution for stock
stock_data = fetch_data(stock_ticker)

# Fetch live data with 1 min resolution for stock option
stock_option_data = fetch_data(stock_option_ticker)

# Fetch live data with 1 min resolution for index option
index_option_data = fetch_data(index_option_ticker)

# Fetch historical fundamental data for stock (example: quarterly results, balance sheets, EPS)
try:
    stock_fundamentals = yf.Ticker(stock_ticker)
    quarterly_financials = stock_fundamentals.quarterly_financials
    balance_sheet = stock_fundamentals.balance_sheet
    income_statement = stock_fundamentals.income_stmt
    shareholders = stock_fundamentals.major_holders
except Exception as e:
    print(f"Failed to fetch fundamental data for {stock_ticker}: {e}")

# Display the first few rows of the data
if stock_data is not None:
    print("Stock Data:")
    print(stock_data.head())
if stock_option_data is not None:
    print("Stock Option Data:")
    print(stock_option_data.head())
if index_option_data is not None:
    print("Index Option Data:")
    print(index_option_data.head())

if 'quarterly_financials' in locals():
    print("Quarterly Financials:")
    print(quarterly_financials)
if 'balance_sheet' in locals():
    print("Balance Sheet:")
    print(balance_sheet)
if 'income_statement' in locals():
    print("Income Statement:")
    print(income_statement)
if 'shareholders' in locals():
    print("Shareholders:")
    print(shareholders)

# Function to plot data with detailed time on x-axis
def plot_data(data, ticker, title):
    if data is not None:
        plt.figure(figsize=(12, 6))
        plt.plot(data['Close'], label=f'{ticker} Closing Price')
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.legend()
        plt.grid(True)

        # Format the x-axis to show detailed time
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.xticks(rotation=45)

        plt.show()

# Plot the closing price for stock
plot_data(stock_data, stock_ticker, f'{stock_ticker} Stock Price')

# Plot the closing price for stock option
plot_data(stock_option_data, stock_option_ticker, f'{stock_option_ticker} Stock Option Price')

# Plot the closing price for index option
plot_data(index_option_data, index_option_ticker, f'{index_option_ticker} Index Option Price')