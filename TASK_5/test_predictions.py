import qlib
import pandas as pd
import numpy as np
from qlib.constant import REG_US
from qlib.data import D
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord
from sklearn.metrics import mean_squared_error, r2_score

def evaluate_predictions():
    # Initialize qlib
    print("Initializing qlib...")
    qlib.init(provider_uri='~/.qlib/qlib_data/us_data', region=REG_US)
    
    # Load the experiment recorder
    with R.start(experiment_name="lightgbm_tech_stocks"):
        recorder = R.get_recorder()
        
        # Load predictions
        pred = recorder.load_object("pred.pkl")
        
        # Get actual data for comparison
        actual_data = D.features(
            ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "AMD"],
            ["$close"],
            start_time="2020-01-01",
            end_time="2020-12-31"
        )
        
        # Calculate metrics
        mse = mean_squared_error(actual_data, pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(actual_data, pred)
        
        print("\nModel Evaluation Metrics:")
        print(f"Mean Squared Error: {mse:.4f}")
        print(f"Root Mean Squared Error: {rmse:.4f}")
        print(f"R-squared Score: {r2:.4f}")
        
        # Print sample comparison
        print("\nSample Predictions vs Actual:")
        comparison = pd.DataFrame({
            'Actual': actual_data.iloc[:5],
            'Predicted': pred.iloc[:5]
        })
        print(comparison)

if __name__ == "__main__":
    evaluate_predictions()
