# Hierarchical Model for Psychometric Function Fitting

This document describes the hierarchical Bayesian model for fitting psychometric functions across multiple blocks, consolidating the previous separate "block fit" and "points fit" approaches.

## Overview

The hierarchical model provides a unified framework for fitting psychometric functions that shares information across blocks through group-level (population) parameters. The model uses the full psychometric function with **guess rate (γ)** and **lapse rate (λ)** parameters:

$$\psi(x) = \gamma + (1 - \gamma - \lambda) \cdot F(x; \text{intercept}, \text{slope})$$

where $F$ is the logistic function. For aggregated data, the model uses a **beta-binomial** likelihood to account for overdispersion.

This approach is particularly beneficial when:

1. You have multiple blocks of data from the same subject or experimental condition
2. Some blocks have sparse data (few trials)
3. You want to estimate both individual block parameters and population-level parameters
4. You want to leverage information sharing (also called "shrinkage" or "partial pooling")
5. You need to account for guess rates and lapse rates in psychophysics experiments

## Mathematical Formulation

### Psychometric Function

The full psychometric function is:

$$\psi(x) = \gamma + (1 - \gamma - \lambda) \cdot \sigma(\text{intercept} + \text{slope} \cdot x)$$

where:
- $\gamma$ (gamma) = **guess rate** - baseline probability of correct response due to guessing
- $\lambda$ (lambda) = **lapse rate** - probability of incorrect response even at high intensities
- $\sigma$ = logistic sigmoid function

### Hierarchical Structure

The model has three levels:

1. **Population level (hyperpriors)**:
   - μ_intercept ~ Normal(0, 2.5)
   - σ_intercept ~ HalfNormal(2.5)
   - μ_slope ~ Normal(0, 2.5)
   - σ_slope ~ HalfNormal(2.5)
   - μ_gamma ~ Beta(1, 19) *(prior mode near 5%)*
   - κ_gamma ~ Gamma(2, 0.1) *(concentration)*
   - μ_lambda ~ Beta(1, 19) *(prior mode near 5%)*
   - κ_lambda ~ Gamma(2, 0.1) *(concentration)*

2. **Block level**:
   - intercept[b] ~ Normal(μ_intercept, σ_intercept) for each block b
   - slope[b] ~ Normal(μ_slope, σ_slope)
   - gamma[b] ~ Beta(μ_gamma × κ_gamma, (1 - μ_gamma) × κ_gamma)
   - lambda[b] ~ Beta(μ_lambda × κ_lambda, (1 - μ_lambda) × κ_lambda)
   - threshold[b] = solution to ψ(x) = 0.5

3. **Trial level** (likelihood):
   - p = γ + (1 - γ - λ) × sigmoid(intercept + slope × Intensity)
   - Result ~ Bernoulli(p)

For aggregated points data (beta-binomial for overdispersion):
   - κ_obs ~ Gamma(2, 0.1) *(overdispersion concentration)*
   - Hits ~ BetaBinomial(n_trials, p × κ_obs, (1 - p) × κ_obs)

### Key Differences from Independent Fits

| Aspect | Independent Fits | Hierarchical Model |
|--------|-----------------|-------------------|
| Parameter sharing | None - each block fit separately | Group-level parameters shared across blocks |
| Sparse data | Poor estimates for blocks with few trials | Shrinkage toward group mean improves estimates |
| Computation | Fast - parallel fitting possible | Slower - joint inference required |
| Use case | Single block or very different blocks | Multiple related blocks |

## Usage

### Basic Example: Trial-Level Data

```python
import polars as pl
from psychoanalyze.data import hierarchical

# Prepare data with multiple blocks
trials_df = pl.DataFrame({
    "Intensity": [0.0, 1.0, 2.0, 3.0, 0.0, 1.0, 2.0, 3.0],
    "Result": [0, 0, 1, 1, 0, 1, 1, 1],
    "Block": [0, 0, 0, 0, 1, 1, 1, 1],
})

# Fit hierarchical model
idata = hierarchical.fit(
    trials_df,
    draws=1000,
    tune=1000,
    chains=2,
    random_seed=42,
)

# Summarize results
summary = hierarchical.summarize_fit(idata)
print(f"Group-level intercept: {summary['mu_intercept']:.2f}")
print(f"Group-level slope: {summary['mu_slope']:.2f}")
print(f"Block thresholds: {summary['threshold']}")
```

### Points-Level Data

For aggregated data (hit counts per intensity level):

