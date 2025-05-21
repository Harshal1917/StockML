import qlib
from qlib.config import REG_CN
from qlib.utils import init_instance_by_config
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord

# Initialize Qlib with custom config
provider_uri = "C:/Users/ASUS/.qlib/qlib_data/NSEI_raw_10yrs"
qlib.init(
    provider_uri=provider_uri,
    region=REG_CN,
    expression_cache=None
)

task = {
    "model": {
        "class": "LGBModel",
        "module_path": "qlib.contrib.model.gbdt",
        "kwargs": {
            "loss": "mse",
            "learning_rate": 0.0001,    # Further reduced for finer learning
            "num_leaves": 50,           # Increased leaf count
            "num_boost_round": 5000,    # Significantly increased iterations
            "max_depth": 10,            # Increased depth
            "feature_fraction": 0.8,    # Adjusted back up
            "bagging_fraction": 0.8,    # Adjusted back up
            "bagging_freq": 5,          # Adjusted for stability
            "verbose": True,
            "early_stopping_rounds": 300,  # Significantly increased patience
            "eval_metric": ["l2", "mae"],
            "min_data_in_leaf": 20,     # Added to prevent overfitting
            "lambda_l1": 0.1,           # Added L1 regularization
            "lambda_l2": 0.1,           # Added L2 regularization
        },
    },
    "dataset": {
        "class": "DatasetH",
        "module_path": "qlib.data.dataset",
        "kwargs": {
            "handler": {
                "class": "Alpha158",
                "module_path": "qlib.contrib.data.handler",
                "kwargs": {
                    "instruments": ["^NSEI_RAW_10YRS"],  # Changed to list format
                    "start_time": "2015-04-24",
                    "end_time": "2025-04-11",
                    "fit_start_time": "2015-04-24",
                    "fit_end_time": "2024-12-31",
                    "infer_processors": [
                        {
                            "class": "FilterCol",
                            "module_path": "qlib.data.dataset.processor",
                            "kwargs": {
                                "fields_group": "feature",
                                "col_list": [
                                    "RESI5", "RESI10", "RESI20",  # Price momentum
                                    "MA5", "MA10", "MA20",        # Moving averages
                                    "STD5", "STD10", "STD20",     # Volatility
                                    "MACD",                       # Trend
                                    "RSI",                        # Momentum
                                    "VOL20",                      # Volume
                                    "KMID", "KUP", "KLOW",       # Bollinger Bands
                                    "WSMA5", "WSMA10",           # Weighted MA
                                ]
                            },
                        },
                        {
                            "class": "RobustZScoreNorm",
                            "module_path": "qlib.data.dataset.processor",
                            "kwargs": {
                                "fields_group": "feature",
                                "clip_outlier": True
                            },
                        },
                    ],
                    "learn_processors": [
                        {
                            "class": "FilterCol",
                            "module_path": "qlib.data.dataset.processor",
                            "kwargs": {
                                "fields_group": "feature",
                                "col_list": [
                                    "RESI5", "RESI10", "RESI20",  
                                    "MA5", "MA10", "MA20",        
                                    "STD5", "STD10", "STD20",     
                                    "MACD",                       
                                    "RSI",                        
                                    "VOL20",                      
                                    "KMID", "KUP", "KLOW",       
                                    "WSMA5", "WSMA10",           
                                ]
                            },
                        },
                        {
                            "class": "RobustZScoreNorm",
                            "module_path": "qlib.data.dataset.processor",
                            "kwargs": {
                                "fields_group": "feature",
                                "clip_outlier": True
                            },
                        },
                    ],
                },
            },
            "segments": {
                "train": ("2015-04-24", "2023-12-31"),
                "valid": ("2024-01-01", "2024-12-31"),
                "test": ("2025-01-01", "2025-04-11"),
            },
        },
    },
}

def main():
    # Correct way to list instruments
    from qlib.data import D
    instruments = D.instruments(market="all")
    print("\nAvailable instruments:", instruments)
    
    # Initialize model and dataset
    model = init_instance_by_config(task["model"])
    dataset = init_instance_by_config(task["dataset"])

    # Print dataset info
    print("\nDataset information:")
    train_data = dataset.prepare("train", col_set=["feature", "label"])
    print("Training data shapes:")
    for k, v in train_data.items():
        print(f"{k} shape: {v.shape if hasattr(v, 'shape') else len(v)}")

    # Start experiment
    with R.start(experiment_name="nsei_lightgbm_basic"):
        # Train model
        print("\nTraining model...")
        model.fit(dataset)
        
        # Make predictions
        print("\nMaking predictions...")
        pred = model.predict(dataset)
        print("\nSample predictions:")
        print(pred[:5])  # Show first 5 predictions

if __name__ == "__main__":
    main()