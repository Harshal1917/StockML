import qlib
from qlib.constant import REG_US
from qlib.workflow import R
import pandas as pd
from qlib.data import D

def list_available_experiments():
    # Initialize Qlib first
    qlib.init(provider_uri='C:/Users/ASUS/.qlib/qlib_data/us_data', region=REG_US)
    
    # Now list experiments
    print("\nAvailable experiments:")
    exps = R.list_experiments()
    for exp in exps:
        print(f"Experiment name: {exp}")
    return exps

def test_model():
    # Get the experiment
    exp = R.get_exp(experiment_name="train_model_us")
    
    # Print experiment info
    print("\nExperiment Information:")
    print(f"Experiment Name: train_model_us")
    print(f"Experiment ID: {exp.id}")
    
    # List all recorders in the experiment
    recorders = exp.list_recorders()
    print("\nAvailable recorders:")
    
    if not recorders:
        raise ValueError("No recorders found in the experiment.")
    
    # Print recorder information
    for rid in recorders.keys():
        rec = exp.get_recorder(rid)
        print(f"Recorder ID: {rid}")
        print(f"Start Time: {rec.start_time}")
        print(f"End Time: {rec.end_time if hasattr(rec, 'end_time') else 'Not finished'}")
        print("-" * 50)
    
    # Get the most recent recorder (first in the dictionary)
    latest_recorder_id = list(recorders.keys())[0]
    recorder = exp.get_recorder(latest_recorder_id)
    print(f"\nUsing recorder with ID: {latest_recorder_id}")
    
    # Load the model
    try:
        model = recorder.load_object("trained_model")
        print("Successfully loaded the model")
        
        # Print model info if available
        if hasattr(model, 'config'):
            print("\nModel Configuration:")
            print(model.config)
    except Exception as e:
        print(f"Error loading model: {e}")
        return None
    
    # Prepare test data
    instruments = ["AAPL", "MSFT", "GOOGL", "AMZN"]
    fields = ["$close", "$volume"]
    
    print("\nFetching test data...")
    # Get test data for 2020
    test_data = D.features(instruments, fields, 
                          start_time='2020-01-01', 
                          end_time='2020-12-31',
                          freq='day')
    
    print("Making predictions...")
    # Make predictions
    predictions = model.predict(test_data)
    
    # Get actual values
    actual_values = D.features(instruments, ["$close"], 
                             start_time='2020-01-01', 
                             end_time='2020-12-31',
                             freq='day')
    
    # Calculate metrics
    results = pd.DataFrame({
        'Predicted': predictions,
        'Actual': actual_values['$close']
    })
    
    results['Error'] = results['Predicted'] - results['Actual']
    results['Abs_Error'] = abs(results['Error'])
    
    # Print summary statistics
    print("\nPrediction Results:")
    print("Mean Absolute Error:", results['Abs_Error'].mean())
    print("Max Error:", results['Abs_Error'].max())
    print("Min Error:", results['Abs_Error'].min())
    
    return results

if __name__ == "__main__":
    # Initialize Qlib first
    print("Initializing Qlib...")
    qlib.init(provider_uri='C:/Users/ASUS/.qlib/qlib_data/us_data', region=REG_US)
    
    # List available experiments
    experiments = list_available_experiments()
    
    # Run the test if we have experiments
    if experiments:
        try:
            results = test_model()
            if results is not None:
                print("\nSample Predictions vs Actuals:")
                print(results.head())
                
                # Save results to CSV
                results.to_csv('prediction_results.csv')
                print("\nResults saved to 'prediction_results.csv'")
        except Exception as e:
            print(f"Error during testing: {e}")
            import traceback
            print("\nDetailed error:")
            print(traceback.format_exc())
    else:
        print("\nNo experiments found. Please train a model first.")
