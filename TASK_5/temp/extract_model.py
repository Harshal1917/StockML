import qlib
import pandas as pd
from qlib.constant import REG_US
from qlib.workflow import R
from qlib.utils import init_instance_by_config

def load_saved_model():
    # Initialize qlib
    print("Initializing qlib...")
    qlib.init(provider_uri='~/.qlib/qlib_data/us_data', region=REG_US)
    
    # Load experiment ID
    try:
        with open("experiment_id.txt", "r") as f:
            exp_id = f.read().strip()
    except FileNotFoundError:
        print("Error: experiment_id.txt not found. Please run training first.")
        return None

    print(f"Loading experiment {exp_id}...")
    
    # Load the experiment
    with R.start(experiment_name="lightgbm_tech_stocks"):
        recorder = R.get_recorder(experiment_id=exp_id)
        
        # Load model and configurations
        model = recorder.load_object("model.pkl")
        config = recorder.load_object("config")
        dataset = recorder.load_object("dataset")
        
        print("\nModel loaded successfully!")
        print("\nModel Configuration:")
        print(config["model_config"])
        
        print("\nData Configuration:")
        print(config["data_config"])
        
        return model, dataset, config

def make_new_predictions(model, dataset, stocks=None):
    """Make predictions for specific stocks"""
    if stocks is None:
        stocks = ["AAPL", "MSFT", "GOOGL"]  # default stocks
        
    pred = model.predict(dataset)
    pred_df = pd.DataFrame(pred)
    
    # Filter predictions for specific stocks if needed
    if stocks:
        pred_df = pred_df[pred_df.index.get_level_values('instrument').isin(stocks)]
    
    return pred_df

if __name__ == "__main__":
    # Load model and make predictions
    result = load_saved_model()
    if result is not None:
        model, dataset, config = result
        
        # Make new predictions
        print("\nMaking new predictions...")
        predictions = make_new_predictions(model, dataset)
        print("\nSample predictions:")
        print(predictions.head())
