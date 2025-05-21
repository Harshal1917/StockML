# Ref($close, -2)/Ref($close, -1) - 1
# 12/11 - 1 =
#TODO: newfeature 
#TODO: % return label

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

import sys
import os
import json
from datetime import datetime
import shutil

# Add after other imports
RESULTS_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "train-test") 

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Define your custom features here
# custom_feature_conf = {
#     "price": {
#         "windows": [0],
#         "feature": ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"],  # Add/remove as needed
#     },
#     # Add more feature groups if needed
# }

# custom_feature_conf = {
#     "returns": {
#         "windows": [1],
#         "feature": ["CLOSE"]
#     },
#     "volatility": {
#         "windows": [5],
#         "feature": ["STD(CLOSE, 5)"]
#     },
#     "volume_change": {
#         "windows": [1],
#         "feature": ["VOLUME"]
#     }
# }

custom_feature_conf = {
    # "price": {
    #     "windows": [1],
    #     "feature": ["$close"]  # Add $ prefix to fields
    #     # - Calculation : Daily price values (Open, High, Low, Close, Volume)
    # },
    "returns": {
        "windows": [1],
        "feature": ["($close - Ref($close, 1)) / Ref($close, 1)"]  # Add $ prefix to fields
        # - Calculation : Daily percentage return (Today's Close vs Yesterday's Close)
        # - Example : Close = 100 → 110 = (110-100)/100 = 10% return
        # - Purpose : Captures price momentum        
    },
    "volatility": {
        "windows": [5],
        "feature": ["Std($close, 5)"]  # Keep $ prefix for close
        # - Calculation : 5-day rolling standard deviation of closing prices
        # - Example : Measures how erratic price movements have been recently
        # - Purpose : Identifies periods of high/low market stability        
        
    },
    "volume_change": {
        "windows": [1],
        "feature": ["($volume - Ref($volume, 1)) / Ref($volume, 1)"]  # Add $ prefix to volume
        # - Calculation : Daily percentage change in trading volume
        # - Example : Volume = 1M → 1.2M = 20% increase
        # - Purpose : Shows unusual trading activity        

    }
}

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
                "class": "CustomHandler",
                "module_path": "NSEI.custom.custom_handler",
                "kwargs": {
                    "instruments": ["^NSEI_RAW_10YRS"],
                    "start_time": "2015-04-24",
                    "end_time": "2025-04-11",
                    "fit_start_time": "2015-04-24",
                    "fit_end_time": "2024-12-31",
                    "feature_conf": custom_feature_conf,
                    "infer_processors": [
                        # {
                        #     "class": "DropCol",
                        #     "module_path": "qlib.data.dataset.processor",
                        #     "kwargs": {
                        #         "col_list": ["factor"]
                        #     },
                        # },
                        # {
                        #     "class": "FilterCol",
                        #     "module_path": "qlib.data.dataset.processor",
                        #     "kwargs": {
                        #         "fields_group": "feature",
                        #         "col_list": [
                        #             "open", "close", "volume"
                        #             # You can adjust this list as needed
                        #         ]
                        #     },
                        # },
                        # {
                        #     "class": "RobustZScoreNorm",
                        #     "module_path": "qlib.data.dataset.processor",
                        #     "kwargs": {
                        #         "fields_group": "feature",
                        #         "clip_outlier": True
                        #     },
                        # },
                    ],
                    #use to learn (train)
                    "learn_processors": [
                        # {
                        #     "class": "DropCol",
                        #     "module_path": "qlib.data.dataset.processor",
                        #     "kwargs": {
                        #         "col_list": ["factor"]
                        #     },
                        # },
                        # {
                        #     "class": "FilterCol",
                        #     "module_path": "qlib.data.dataset.processor",
                        #     "kwargs": {
                        #         "fields_group": "feature",
                        #         "col_list": [
                        #             "open", "close", "volume"
                        #             # You can adjust this list as needed
                        #         ]
                        #     },
                        # },
                        # {
                        #     "class": "RobustZScoreNorm",
                        #     "module_path": "qlib.data.dataset.processor",
                        #     "kwargs": {
                        #         "fields_group": "feature",
                        #         "clip_outlier": True
                        #     },
                        # },
                    ],
                },
            },
            "segments": {
                "train": ("2015-04-24", "2022-12-31"),
                "valid": ("2023-01-01", "2023-12-31"),
                "test": ("2024-01-01", "2024-12-31"),
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
    
    # Print available columns``
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
    from qlib.data.dataset import DatasetH
    if not isinstance(dataset, DatasetH):
        raise ValueError("Dataset type mismatch - check handler integration. "
                         "Expected DatasetH, got {}".format(type(dataset)))

    train_data = dataset.prepare("train", col_set=["feature", "label"])
    print("Train data after processing:", train_data.shape)
    print(train_data.head())

    # Diagnostic: count NaNs
    print("\nNaN count per column:")
    print(train_data.isnull().sum())

    print("\nRows with all NaN values:")
    print(train_data[train_data.isnull().all(axis=1)])

    print("\nRows with at least one non-NaN value:")
    print(train_data[train_data.notnull().any(axis=1)].head())

    print("\nFeature Correlations:")
    correlation_matrix = train_data['feature'].corr()
    high_corr_features = np.where(np.abs(correlation_matrix) > 0.95)
    print("Highly correlated features:")
    for i, j in zip(*high_corr_features):
        if i != j:
            print(f"{train_data['feature'].columns[i]} - {train_data['feature'].columns[j]}: {correlation_matrix.iloc[i, j]:.3f}")
    
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

def check_raw_data():
    from qlib.data import D
    df = D.features(
        ["^NSEI_RAW_10YRS"],
        ["$open", "$high", "$low", "$close", "$volume"],
        start_time="2015-04-24",
        end_time="2022-12-31"
    )
    print("Raw data shape:", df.shape)
    print("Raw data NaN count per column:")
    print(df.isnull().sum())
    print(df.head())

def main():
    # Create base directories
    os.makedirs(os.path.join(RESULTS_BASE, "models"), exist_ok=True)
    os.makedirs(os.path.join(RESULTS_BASE, "results"), exist_ok=True)
    
    exp_id = get_experiment_id()
    
    # Initialize Qlib
    provider_uri = initialize_qlib()
    
    # Check raw data before anything else
    check_raw_data()
    
    # Verify instruments
    verify_instruments()
    
    # Load data
    model, dataset = load_data(task)
    
    # Validate data quality before training
    train_data = validate_data_quality(dataset)
    
    # Only proceed to training if data validation passes
    user_input = input("\nDo you want to proceed with training? (y/n): ")
    if user_input.lower() == 'y':
        # Train model and get predictions
        pred, evals_result = train_model(model, dataset)
        
        # Save model and config
        model_dir = save_model_with_config(exp_id, model, task)
        
        # Evaluate and save results
        test_results = test_model(model, dataset, exp_id)
        
        # Additional analysis
        # evaluate_model(model, dataset, evals_result)

def test_model(model, dataset, exp_id):
    """Evaluate model performance and save results"""
    results_dir = os.path.join(RESULTS_BASE, "results", exp_id)
    os.makedirs(results_dir, exist_ok=True)
    
    # 1. Prepare test data
    test_data = dataset.prepare("test", col_set=["feature", "label"])
    true = test_data[("label", "NEXT_CLOSE")]
    
    # 2. Get predictions
    pred = model.predict(dataset, segment="test")
    pred = pd.Series(pred, index=true.index, name="predicted")
    
    # 3. Create comparison DataFrame
    results = pd.DataFrame({
        "actual": true,
        "predicted": pred
    }).dropna()
    
    # 4. Calculate returns-based metrics
    results["actual_returns"] = results["actual"].pct_change()
    results["predicted_returns"] = results["predicted"].pct_change()
    
    # 5. Compute metrics
    mse = mean_squared_error(results["actual"], results["predicted"])
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(results["actual"], results["predicted"])
    r2 = r2_score(results["actual"], results["predicted"])
    corr = results[["actual", "predicted"]].corr().iloc[0,1]
    
    # 6. Directional accuracy
    direction_acc = np.mean(
        (results["actual_returns"] * results["predicted_returns"]) > 0
    )
    
    print(f"\n{' Metric ':-^60}")
    print(f"{'MSE:':<25}{mse:>15.4f}")
    print(f"{'RMSE:':<25}{rmse:>15.4f}")
    print(f"{'MAE:':<25}{mae:>15.4f}")
    print(f"{'R²:':<25}{r2:>15.4f}")
    print(f"{'Correlation:':<25}{corr:>15.4f}")
    print(f"{'Direction Accuracy:':<25}{direction_acc:>15.2%}")
    
    # 7. Visual validation
    plt.figure(figsize=(16, 6))
    
    # Price comparison
    ax1 = plt.subplot(1, 2, 1)
    results[["actual", "predicted"]].plot(ax=ax1, linewidth=2)
    ax1.set_title("Actual vs Predicted Prices", fontsize=14)
    ax1.set_ylabel("Price", fontsize=12)
    ax1.set_xlabel("Date", fontsize=12)
    ax1.legend(["Actual", "Predicted"], fontsize=10)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    # Returns correlation
    ax2 = plt.subplot(1, 2, 2)
    # FIX: Remove c=... and cmap=... to avoid datetime conversion error
    ax2.scatter(results["actual"], results["predicted"], alpha=0.6)
    ax2.set_xlabel("Actual Prices", fontsize=12)
    ax2.set_ylabel("Predicted Prices", fontsize=12)
    ax2.set_title("Prediction Correlation", fontsize=14)
    ax2.grid(True, linestyle='--', alpha=0.6)
    # Annotate correlation
    corr = results[["actual", "predicted"]].corr().iloc[0,1]
    ax2.annotate(f"Corr: {corr:.2f}", xy=(0.05, 0.95), xycoords='axes fraction', fontsize=12,
                 bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3))
    
    plt.tight_layout()
    plot_path = os.path.join(results_dir, "results_comparison.png")
    plt.savefig(plot_path, dpi=150)
    plt.show()
    plt.close()
    
    # Save metrics
    metrics = {
        "MSE": mse,
        "RMSE": rmse,
        "MAE": mae,
        "R2": r2,
        "Correlation": corr,
        "Direction_Accuracy": direction_acc
    }
    
    metrics_path = os.path.join(results_dir, "metrics.json")
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
        
    # Save raw results
    results_path = os.path.join(results_dir, "predictions.csv")
    results.to_csv(results_path)
    
    return results

