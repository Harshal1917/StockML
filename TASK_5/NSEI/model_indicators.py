import qlib
from qlib.utils import init_instance_by_config
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord

# Initialize with indicator data
qlib.init(provider_uri="C:/Users/ASUS/.qlib/qlib_data/NSEI_indicators")

market = "^NSEI"
data_handler_config = {
    "start_time": "2023-01-01",
    "end_time": "2025-04-30", 
    "fit_start_time": "2023-01-01",
    "fit_end_time": "2024-06-30",
    "instruments": market,
}

task = {
    "model": {
        "class": "DEnsembleModel",
        "module_path": "qlib.contrib.model.double_ensemble",
        "kwargs": {
            "base_model": "LGBModel",
            "loss": "mse",
            "num_models": 6,         # Number of base models in ensemble
            "enable_sr": True,        # Enable sample reweighting
            "enable_fs": True,        # Enable feature selection
            "alpha": 0.5,             # Balance between feature selection and sample reweighting
            "bins_sr": 10,            # Number of bins for sample reweighting
            "bins_fs": 5,             # Number of bins for feature selection
            "decay": 0.5,             # Learning rate decay
            "sampling_rate": 0.8,     # Sampling rate for each base model
            # Base model (LightGBM) parameters
            "base_kwargs": {
                "loss": "mse",
                "learning_rate": 0.1,
                "max_depth": 8,
                "num_leaves": 200,
                "num_boost_round": 500,
                "colsample_bytree": 0.85,
                "subsample": 0.8,
                "lambda_l1": 200,
                "lambda_l2": 500,
            },
        },
    },
    "dataset": {
        "class": "DatasetH",
        "module_path": "qlib.data.dataset",
        "kwargs": {
            "handler": {
                "class": "Alpha158",
                "module_path": "qlib.contrib.data.handler",
                "kwargs": data_handler_config,
            },
            "segments": {
                "train": ("2023-01-01", "2024-06-30"),
                "valid": ("2024-07-01", "2024-12-31"),
                "test": ("2025-01-01", "2025-04-30"),
            },
        },
    },
}

# Start experiment
with R.start(experiment_name="nsei_doubleensemble_indicators"):
    # Initialize model and dataset
    model = init_instance_by_config(task["model"])
    dataset = init_instance_by_config(task["dataset"])
    
    # Train model
    model.fit(dataset)
    
    # Generate predictions
    recorder = R.get_recorder()
    sr = SignalRecord(model, dataset, recorder)
    sr.generate()