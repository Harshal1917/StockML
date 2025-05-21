
# PS E:\Finance Internship\TASK_5\^NSEI> python .\analyze_nsei_data.py
# Data loaded. Shape: (2458, 8)

# First 5 rows:
#   symbol        date  ...  volume  factor
# 0  ^NSEI  2015-04-24  ...  173600     1.0
# 1  ^NSEI  2015-04-27  ...  171500     1.0
# 2  ^NSEI  2015-04-28  ...  174600     1.0
# 3  ^NSEI  2015-04-29  ...  160400     1.0
# 4  ^NSEI  2015-04-30  ...  267700     1.0

# [5 rows x 8 columns]

# Missing values per column:
# symbol    0
# date      0
# open      0
# close     0
# high      0
# low       0
# volume    0
# factor    0
# dtype: int64

# Infinite values per column:
# open      0
# close     0
# high      0
# low       0
# volume    0
# factor    0
# dtype: int64

# Summary statistics:
#                open         close  ...        volume  factor
# count   2458.000000   2458.000000  ...  2.458000e+03  2458.0 
# mean   13941.361069  13932.018780  ...  3.264895e+05     1.0 
# std     5148.258502   5147.876151  ...  1.936454e+05     0.0 
# min     7023.649902   6970.600098  ...  0.000000e+00     1.0 
# 25%     9877.737549   9875.262451  ...  2.005000e+05     1.0 
# 50%    11735.950195  11725.450195  ...  2.670500e+05     1.0 
# 75%    17804.875488  17796.649902  ...  3.869500e+05     1.0 
# max    26248.250000  26216.050781  ...  1.811000e+06     1.0 

# [8 rows x 6 columns]

# Correlation matrix (top 10 pairs):
# open    high      0.999903
# close   low       0.999886
#         high      0.999882
# open    low       0.999851
# high    low       0.999814
# open    close     0.999754
# volume  high      0.022633
#         open      0.019489
#         close     0.018735
# low     volume    0.014532
# dtype: float64

# --- Recommendations ---
# 1. If you see missing values above, consider using Fillna or DropnaProcessor.
# 2. If you see infinite values, consider using ProcessInf.    
# 3. If you see strong outliers in boxplots, consider RobustZScoreNorm or TanhProcess.
# 4. If features are on different scales, use ZScoreNorm or MinMaxNorm.
# 5. If some features are highly correlated, consider using FilterCol or DropCol to reduce redundancy.

# How this helps:
# 1. Reduces outlier impact by clipping extreme values (between -3 and 3 sigma)
# 2. Makes features more normally distributed using robust median/MAD instead of mean/std
# 3. Improves model stability by creating consistent value ranges












# (qlib_env) E:\Finance Internship\TASK_5\^NSEI>python analyze_nsei_data.py



# Data loaded. Shape: (2458, 8)

# First 5 rows:
#   symbol        date         open  ...          low  volume  factor
# 0  ^NSEI  2015-04-24  8405.700195  ...  8273.349609  173600     1.0
# 1  ^NSEI  2015-04-27  8330.549805  ...  8202.349609  171500     1.0
# 2  ^NSEI  2015-04-28  8215.549805  ...  8185.149902  174600     1.0
# 3  ^NSEI  2015-04-29  8274.799805  ...  8219.200195  160400     1.0
# 4  ^NSEI  2015-04-30  8224.500000  ...  8144.750000  267700     1.0

# [5 rows x 8 columns]

# Missing values per column:
# symbol    0
# date      0
# open      0
# close     0
# high      0
# low       0
# volume    0
# factor    0
# dtype: int64

# Infinite values per column:
# open      0
# close     0
# high      0
# low       0
# volume    0
# factor    0
# dtype: int64

# Summary statistics:
#                open         close  ...        volume  factor
# count   2458.000000   2458.000000  ...  2.458000e+03  2458.0
# mean   13941.361069  13932.018780  ...  3.264895e+05     1.0
# std     5148.258502   5147.876151  ...  1.936454e+05     0.0
# min     7023.649902   6970.600098  ...  0.000000e+00     1.0
# 25%     9877.737549   9875.262451  ...  2.005000e+05     1.0
# 50%    11735.950195  11725.450195  ...  2.670500e+05     1.0
# 75%    17804.875488  17796.649902  ...  3.869500e+05     1.0
# max    26248.250000  26216.050781  ...  1.811000e+06     1.0

# [8 rows x 6 columns]

# Correlation matrix (top 10 pairs):
# open    high      0.999903
# close   low       0.999886
#         high      0.999882
# open    low       0.999851
# high    low       0.999814
# open    close     0.999754
# volume  high      0.022633
#         open      0.019489
#         close     0.018735
# low     volume    0.014532
# dtype: float64

# --- Recommendations ---
# 1. If you see missing values above, consider using Fillna or DropnaProcessor.
# 2. If you see infinite values, consider using ProcessInf.
# 3. If you see strong outliers in boxplots, consider RobustZScoreNorm or TanhProcess.
# 4. If features are on different scales, use ZScoreNorm or MinMaxNorm.
# 5. If some features are highly correlated, consider using FilterCol or DropCol to reduce redundancy.




