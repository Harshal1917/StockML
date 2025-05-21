import qlib
import pandas as pd
from qlib.constant import REG_US
from qlib.contrib.model.gbdt import LGBModel
from qlib.contrib.data.handler import Alpha158
from qlib.utils import init_instance_by_config, flatten_dict
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord
from qlib.data.dataset import DatasetH
import os

def main():
    # Initialize qlib with US market data
    print("Initializing qlib...")
    qlib.init(provider_uri='~/.qlib/qlib_data/us_data', region=REG_US)

    # List of stocks to train on
    selected_stocks = [
        "AAPL",     # Apple
        "MSFT",     # Microsoft
        "GOOGL",    # Google
        "AMZN",     # Amazon
        "META",     # Meta (Facebook)
        "NVDA",     # NVIDIA
        "TSLA",     # Tesla
        "AMD"       # AMD
    ]

    # Set up the data handler configuration
    data_handler_config = {
        "start_time": "2010-01-01",
        "end_time": "2020-12-31",
        "fit_start_time": "2010-01-01",
        "fit_end_time": "2019-12-31",
        "instruments": selected_stocks,
    }

    # Model config for saving
    model_config = {
        "class": "LGBModel",
        "module_path": "qlib.contrib.model.gbdt",
        "kwargs": {
            "loss": 'mse',
            "learning_rate": 0.01,
            "num_leaves": 31,
            "num_boost_round": 100,
            "max_depth": 5,
            "feature_fraction": 0.8,
            "bagging_fraction": 0.8,
            "bagging_freq": 5,
            "verbose": 10
        }
    }

    print(f"\nTraining on stocks: {', '.join(selected_stocks)}")

    # Create data handler
    handler = Alpha158(**data_handler_config)

    # Create dataset
    dataset = DatasetH(
        handler,
        segments={
            "train": ("2010-01-01", "2018-12-31"),
            "valid": ("2019-01-01", "2019-12-31"),
            "test": ("2020-01-01", "2020-12-31")
        }
    )

    # Create model
    model = init_instance_by_config(model_config)

    # Start experiment
    with R.start(experiment_name="lightgbm_tech_stocks"):
        # Save configurations
        R.log_params(**flatten_dict({"model_config": model_config}))
        R.log_params(**flatten_dict({"data_config": data_handler_config}))
        
        # Train model
        print("Training model...")
        model.fit(dataset)
        
        # Save model using qlib's recorder
        R.save_objects(**{
            "model.pkl": model,
            "dataset": dataset,
            "config": {
                "model_config": model_config,
                "data_config": data_handler_config
            }
        })
        
        # Make predictions
        print("Making predictions...")
        pred = model.predict(dataset)
        
        # Record predictions
        sr = SignalRecord(model, dataset, R.get_recorder())
        sr.generate()
        
        # Save experiment ID for later use
        exp_id = R.get_recorder().experiment_id
        with open("experiment_id.txt", "w") as f:
            f.write(str(exp_id))
        
        print(f"\nExperiment ID saved: {exp_id}")
        print("Model and configurations saved in qlib recorder")

        # Print some predictions
        pred_df = pd.DataFrame(pred)
        print("\nSample predictions:")
        print(pred_df.head())

if __name__ == "__main__":
    main()
