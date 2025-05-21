import qlib
from qlib.constant import REG_US
from qlib.utils import init_instance_by_config, flatten_dict
from qlib.workflow import R
from qlib.data import D

def main():
    # Initialize Qlib with US data
    qlib.init(provider_uri='C:/Users/ASUS/.qlib/qlib_data/us_data', region=REG_US)

    # Data handler configuration
    data_handler_config = {
        "start_time": "2010-01-01",
        "end_time": "2020-12-31",
        "fit_start_time": "2010-01-01",
        "fit_end_time": "2018-12-31",
        "instruments": "sp500",  # Example: S&P 500 index
    }

    # Task configuration
    task = {
        "model": {
            "class": "LGBModel",
            "module_path": "qlib.contrib.model.gbdt",
            "kwargs": {
                "loss": "mse",
                "learning_rate": 0.01,
                "num_leaves": 31,
                "max_depth": 5,
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
                    "train": ("2010-01-01", "2018-12-31"),
                    "valid": ("2019-01-01", "2019-12-31"),
                    "test": ("2020-01-01", "2020-12-31"),
                },
            },
        },
    }

    # Model initialization and training
    model = init_instance_by_config(task["model"])
    dataset = init_instance_by_config(task["dataset"])

    with R.start(experiment_name="train_model_us"):
        R.log_params(**flatten_dict(task))
        model.fit(dataset)
        R.save_objects(trained_model=model)
        rid = R.get_recorder().id

    # Additional code after training
    # instruments = ["AAPL", "MSFT"]
    # fields = ["$close", "$volume"]
    # df = D.features(instruments, fields, start_time='2010-01-01', end_time='2020-12-31')
    # print(df.head())

if __name__ == '__main__':
    main()
