import qlib
from qlib.config import REG_CN
from qlib.utils import init_instance_by_config
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord

# Initialize Qlib with basic config
provider_uri = "C:/Users/ASUS/.qlib/qlib_data/NSEI_raw"
qlib.init(provider_uri=provider_uri, region=REG_CN)

task = {
    "model": {
        "class": "LGBModel",
        "module_path": "qlib.contrib.model.gbdt",
        "kwargs": {
            "loss": "mse",
            "learning_rate": 0.01,  # Further reduced
            "num_leaves": 20,  # Reduced to prevent overfitting
            "num_boost_round": 1000,  # Increased rounds
            "max_depth": 4,  # Reduced depth
            "feature_fraction": 0.8,  # Added feature sampling
            "bagging_fraction": 0.8,  # Added bagging
            "bagging_freq": 5,
            "verbose": True,
            "early_stopping_rounds": 50,  # Reduced patience
            "eval_metric": ["l2", "mae"],
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
                    "instruments": "all",
                    "start_time": "2023-04-17",
                    "end_time": "2025-04-11",
                    "fit_start_time": "2023-04-17",
                    "fit_end_time": "2024-12-31",
                    "infer_processors": [
                        {
                            "class": "FilterCol",
                            "module_path": "qlib.data.dataset.processor",
                            "kwargs": {
                                "fields_group": "feature",
                                "col_list": [
                                    "RESI5", "RESI10", "RESI20",
                                    "MA5", "MA10", "MA20",
                                    "STD5", "STD10", "STD20",
                                    "MACD", "RSI", "VOL20",
                                    "KMID", "KUP", "KLOW",  # Added Bollinger Bands
                                    "WSMA5", "WSMA10",  # Added weighted MA
                                ]
                            },
                        },
                        {
                            "class": "RobustZScoreNorm",
                            "module_path": "qlib.data.dataset.processor",
                            "kwargs": {
                                "fields_group": "feature",
                                "clip_outlier": True  # Added outlier clipping
                            },
                        },
                    ],
                    "learn_processors": [
                        # Copy the same processors from infer_processors
                    ],
                },
            },
            "segments": {
                "train": ("2023-04-17", "2024-12-31"),
                "valid": ("2025-01-01", "2025-03-01"),
                "test": ("2025-03-02", "2025-04-11"),
            },
        },
    },
}

def main():
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