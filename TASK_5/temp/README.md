# AI-Based Stock Market Analysis with Qlib

This project demonstrates how to use Microsoft's Qlib framework for AI-based stock market analysis and trading strategy development.

## Setup Instructions

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Download the Qlib stock market data:
```bash
# For Chinese market data
python scripts/get_data.py qlib_data --target_dir ~/.qlib/qlib_data/cn_data --region cn
```

3. Run the analysis:
```bash
python qlib_stock_analysis.py
```

## Features

The implementation includes:

1. **Data Loading**: Loads historical stock data with various features including:
   - Price data (open, high, low, close)
   - Volume data
   - Technical indicators (moving averages, standard deviations)

2. **Model Training**: Uses LightGBM model to predict stock performance with:
   - Automated feature engineering
   - Model training and validation
   - Experiment tracking

3. **Trading Strategy**: Implements a top-k dropout strategy that:
   - Selects top performing stocks
   - Manages portfolio rebalancing
   - Includes transaction costs

4. **Performance Analysis**: Calculates key metrics including:
   - Annualized returns
   - Maximum drawdown
   - Sharpe ratio
   - Information ratio

## Configuration

You can modify the following parameters in `qlib_stock_analysis.py`:

- `stock_pool`: Stock universe for trading
- `fields`: Features used for prediction
- `start_time` and `end_time`: Analysis period
- Trading strategy parameters in `strategy_config`
- Backtest parameters in `backtest_config`

## Results

The program will output:
1. Training progress information
2. Backtest results
3. Portfolio performance metrics

## Notes

- The default configuration uses Chinese A-share market data
- Transaction costs and trading constraints are included in the backtest
- All experiments are automatically logged for future reference 