# (qlib_env) E:\Finance Internship\TASK_5\custom_dataset_with_fea>python custom_data.py
# [1316:MainThread](2025-04-15 11:39:55,991) INFO - qlib.Initialization - [config.py:420] - default_conf: client.
# [1316:MainThread](2025-04-15 11:40:08,755) INFO - qlib.Initialization - [__init__.py:74] - qlib successfully initialized based on client settings.
# [1316:MainThread](2025-04-15 11:40:08,755) INFO - qlib.Initialization - [__init__.py:76] - data_path={'__DEFAULT_FREQ': WindowsPath('C:/Users/ASUS/.qlib/qlib_data/my_data_new')}
#                           $close      $open      $high       $low      $volume    $sma_20    $ema_20     $macd       $rsi   $bb_high
# instrument datetime
# AAPL       2020-01-02  72.716072  71.721016  72.776596  71.466812  135480400.0  75.545418  75.919594  0.954442  70.820572  79.493553
#            2020-01-03  72.009102  71.941315  72.771729  71.783943  146322800.0  75.545418  75.919594  0.954442  70.820572  79.493553
#            2020-01-06  72.582901  71.127861  72.621635  70.876068  118387200.0  75.545418  75.919594  0.954442  70.820572  79.493553
#            2020-01-07  72.241547  72.592590  72.849220  72.021233  108872000.0  75.545418  75.919594  0.954442  70.820572  79.493553
#            2020-01-08  73.403641  71.943748  73.706268  71.943748  132079200.0  75.545418  75.919594  0.954442  70.820572  79.493553


import qlib
from qlib.config import REG_CN

# initialize qlib with your data
qlib.init(provider_uri="C:/Users/ASUS/.qlib/qlib_data/my_data_new")

# try to load some data
from qlib.data.dataset import DatasetH
from qlib.data import D

# Get stock data
df = D.features(
    ["AAPL"], 
    ["$close", "$open", "$high", "$low", "$volume",
     "$sma_20", "$ema_20", "$macd", "$rsi", "$bb_high"], 
    start_time='2020-01-01', 
    end_time='2023-12-31'
)
print(df.head())