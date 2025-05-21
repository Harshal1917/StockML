# Qlib Dataset Descriptions

## Common Characteristics

Both datasets:
- Are stored in `.bin` format (Qlib's proprietary format)
- Available for both US and China markets
- Use adjusted prices normalized to 1 on first trading day
- Include data for stocks in CSI300 (China) or SP500 (US)

## Alpha158 Dataset

### Overview
A tabular dataset containing 158 handcrafted alpha factors engineered from market data.

### Configuration Parameters
```python
alpha158_config = {
    "start_time": "2008-01-01",      # Data start time
    "end_time": "2020-08-01",        # Data end time
    "fit_start_time": "2008-01-01",  # Training data start time
    "fit_end_time": "2014-12-31",    # Training data end time
    "instruments": "csi300",         # or "sp500" for US market
    "freq": "day"                    # Data frequency
}
```

### Feature Categories

1. **Price Features**
   - KBAR based features (KMID, KLEN, KUP, KLOW)
   - Price ratios and differences
   - Normalized prices

2. **Volume Features**
   - Volume ratios
   - VSTD (Volume Standard Deviation)
   - VWAP (Volume Weighted Average Price)
   - Volume-price correlations

3. **Technical Indicators**
   - ROC (Rate of Change)
   - MA (Moving Average) with different windows
   - MACD (Moving Average Convergence Divergence)
   - RSI (Relative Strength Index)
   - BETA (Price change rate)
   - RSQR (R-squared of price regression)
   - RESI (Residuals of price regression)
   - MAX/MIN (Price extremes)

4. **Volatility Factors**
   - STD (Standard Deviation)
   - BETA
   - RSQR
   - RESI
   - Volatility ratios

## Alpha360 Dataset

### Overview
A sequential dataset focusing on raw price and volume data, specifically designed for deep learning models.

### Configuration Parameters
```python
alpha360_config = {
    "start_time": "2008-01-01",      # Data start time
    "end_time": "2020-08-01",        # Data end time
    "fit_start_time": "2008-01-01",  # Training data start time
    "fit_end_time": "2014-12-31",    # Training data end time
    "instruments": "csi300",         # or "sp500" for US market
    "freq": "day",                   # Data frequency
    "seq_len": 60                    # Length of historical sequence
}
```

### Feature Set (360 features total)
For each of the past 60 days:
1. **Price Data** (normalized)
   - Close price
   - Open price
   - High price
   - Low price
   - VWAP (Volume Weighted Average Price)

2. **Volume Data**
   - Trading volume (normalized)

## Label Definition

Both datasets use the same label definition:
```python
label = "Ref($close, -2)/Ref($close, -1) - 1"
```

This represents:
- The price change from T+1 to T+2
- Used instead of T to T+1 for China market due to trading rules
- Returns are calculated using adjusted prices

## Data Processing Details

### Normalization Methods
1. **Price Normalization**
   ```python
   normalized_price = price / first_day_price
   ```

2. **Volume Normalization**
   ```python
   normalized_volume = volume / rolling_mean(volume, window=N)
   ```

### Missing Data Handling
- NaN values are processed by data handlers
- Forward filling for minor gaps
- Stocks with excessive missing data are filtered out

### Data Frequency Options
```python
frequency_options = {
    "day": "Daily data",
    "week": "Weekly data",
    "month": "Monthly data"
}
```

## Usage Example

```python
from qlib.contrib.data.handler import Alpha158, Alpha360

# Initialize Alpha158
handler_158 = Alpha158(
    instruments="csi300",
    start_time="2010-01-01",
    end_time="2020-12-31",
    fit_start_time="2010-01-01",
    fit_end_time="2019-12-31",
    freq="day"
)

# Initialize Alpha360
handler_360 = Alpha360(
    instruments="csi300",
    start_time="2010-01-01",
    end_time="2020-12-31",
    fit_start_time="2010-01-01",
    fit_end_time="2019-12-31",
    freq="day"
)

# Get features
features_158 = handler_158.fetch(selector="feature")
features_360 = handler_360.fetch(selector="feature")

# Get labels
labels_158 = handler_158.fetch(selector="label")
labels_360 = handler_360.fetch(selector="label")
```

## Model Compatibility

### Alpha158
- Traditional ML models (LightGBM, XGBoost)
- Linear models
- Tree-based models
- Feature importance analysis possible

### Alpha360
- Deep Learning models (LSTM, GRU)
- Transformer architectures
- CNN-based models
- Models that can capture temporal dependencies

## References

- [Qlib Data Preparation Documentation](https://qlib.readthedocs.io/en/latest/component/data.html#data-preparation)
- [Qlib Format Dataset](https://qlib.readthedocs.io/en/latest/component/data.html#qlib-format-dataset)
- [Price Adjustment Discussion](https://github.com/microsoft/qlib/issues/991#issuecomment-1075252402)

For more detailed information about specific components, please refer to the [official Qlib documentation](https://qlib.readthedocs.io/en/latest/).
