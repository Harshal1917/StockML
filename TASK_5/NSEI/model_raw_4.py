# Ref($close, -2)/Ref($close, -1) - 1
# 12/11 - 1 =


import qlib
from qlib.config import REG_CN
from qlib.utils import init_instance_by_config
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord
from qlib.data import D
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score



task = {
    "model": {
        "class": "LGBModel",
        "module_path": "qlib.contrib.model.gbdt",
        "kwargs": {
            "loss": "mse",
            "learning_rate": 0.01,      # Increased from 0.0001
            "num_leaves": 31,           # Reduced from 50
            "num_boost_round": 1000,    # Reduced from 5000
            "max_depth": 8,             # Adjusted from 10
            "feature_fraction": 0.85,    # Slightly increased
            "bagging_fraction": 0.85,    # Slightly increased
            "bagging_freq": 5,
            "verbose": True,
            "early_stopping_rounds": 50, # Reduced from 300
            "eval_metric": ["l2", "mae"],
            "min_data_in_leaf": 30,     # Increased from 20
            "lambda_l1": 0.05,          # Reduced from 0.1
            "lambda_l2": 0.05,          # Reduced from 0.1
            "objective": "regression",   # Added explicit objective
            "force_row_wise": True,      # Added for better numeric stability
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
                    #DONE#TODO: how this works?
                    #DONE#TODO: how this works?
                    #DONE#TODO: how this works?
                    "start_time": "2015-04-24",
                    "end_time": "2025-04-11",
                    "fit_start_time": "2015-04-24",
                    "fit_end_time": "2024-12-31",
                    #DONE#TODO: how this works? processors- how to use infer and learn processors?
                    #use to infer (valid/test)
                    "infer_processors": [
                        {
                            "class": "DropCol",
                            "module_path": "qlib.data.dataset.processor",
                            "kwargs": {
                                "col_list": ["factor"]
                            },
                        },
                        {
                            "class": "FilterCol",
                            "module_path": "qlib.data.dataset.processor",
                            "kwargs": {
                                "fields_group": "feature",
                                "col_list": [
                                    "open", "close", "volume"
                                    # You can adjust this list as needed
                                ]
                            },
                        },
                        {
                            #TODO: which col are we using?
                            "class": "RobustZScoreNorm",
                            "module_path": "qlib.data.dataset.processor",
                            "kwargs": {
                                "fields_group": "feature",
                                "clip_outlier": True
                            },
                        },
                    ],
                    #use to learn (train)
                    "learn_processors": [
                        {
                            "class": "DropCol",
                            "module_path": "qlib.data.dataset.processor",
                            "kwargs": {
                                "col_list": ["factor"]
                            },
                        },
                        {
                            "class": "FilterCol",
                            "module_path": "qlib.data.dataset.processor",
                            "kwargs": {
                                "fields_group": "feature",
                                "col_list": [
                                    "open", "close", "volume"
                                    # You can adjust this list as needed
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
                "train": ("2015-04-24", "2022-12-31"),  # Reduced training period
                "valid": ("2023-01-01", "2023-12-31"),  # Full year for validation
                "test": ("2024-01-01", "2024-12-31"),   # More recent test data
            },
        },
    },
}


def initialize_qlib():
    """Initialize Qlib with custom configuration"""
    provider_uri = "C:/Users/ASUS/.qlib/qlib_data/NSEI_raw_10yrs"
    qlib.init(
        provider_uri=provider_uri,
        region=REG_CN,
        expression_cache=None
    )
    return provider_uri

def load_data(task_config):
    """Load and prepare the dataset"""
    model = init_instance_by_config(task_config["model"])
    dataset = init_instance_by_config(task_config["dataset"])
    
    # Print dataset info
    print("\nDataset information:")
    
    train_data = dataset.prepare("train", col_set=["feature", "label"])

    print("Training data shapes:")
    for k, v in train_data.items():
        print(f"{k} shape: {v.shape if hasattr(v, 'shape') else len(v)}")
    
    # Print available columns
    print("\nAvailable columns in the dataset:")
    print(train_data.columns)
    
    return model, dataset

def train_model(model, dataset):
    """Train the model and make predictions"""
    with R.start(experiment_name="nsei_lightgbm_basic"):
        print("\nTraining model...")
        evals_result = {}
        model.fit(dataset, evals_result=evals_result)
        
        # Print training metrics
        print("\nTraining Metrics:")
        for metric, values in evals_result.items():
            print(f"{metric}: {values}")
        
        print("\nMaking predictions...")
        pred = model.predict(dataset)
        print("\nSample predictions:")
        print(pred[:5])
        
        return pred, evals_result

def verify_instruments():
    """Verify available instruments"""
    instruments = D.instruments(market="all")
    print("\nAvailable instruments:", instruments)

def validate_data_quality(dataset):
    """Validate data quality and feature distributions"""
    train_data = dataset.prepare("train", col_set=["feature", "label"])
    
    # Add feature correlation analysis
    if ('feature' in train_data):
        print("\nFeature Correlations:")
        correlation_matrix = train_data['feature'].corr()
        high_corr_features = np.where(np.abs(correlation_matrix) > 0.95)
        print("Highly correlated features:")
        for i, j in zip(*high_corr_features):
            if i != j:
                print(f"{train_data['feature'].columns[i]} - {train_data['feature'].columns[j]}: {correlation_matrix.iloc[i, j]:.3f}")
    
    # Add feature importance analysis
    return train_data

def analyze_predictions(predictions, dataset):
    """Analyze model predictions"""
    test_data = dataset.prepare("test", col_set=["label"])
    test_labels = test_data["label"]
    
    # Calculate metrics
    mse = mean_squared_error(test_labels, predictions)
    mae = mean_absolute_error(test_labels, predictions)
    r2 = r2_score(test_labels, predictions)
    
    print("\nModel Performance Metrics:")
    print(f"MSE: {mse:.6f}")
    print(f"MAE: {mae:.6f}")
    print(f"R2 Score: {r2:.6f}")
    
    # Return metrics instead of undefined train_data
    return {
        'mse': mse,
        'mae': mae,
        'r2': r2
    }

def main():
    # Initialize Qlib
    provider_uri = initialize_qlib()
    
    # Verify instruments
    verify_instruments()
    
    # Load data
    model, dataset = load_data(task)
    
    # Validate data quality before training
    train_data = validate_data_quality(dataset)
    
    # Only proceed to training if data validation passes
    user_input = input("\nDo you want to proceed with training? (y/n): ")
    if user_input.lower() == 'y':
        predictions = train_model(model, dataset)

def evaluate_model(model, dataset, evals_result):
    """Comprehensive model evaluation"""
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': dataset.feature_names,
        'importance': model.get_feature_importance()
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Important Features:")
    print(feature_importance.head(10))
    
    # Learning curves
    if evals_result:
        plt.figure(figsize=(10, 5))
        for metric, values in evals_result.items():
            plt.plot(values, label=metric)
        plt.title('Learning Curves')
        plt.xlabel('Iterations')
        plt.ylabel('Metric Value')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    main()