import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Path to your CSV file
csv_path = r"e:\Finance Internship\TASK_5\^NSEI\^NSEI_raw_10yrs.csv"

from qlib.data.dataset.processor import RobustZScoreNorm

def main_old():
    # Load data with header explicitly defined
    df = pd.read_csv(csv_path, header=0)  # Use first line as header
    print("Data loaded. Shape:", df.shape)
    print("\nFirst 5 rows:")
    print(df.head())

    # 1. Check for missing values
    print("\nMissing values per column:")
    print(df.isnull().sum())

    # 2. Check for infinite values
    print("\nInfinite values per column:")
    print(np.isinf(df.select_dtypes(include=[np.number])).sum())

    # 3. Summary statistics
    print ("\nSummary statistics:")
    print(df.describe())

    # 4. Visualize distributions for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols].hist(bins=50, figsize=(15, 10))
    plt.suptitle("Feature Distributions")
    plt.tight_layout()
    plt.show()

    # 5. Check for outliers using boxplots
    plt.figure(figsize=(15, 6))
    df[numeric_cols].boxplot()
    plt.title("Boxplot for Numeric Features (Outlier Detection)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # 6. Correlation matrix
    corr = df[numeric_cols].corr()
    print("\nCorrelation matrix (top 10 pairs):")
    corr_pairs = corr.abs().unstack().sort_values(ascending=False)
    corr_pairs = corr_pairs[corr_pairs < 1]  # exclude self-correlation
    print(corr_pairs.drop_duplicates().head(10))

    # 7. Print recommendations based on findings
    print("\n--- Recommendations ---")
    print("1. If you see missing values above, consider using Fillna or DropnaProcessor.")
    print("2. If you see infinite values, consider using ProcessInf.")
    print("3. If you see strong outliers in boxplots, consider RobustZScoreNorm or TanhProcess.")
    print("4. If features are on different scales, use ZScoreNorm or MinMaxNorm.")
    print("5. If some features are highly correlated, consider using FilterCol or DropCol to reduce redundancy.")

def visualize_robust_norm():
    # Load raw data
    raw_df = pd.read_csv(csv_path, parse_dates=['date'])
    raw_df = raw_df.set_index(['date', 'symbol']).sort_index()
    
    # Convert columns to feature group format expected by Qlib
    raw_df.columns = pd.MultiIndex.from_tuples(
        [('feature', col) if col in ['open', 'close', 'high', 'low', 'volume'] else (col, '')
         for col in raw_df.columns],
        names=['field', 'col']
    )
    
    # Initialize processor with same parameters as model config
    processor = RobustZScoreNorm(
        fit_start_time="2015-04-24",
        fit_end_time="2024-12-31",
        fields_group="feature",
        clip_outlier=True
    )
    
    # Fit on training period
    fit_df = raw_df.loc["2015-04-24":"2024-12-31"]
    processor.fit(fit_df)
    
    # Apply transformation
    processed_df = processor(raw_df.copy())

    # Visualize before/after for each feature
    features = [('feature', 'open'), ('feature', 'close'), 
               ('feature', 'high'), ('feature', 'low'), 
               ('feature', 'volume')]
    
    plt.figure(figsize=(30, 25))  # Increased figure size
    for i, (field, col) in enumerate(features, 1):
        # Before Processing - Histogram
        plt.subplot(5, 4, (i-1)*4 + 1)
        plt.hist(raw_df[(field, col)], bins=50, alpha=0.7, color='blue')
        plt.title(f'BEFORE: {col} Distribution', fontsize=12)
        plt.grid(True)
        
        # Before Processing - Boxplot
        plt.subplot(5, 4, (i-1)*4 + 2)
        raw_df[(field, col)].plot(kind='box', color='blue', widths=0.6)
        plt.title(f'BEFORE: {col} Outliers', fontsize=12)
        plt.xticks([])
        
        # After Processing - Histogram
        plt.subplot(5, 4, (i-1)*4 + 3)
        plt.hist(processed_df[(field, col)], bins=50, alpha=0.7, color='orange')
        plt.title(f'AFTER: {col} Distribution', fontsize=12)
        plt.grid(True)
        
        # After Processing - Boxplot
        plt.subplot(5, 4, (i-1)*4 + 4)
        processed_df[(field, col)].plot(kind='box', color='orange', widths=0.6)
        plt.title(f'AFTER: {col} Outliers', fontsize=12)
        plt.xticks([])

    plt.suptitle("RobustZScoreNorm Impact Analysis\nLeft Side: Before Processing | Right Side: After Processing", fontsize=16)
    plt.tight_layout()
    plt.subplots_adjust(top=0.95, hspace=0.3)
    plt.show()

    print("\nHow this helps:")
    print("1. Reduces outlier impact by clipping extreme values (between -3 and 3 sigma)")
    print("2. Makes features more normally distributed using robust median/MAD instead of mean/std")
    print("3. Improves model stability by creating consistent value ranges")

# Add to main function
def main():
    main_old()  # keep existing analysis
    visualize_robust_norm()

if __name__ == "__main__":
    main()