```python
from psychoanalyze.data import hierarchical, points

# Aggregate trials to points
points_df = points.from_trials(trials_df)

# Fit using points data
idata = hierarchical.from_points(
    points_df,
    draws=1000,
    tune=1000,
    chains=2,
)
```

### Computing Credible Bands

```python
import numpy as np

# Generate intensity values for prediction
x = np.linspace(-2, 2, 100)

# Compute credible band for block 0
band = hierarchical.curve_credible_band(
    idata,
    x,
    block_idx=0,
    hdi_prob=0.9,
)

# Plot with plotly
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=band["Intensity"],
    y=band["lower"],
    mode="lines",
    line=dict(width=0),
    showlegend=False,
))
fig.add_trace(go.Scatter(
    x=band["Intensity"],
    y=band["upper"],
    fill="tonexty",
    mode="lines",
    line=dict(width=0),
    name="90% Credible Band",
))
```

## When to Use Hierarchical vs Independent Fits

### Use Hierarchical Model When:
- You have **multiple blocks** from related conditions
- Some blocks have **sparse data** (< 50 trials)
- You want to **estimate population parameters**
- Blocks are expected to be **similar** (same subject, condition, etc.)
- You need **uncertainty quantification** across blocks

### Use Independent Fits When:
- You have a **single block**
- Blocks are **very different** (different subjects, conditions)
- You need **fast computation**
- Each block has **plenty of data** (> 100 trials)
- Blocks should not share information

## API Reference

### `hierarchical.fit()`

Fit hierarchical logistic regression to trial data.

**Parameters:**
- `trials`: DataFrame with columns 'Intensity', 'Result', 'Block'
- `draws`: Number of posterior samples per chain (default: 1000)
- `tune`: Number of tuning samples (default: 1000)
- `chains`: Number of MCMC chains (default: 2)
- `target_accept`: Target acceptance probability (default: 0.9)
- `random_seed`: Random seed for reproducibility

**Returns:** `arviz.InferenceData` with posterior samples

### `hierarchical.from_points()`

Fit hierarchical model using aggregated points data.

**Parameters:**
- `points`: DataFrame with 'Intensity', 'Hits', 'n trials', 'Block'
- Same fitting parameters as `fit()`

**Returns:** `arviz.InferenceData` with posterior samples

### `hierarchical.summarize_fit()`

Extract point estimates from posterior.

**Parameters:**
- `idata`: InferenceData from `fit()` or `from_points()`

**Returns:** Dictionary with:
- `mu_intercept`, `sigma_intercept`: Group-level intercept parameters
- `mu_slope`, `sigma_slope`: Group-level slope parameters
- `mu_gamma`, `kappa_gamma`: Group-level guess rate parameters
- `mu_lambda`, `kappa_lambda`: Group-level lapse rate parameters
- `intercept`, `slope`, `threshold`: Arrays of block-specific parameters
- `gamma`: Array of block-specific guess rates
- `lam`: Array of block-specific lapse rates

### `hierarchical.curve_credible_band()`

Compute credible interval for full psychometric curve (including γ and λ).

**Parameters:**
- `idata`: InferenceData from fitting
- `x`: Array of intensity values
- `block_idx`: Which block to compute curve for (default: 0)
- `hdi_prob`: Probability mass for interval (default: 0.9)

**Returns:** DataFrame with 'Intensity', 'lower', 'upper' columns

The credible band properly accounts for uncertainty in all parameters (intercept, slope, gamma, lambda).

## Implementation Details

### PyMC Model

The hierarchical model is implemented using PyMC, which provides:
- Automatic differentiation for gradient-based MCMC (NUTS)
- Efficient sampling with adaptive tuning
- Comprehensive diagnostics via ArviZ
- GPU acceleration support (optional)

### Performance Considerations

- **Computation time** scales with:
  - Number of blocks (linear)
  - Number of trials (linear)
  - Number of chains × (draws + tune)

- **Memory usage** is proportional to:
  - Number of posterior samples stored
  - Number of blocks × parameters

- **Recommendations**:
  - Start with `draws=100, tune=100, chains=1` for testing
  - Use `draws=1000, tune=1000, chains=2` for final analysis
  - Monitor convergence with `az.plot_trace(idata)`
  - Check R-hat values: should be < 1.01

## Examples and Use Cases

### Example 1: Longitudinal Study

Fitting psychometric functions across multiple sessions:

