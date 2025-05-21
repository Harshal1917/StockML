import qlib
from qlib.config import REG_CN
from qlib.data import D
from qlib.contrib.model.gbdt import LGBModel
from qlib.contrib.strategy.signal_strategy import TopkDropoutStrategy
from qlib.contrib.evaluate import backtest_daily, risk_analysis
from qlib.utils import init_instance_by_config
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord, PortAnaRecord
import pandas as pd
import numpy as np

def init_qlib():
    """Initialize Qlib with China Market data"""
    qlib.init(provider_uri='~/.qlib/qlib_data/cn_data', region=REG_CN)
    print("Qlib initialized successfully.")

def load_data():
    """Load and prepare stock data"""
    # Define the stock pool
    stock_pool = "SH600000"  # Example: Shanghai Stock Exchange stocks
    
    # Define the features we want to use
    fields = [
        "$close", "$open", "$high", "$low", "$volume",
        "Ref($close, 1)", "Ref($close, 2)",  # Previous days' closing prices
        "Mean($close, 5)", "Mean($close, 10)",  # Moving averages
        "Std($close, 5)", "Std($close, 10)",  # Standard deviations
    ]
    
    # Get the features data
    data = D.features(
        instruments=stock_pool,
        fields=fields,
        freq='day',
        start_time='2020-01-01',
        end_time='2023-12-31'
    )
    print("Data loaded successfully.")
    return data

def train_model(data):
    """Train a machine learning model"""
    # Split data into training and testing
    train_end = '2022-12-31'
    valid_start = '2023-01-01'
    valid_end = '2023-12-31'
    
    # Model config
    model_config = {
        "class": "LGBModel",
        "module_path": "qlib.contrib.model.gbdt",
        "kwargs": {
            "loss": "mse",
            "learning_rate": 0.1,
            "num_leaves": 31,
            "num_boost_round": 100,
        },
    }
    
    model = init_instance_by_config(model_config)
    
    # Start recording the experiment
    with R.start(experiment_name="stock_analysis"):
        # Train the model
        model.fit(data)
        R.record("training", {"status": "finished"})
    
    print("Model trained successfully.")
    return model

def backtest_strategy(model):
    """Backtest a trading strategy"""
    strategy_config = {
        "class": "TopkDropoutStrategy",
        "module_path": "qlib.contrib.strategy.signal_strategy",
        "kwargs": {
            "model": model,
            "topk": 5,
            "n_drop": 2,
        },
    }
    
    strategy = init_instance_by_config(strategy_config)
    
    # Run backtest
    backtest_config = {
        "start_time": "2023-01-01",
        "end_time": "2023-12-31",
        "account": 1000000,  # 1M initial capital
        "benchmark": "SH000300",  # CSI 300 Index
        "exchange_kwargs": {
            "limit_threshold": 0.095,
            "deal_price": "close",
            "open_cost": 0.0005,
            "close_cost": 0.0015,
            "min_cost": 5,
        },
    }
    
    # Record backtest results
    with R.start(experiment_name="strategy_backtest"):
        portfolio_metrics = backtest_daily(strategy, **backtest_config)
        R.record("portfolio", portfolio_metrics)
    
    print("Backtest completed successfully.")
    return portfolio_metrics

def analyze_results(portfolio_metrics):
    """Analyze the backtest results"""
    # Calculate risk metrics
    risk_metrics = risk_analysis(
        portfolio_metrics["return"],
        portfolio_metrics["benchmark_return"]
    )
    
    print("\nPortfolio Analysis Results:")
    print(f"Annualized Return: {risk_metrics['annualized_return']:.2%}")
    print(f"Max Drawdown: {risk_metrics['max_drawdown']:.2%}")
    print(f"Sharpe Ratio: {risk_metrics['sharpe']:.2f}")
    print(f"Information Ratio: {risk_metrics['information_ratio']:.2f}")

def main():
    """Main execution function"""
    try:
        # Initialize Qlib
        init_qlib()
        
        # Load data
        data = load_data()
        
        # Train model
        model = train_model(data)
        
        # Backtest strategy
        portfolio_metrics = backtest_strategy(model)
        
        # Analyze results
        analyze_results(portfolio_metrics)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 