# Qlib Processors: Summary & Logic

This document summarizes the main processors in `qlib.data.dataset.processor.py`, describing their logic and typical use cases.

---

## 1. DropnaProcessor
- **Logic:** Drops rows with NaN values in the specified fields group.
- **Use:** Cleans data by removing incomplete samples.

## 2. DropnaLabel
- **Logic:** Inherits from DropnaProcessor, but specifically for the "label" group.
- **Use:** Removes samples with missing labels (not used during inference).

## 3. DropCol
- **Logic:** Drops specified columns from the DataFrame.
- **Use:** Removes unwanted features or labels.

## 4. FilterCol
- **Logic:** Selects only specified columns from a group (e.g., "feature").
- **Use:** Keeps only relevant features for modeling.

## 5. TanhProcess
- **Logic:** Applies the hyperbolic tangent (tanh) function to denoise data, after shifting by 1.
- **Use:** Reduces the impact of outliers/noise in features.

## 6. ProcessInf
- **Logic:** Replaces infinite values in each column with the mean of non-infinite values (per group).
- **Use:** Handles infinite values that may disrupt training.

## 7. Fillna
- **Logic:** Fills NaN values with a specified value (default 0) in the whole DataFrame or a group.
- **Use:** Ensures no missing values remain.

## 8. MinMaxNorm
- **Logic:** Normalizes features to [0, 1] using min-max scaling, fitted on training data.
- **Use:** Scales features for models sensitive to value ranges.

## 9. ZScoreNorm
- **Logic:** Standardizes features using mean and standard deviation (z-score), fitted on training data.
- **Use:** Centers and scales features for models.

## 10. RobustZScoreNorm
- **Logic:** Standardizes features using median and MAD (robust to outliers), fitted on training data.
- **Use:** Normalizes features with outlier resistance.

## 11. CSZScoreNorm
- **Logic:** Applies z-score normalization across instruments for each date (cross-sectional).
- **Use:** Removes cross-sectional mean and scales by std per date.

## 12. CSRankNorm
- **Logic:** Ranks features across instruments for each date, then normalizes to have mean 0 and std ~1.
- **Use:** Converts features to cross-sectional ranks (uniform distribution).

## 13. CSZFillna
- **Logic:** Fills NaN values in each feature group with the mean value for that date (cross-sectional).
- **Use:** Handles missing values in a cross-sectional context.

## 14. HashStockFormat
- **Logic:** Converts DataFrame to a hashed storage format for efficient storage.
- **Use:** Used internally for data storage optimization.

## 15. TimeRangeFlt
- **Logic:** Filters data to only keep instruments that exist throughout a specified time range.
- **Use:** Ensures data consistency for time-based analysis.

---

**Note:**  
- Most normalization processors (`MinMaxNorm`, `ZScoreNorm`, `RobustZScoreNorm`) require fitting on training data and then applying the same transformation to validation/test data.
- Some processors (like `DropnaLabel`) are only used during training, not inference.

---
## Quick Reference Table

| Situation | Recommended Processor(s) |
|-----------|------------------------|
| Missing labels | DropnaLabel |
| Missing feature values | DropnaProcessor / Fillna |
| Outliers | RobustZScoreNorm / TanhProcess |
| Standard scaling | ZScoreNorm |
| Min-max scaling | MinMaxNorm |
| Feature selection | FilterCol / DropCol |
| Cross-sectional operation | CSZScoreNorm / CSRankNorm |
| Infinite values | ProcessInf |
| Consistent time range | TimeRangeFlt |

---