```python
# Data from 5 experimental sessions
sessions_df = pl.DataFrame({
    "Intensity": [...],  # stimulus intensities
    "Result": [...],     # 0/1 outcomes
    "Block": [...],      # session IDs: 0, 1, 2, 3, 4
})

# Fit hierarchical model
idata = hierarchical.fit(sessions_df, draws=1000, tune=1000)
summary = hierarchical.summarize_fit(idata)

# Extract session-specific thresholds
thresholds = summary["threshold"]
print(f"Threshold evolution: {thresholds}")
```

### Example 2: Multi-Subject Study

Fitting subject-specific curves while estimating population parameters:

```python
# Prepare data with subject IDs as blocks
multi_subject_df = trials_df.with_columns(
    pl.col("Subject").alias("Block")
)

# Fit hierarchical model
idata = hierarchical.fit(multi_subject_df)
summary = hierarchical.summarize_fit(idata)

# Population-level estimates
print(f"Population threshold: {summary['mu_intercept'] / -summary['mu_slope']:.2f}")
print(f"Between-subject variability: {summary['sigma_intercept']:.2f}")
```

### Example 3: Handling Sparse Data

Demonstrating shrinkage for blocks with few trials:

```python
# Block 0: Well-sampled (100 trials)
# Block 1: Sparse (10 trials)

# Without hierarchical model (independent fits):
# Block 1 estimate: Unreliable, large uncertainty

# With hierarchical model:
# Block 1 estimate: Shrinks toward group mean, reduced uncertainty

# Compare posterior widths
import arviz as az
az.plot_forest([
    idata.posterior["threshold"].sel(intercept_dim_0=0),
    idata.posterior["threshold"].sel(intercept_dim_0=1),
])
```

## Comparison with Previous Approaches

### Legacy `blocks.fit()` (Independent)

```python
# Old approach - fit each block separately
from psychoanalyze.data import blocks

block_0 = trials_df.filter(pl.col("Block") == 0)
block_1 = trials_df.filter(pl.col("Block") == 1)

idata_0 = blocks.fit(block_0)
idata_1 = blocks.fit(block_1)
# Each fit is independent, no information sharing
```

### Legacy `points.prep_fit()` (Incomplete PyMC approach)

```python
# Old approach - prepare data for external fitting (not fully implemented)
from psychoanalyze.data import points

points_data = points.prep_fit(points_df)
# This was a preparation step that wasn't connected to any fitting
```

### New `hierarchical.fit()` (Unified)

```python
# New approach - unified hierarchical model
from psychoanalyze.data import hierarchical

# Automatically handles multiple blocks with information sharing
idata = hierarchical.fit(trials_df)
# OR use points data directly
idata = hierarchical.from_points(points_df)
```

## Migration Guide

### For Existing Code Using `blocks.fit()`

**Before:**
```python
from psychoanalyze.data import blocks

# Fit each block separately
results = []
for block_id in trials_df["Block"].unique():
    block_trials = trials_df.filter(pl.col("Block") == block_id)
    idata = blocks.fit(block_trials)
    results.append(blocks.summarize_fit(idata))
```

**After:**
```python
from psychoanalyze.data import hierarchical

# Fit all blocks jointly
idata = hierarchical.fit(trials_df)
summary = hierarchical.summarize_fit(idata)

# Extract individual block results
for i, block_id in enumerate(trials_df["Block"].unique().sort()):
    print(f"Block {block_id}: threshold = {summary['threshold'][i]:.2f}")
```

### For Existing Code Using `points.prep_fit()`

**Before:**
```python
from psychoanalyze.data import points

# Prepare data for external fitting (not used)
data_dict = points.prep_fit(points_df)
# This wasn't connected to any actual fitting implementation
```

**After:**
```python
from psychoanalyze.data import hierarchical

# Fit directly using points data
idata = hierarchical.from_points(points_df)
summary = hierarchical.summarize_fit(idata)
```

## References

- Gelman, A., & Hill, J. (2006). *Data Analysis Using Regression and Multilevel/Hierarchical Models*. Cambridge University Press.
- Kruschke, J. K. (2015). *Doing Bayesian Data Analysis* (2nd ed.). Academic Press.
- McElreath, R. (2020). *Statistical Rethinking* (2nd ed.). CRC Press.
- Prins, N., & Kingdom, F. A. A. (2018). *Applying the Model-Comparison Approach to Test Specific Research Hypotheses in Psychophysical Research Using the Palamedes Toolbox*. Frontiers in Psychology.