def evaluate_model(model, dataset, evals_result):
    """Comprehensive model evaluation"""
    # Extract feature names from dataset columns (MultiIndex)
    feature_names = [
        col[1] for col in dataset.prepare("train", col_set=["feature"]).columns
        if col[0] == "feature"
    ]
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'Feature': feature_names,
        'Importance': model.get_feature_importance()
    }).sort_values('Importance', ascending=False).reset_index(drop=True)
    
    print("\nTop 10 Important Features:")
    print(feature_importance.head(10).to_string(index=False))
    
    # Bar plot for feature importance
    plt.figure(figsize=(8, 5))
    plt.barh(feature_importance['Feature'][:10][::-1], feature_importance['Importance'][:10][::-1], color='skyblue')
    plt.xlabel('Importance')
    plt.title('Top 10 Feature Importances')
    plt.tight_layout()
    plt.show()
    
    # Learning curves
    if evals_result:
        plt.figure(figsize=(10, 5))
        for metric, values in evals_result.items():
            plt.plot(values, label=metric)
        plt.title('Learning Curves')
        plt.xlabel('Iterations')
        plt.ylabel('Metric Value')
        plt.legend()
        plt.tight_layout()
        plt.show()



def get_experiment_id():
    """Generate unique experiment ID"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def save_model_with_config(exp_id, model, task_config):
    """Save model and its configuration"""
    model_dir = os.path.join(RESULTS_BASE, "models", exp_id)
    os.makedirs(model_dir, exist_ok=True)
    
    # Try to save using LightGBM's native format if possible
    model_path_txt = os.path.join(model_dir, "model.txt")
    model_path_pkl = os.path.join(model_dir, "model.pkl")
    saved = False

    # Try LightGBM native save
    if hasattr(model, "model") and model.model is not None:
        try:
            model.model.save_model(model_path_txt)
            print(f"Model saved in LightGBM format at: {model_path_txt}")
            saved = True
        except Exception as e:
            print(f"LightGBM save_model failed: {e}")

    # Fallback: Pickle the model object
    if not saved:
        try:
            with open(model_path_pkl, "wb") as f:
                pickle.dump(model, f)
            print(f"Model pickled at: {model_path_pkl}")
            saved = True
        except Exception as e:
            print(f"Pickle save failed: {e}")

    # Save config
    config = {
        "model": task_config["model"],
        "dataset": {
            "instruments": task_config["dataset"]["kwargs"]["handler"]["kwargs"]["instruments"],
            "time_ranges": task_config["dataset"]["kwargs"]["segments"],
            "features": custom_feature_conf
        }
    }
    
    config_path = os.path.join(model_dir, "config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Config saved at: {config_path}")
    
    return model_dir




if __name__ == "__main__":
    main()