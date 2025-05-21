import qlib
from qlib.tests.config import CSI300_GBDT_TASK  # Adjust import if your path differs
from qlib.model.trainer import task_train

# Initialize Qlib (adjust provider_uri to your data location)
qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region="cn")

# Train the model using the task config
recorder = task_train(CSI300_GBDT_TASK, experiment_name="CSI300_LGBM_Alpha158")

# Optionally, you can access results, logs, and artifacts via the recorder
print(f"Experiment ID: {recorder.experiment_id}")