# Signal Detection Theory in PsychoAnalyze

This document describes the Signal Detection Theory (SDT) analysis module added to PsychoAnalyze.

## Overview

Signal Detection Theory provides a framework for quantifying the ability to discriminate between signal and noise in psychophysical experiments. The new `psychoanalyze.analysis.sdt` module implements core SDT metrics and analysis tools that integrate seamlessly with the existing psychometric function framework.

## Key Features

### Core Metrics

- **d' (d-prime)**: Sensitivity measure quantifying discriminability between signal and noise distributions. A d' of 0 indicates chance performance, while larger values indicate better sensitivity.

- **c (criterion)**: Response bias measure. A criterion of 0 indicates unbiased responding, negative values indicate liberal bias (high response rate), and positive values indicate conservative bias (low response rate).

- **β (beta)**: Likelihood ratio measure of bias. Values > 1 indicate conservative bias, < 1 indicate liberal bias, and = 1 indicates unbiased responding.

### Analysis Functions

#### Basic SDT Metrics

```python
from psychoanalyze.analysis import sdt

# Calculate d' from hit rate and false alarm rate
d_prime = sdt.d_prime(hit_rate=0.8, false_alarm_rate=0.2)

# Calculate criterion
criterion = sdt.criterion(hit_rate=0.8, false_alarm_rate=0.2)

# Calculate beta
beta = sdt.beta(hit_rate=0.8, false_alarm_rate=0.2)
```

#### From Trial Data

```python
import polars as pl
from psychoanalyze.analysis import sdt

# Load or generate trial data
trials = pl.DataFrame({
    "Intensity": [0.0, 0.0, 1.0, 1.0, 2.0, 2.0],
    "Result": [0, 1, 0, 1, 1, 1]
})

# Compute all SDT metrics at a specific criterion
metrics = sdt.sdt_from_trials(trials, criterion_threshold=1.0)
# Returns: hit_rate, false_alarm_rate, d_prime, criterion_c, beta,
#          n_signal_trials, n_noise_trials
```

#### ROC Curve Analysis

```python
# Generate ROC curve by varying criterion
roc = sdt.roc_curve(trials, n_points=20)

# Calculate Area Under Curve
auc_value = sdt.auc_from_roc(roc)

# Visualize (requires plotly)
fig = sdt.plot_roc(roc)
fig.show()
```

### Integration with Psychometric Functions

The module provides natural mappings between psychometric function parameters and SDT metrics:

```python
# Extract SDT metrics from fitted psychometric function parameters
params = {
    "x_0": 0.0,      # Threshold (50% point)
    "k": 1.5,        # Slope (steepness)
    "gamma": 0.1,    # Guess rate (lower asymptote)
    "lambda": 0.05,  # Lapse rate (upper asymptote deviation)
}

sdt_metrics = sdt.sdt_from_params(params)
# Returns: d_prime_approx, threshold, far_approx, lapse_rate, sensitivity_range
```

**Key mappings:**
- γ (guess rate) ≈ false alarm rate at low intensities
- k (slope) ≈ d' (sensitivity)
- x₀ (threshold) ≈ location of decision criterion
- λ (lapse rate) = miss rate at high intensities

## Mathematical Background

### d' (d-prime)

$$d' = Z(\text{hit rate}) - Z(\text{false alarm rate})$$

where Z is the inverse normal (probit) transformation.

### Criterion (c)

$$c = -0.5 \times [Z(\text{hit rate}) + Z(\text{false alarm rate})]$$

### Beta (β)

$$\beta = \exp\left(\frac{Z(\text{FAR})^2 - Z(\text{HR})^2}{2}\right)$$

### Area Under ROC Curve

Computed using trapezoidal integration of the hit rate vs. false alarm rate curve.

## Usage Examples

See `examples/sdt_usage.py` for comprehensive usage examples including:
1. Computing SDT metrics from known rates
2. Analyzing trial data
3. Generating and analyzing ROC curves
4. Extracting SDT metrics from psychometric function parameters
5. Comparing performance across experimental conditions

## API Reference

### Core Functions

- `d_prime(hit_rate, false_alarm_rate) -> float`
- `criterion(hit_rate, false_alarm_rate) -> float`
- `beta(hit_rate, false_alarm_rate) -> float`

### Trial Analysis

- `compute_hr_far(trials, criterion, intensity_col="Intensity", result_col="Result") -> dict`
- `sdt_from_trials(trials, criterion_threshold, intensity_col="Intensity", result_col="Result") -> dict`

### ROC Analysis

- `roc_curve(trials, n_points=20, intensity_col="Intensity", result_col="Result") -> DataFrame`
- `auc(hit_rates, false_alarm_rates) -> float`
- `auc_from_roc(roc_df) -> float`

### Parameter Extraction

- `sdt_from_params(params) -> dict`

### Visualization

- `plot_roc(roc_df, show_diagonal=True, show_auc=True, title="ROC Curve") -> Figure`
- `plot_sdt_metrics(trials, n_criteria=20, intensity_col="Intensity", result_col="Result") -> Figure`

## Testing

Comprehensive tests are provided in `tests/test_sdt.py`. Run with:

```bash
pytest tests/test_sdt.py -v
```

## References

1. Green, D. M., & Swets, J. A. (1966). Signal detection theory and psychophysics. Wiley.
2. Macmillan, N. A., & Creelman, C. D. (2004). Detection theory: A user's guide (2nd ed.). Psychology Press.
3. Wickens, T. D. (2001). Elementary signal detection theory. Oxford University Press.

## Notes

- Rates are automatically clipped to (0.001, 0.999) to avoid infinite values from the inverse normal transform.
- For ROC curve generation, some criterion values may not yield valid points if all trials fall on one side of the criterion. These points are omitted from the results.
- The module is fully compatible with both numpy 1.x and 2.x (handles deprecated `np.trapz`).
