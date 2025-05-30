#  Copyright (c) Microsoft Corporation.
#  Licensed under the MIT License.
"""
Qlib provides two kinds of interfaces.
(1) Users could define the Quant research workflow by a simple configuration.
(2) Qlib is designed in a modularized way and supports creating research workflow by code just like building blocks.

The interface of (1) is `qrun XXX.yaml`.  The interface of (2) is script like this, which nearly does the same thing as `qrun XXX.yaml`
"""
import qlib
from qlib.constant import REG_US
from qlib.utils import init_instance_by_config, flatten_dict
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord, PortAnaRecord, SigAnaRecord
from qlib.tests.data import GetData
from qlib.tests.config import CSI300_GBDT_TASK

# Modified US version of the GBDT task
US_GBDT_TASK = {
    "model": {
        "class": "LGBModel",
        "module_path": "qlib.contrib.model.gbdt",
        "kwargs": {
            "loss": "mse",
            "learning_rate": 0.1,
            "num_leaves": 250,
            "max_depth": 8,
            "num_threads": 20,
        },
    },
    "dataset": {
        "class": "DatasetH",
        "module_path": "qlib.data.dataset",
        "kwargs": {
            "handler": {
                "class": "Alpha158",#360
                "module_path": "qlib.contrib.data.handler",
                "kwargs": {
                    "start_time": "2010-01-01",
                    "end_time": "2019-12-31",
                    "fit_start_time": "2010-01-01",
                    "fit_end_time": "2017-12-31",
                    "instruments": "sp500",
                },
            },
            "segments": {
                "train": ("2010-01-01", "2017-12-31"),
                "valid": ("2018-01-01", "2018-12-31"),
                "test": ("2019-01-01", "2019-12-31")
            }
        },
    },
}

if __name__ == "__main__":
    # Use US data
    provider_uri = "C:/Users/ASUS/.qlib/qlib_data/us_data"
    qlib.init(provider_uri=provider_uri, region=REG_US)

    #use for train
    model = init_instance_by_config(US_GBDT_TASK["model"])
    dataset = init_instance_by_config(US_GBDT_TASK["dataset"])

    #use for backtest
    port_analysis_config = {
        "executor": {
            "class": "SimulatorExecutor",
            "module_path": "qlib.backtest.executor",
            "kwargs": {
                "time_per_step": "day",
                "generate_portfolio_metrics": True,
            },
        },
        "strategy": {
            "class": "TopkDropoutStrategy",
            "module_path": "qlib.contrib.strategy.signal_strategy",
            "kwargs": {
                "signal": (model, dataset),
                "topk": 50,
                "n_drop": 5,
            },
        },
        "backtest": {
            "start_time": "2019-01-01",
            "end_time": "2019-12-31",
            "account": 100000000,
            "benchmark": "SPY",
            "exchange_kwargs": {
                "freq": "day",
                "limit_threshold": 0.095,
                "deal_price": "close",
                "open_cost": 0.0005,
                "close_cost": 0.0015,
                "min_cost": 5,
            },
        },
    }

    # NOTE: This line is optional
    # It demonstrates that the dataset can be used standalone.
    example_df = dataset.prepare("train")
    print(example_df.head())

    # start exp
    with R.start(experiment_name="workflow_us"):
        R.log_params(**flatten_dict(US_GBDT_TASK))
        model.fit(dataset)
        R.save_objects(**{"params.pkl": model})

        # prediction
        recorder = R.get_recorder()
        sr = SignalRecord(model, dataset, recorder)
        sr.generate()

        # Signal Analysis
        sar = SigAnaRecord(recorder)
        sar.generate()

        # backtest
        par = PortAnaRecord(recorder, port_analysis_config, "day")
        par.generate()
