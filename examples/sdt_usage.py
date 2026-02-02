"""
Signal Detection Theory in PsychoAnalyze - Usage Examples
==========================================================

This script demonstrates how to use the new Signal Detection Theory (SDT)
functionality in PsychoAnalyze. SDT provides a framework for quantifying
the ability to discriminate between signal and noise in psychophysical experiments.

Key Features:
- d' (d-prime): Sensitivity measure
- c (criterion): Response bias measure  
- ROC curves: Receiver Operating Characteristic analysis
- AUC: Area Under the ROC Curve
- Integration with existing psychometric function framework
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import polars as pl
from psychoanalyze.analysis import sdt

# =============================================================================
# Example 1: Basic SDT Metrics from Known Rates
# =============================================================================
print("=" * 70)
print("Example 1: Computing SDT metrics from hit rate and false alarm rate")
print("=" * 70)

# Scenario: Observer detects 80% of signals, 20% false alarm rate
hit_rate = 0.80
false_alarm_rate = 0.20

# Calculate sensitivity (d')
d_prime_value = sdt.d_prime(hit_rate, false_alarm_rate)
print(f"\nHit Rate: {hit_rate:.2f}")
print(f"False Alarm Rate: {false_alarm_rate:.2f}")
print(f"d' (sensitivity): {d_prime_value:.3f}")

# Calculate response bias (criterion)
criterion_value = sdt.criterion(hit_rate, false_alarm_rate)
print(f"Criterion (c): {criterion_value:.3f}")
if abs(criterion_value) < 0.1:
    print("  → Unbiased responding")
elif criterion_value > 0:
    print("  → Conservative bias (high threshold)")
else:
    print("  → Liberal bias (low threshold)")

# Calculate likelihood ratio (beta)
beta_value = sdt.beta(hit_rate, false_alarm_rate)
print(f"Beta (β): {beta_value:.3f}")

# =============================================================================
# Example 2: SDT from Trial Data
# =============================================================================
print("\n" + "=" * 70)
print("Example 2: Computing SDT metrics from trial data")
print("=" * 70)

# Simulate trial data from a psychophysical experiment
np.random.seed(42)

# Low intensity trials (noise)
low_intensities = [0.0] * 30
low_results = [int(np.random.random() < 0.25) for _ in range(30)]  # 25% FA rate

# High intensity trials (signal)
high_intensities = [2.0] * 30
high_results = [int(np.random.random() < 0.85) for _ in range(30)]  # 85% hit rate

# Combine into trial DataFrame
trials = pl.DataFrame({
    "Intensity": low_intensities + high_intensities,
    "Result": low_results + high_results,
})

print(f"\nGenerated {len(trials)} trials:")
print(f"  - {sum(trials['Intensity'] < 1.0)} noise trials (low intensity)")
print(f"  - {sum(trials['Intensity'] >= 1.0)} signal trials (high intensity)")

# Compute SDT metrics using intensity 1.0 as criterion
metrics = sdt.sdt_from_trials(trials, criterion_threshold=1.0)

print(f"\nSDT Metrics (criterion at intensity 1.0):")
print(f"  Hit Rate: {metrics['hit_rate']:.3f}")
print(f"  False Alarm Rate: {metrics['false_alarm_rate']:.3f}")
print(f"  d': {metrics['d_prime']:.3f}")
print(f"  Criterion (c): {metrics['criterion_c']:.3f}")
print(f"  Beta (β): {metrics['beta']:.3f}")
print(f"  Signal trials: {metrics['n_signal_trials']}")
print(f"  Noise trials: {metrics['n_noise_trials']}")

# =============================================================================
# Example 3: ROC Curve Analysis
# =============================================================================
print("\n" + "=" * 70)
print("Example 3: Generating ROC curves")
print("=" * 70)

# Generate trial data with gradual intensity progression
np.random.seed(123)
n_trials_per_level = 20
intensities = []
results = []

for intensity in np.linspace(-2, 2, 10):
    # Psychometric function: higher intensity → higher response probability
    p_response = 1 / (1 + np.exp(-1.5 * intensity))
    
    for _ in range(n_trials_per_level):
        intensities.append(intensity)
        results.append(int(np.random.random() < p_response))

trials_roc = pl.DataFrame({
    "Intensity": intensities,
    "Result": results,
})

print(f"\nGenerated {len(trials_roc)} trials across intensity range:")
print(f"  Min intensity: {min(intensities):.2f}")
print(f"  Max intensity: {max(intensities):.2f}")
print(f"  Overall response rate: {np.mean(results):.3f}")

# Generate ROC curve by varying criterion
roc = sdt.roc_curve(trials_roc, n_points=15)

print(f"\nGenerated ROC curve with {len(roc)} points")
print("\nSample ROC points:")
print(roc.head(5))

# Calculate Area Under Curve
auc_value = sdt.auc_from_roc(roc)
print(f"\nArea Under ROC Curve (AUC): {auc_value:.3f}")
if auc_value > 0.9:
    print("  → Excellent discrimination")
elif auc_value > 0.7:
    print("  → Good discrimination")
elif auc_value > 0.5:
    print("  → Fair discrimination")
else:
    print("  → Poor discrimination")

# =============================================================================
# Example 4: Extracting SDT from Psychometric Function Parameters
# =============================================================================
print("\n" + "=" * 70)
print("Example 4: SDT metrics from psychometric function parameters")
print("=" * 70)

# Psychometric function parameters from a fitted model
params = {
    "x_0": 0.0,      # Threshold (50% point)
    "k": 2.0,        # Slope (steepness)
    "gamma": 0.05,   # Guess rate (lower asymptote)
    "lambda": 0.02,  # Lapse rate (upper asymptote deviation)
}

print("\nPsychometric function parameters:")
print(f"  Threshold (x₀): {params['x_0']:.2f}")
print(f"  Slope (k): {params['k']:.2f}")
print(f"  Guess rate (γ): {params['gamma']:.3f}")
print(f"  Lapse rate (λ): {params['lambda']:.3f}")

# Extract SDT-related metrics
sdt_metrics = sdt.sdt_from_params(params)

print("\nCorresponding SDT metrics:")
print(f"  d' (approx): {sdt_metrics['d_prime_approx']:.2f}")
print(f"  Threshold location: {sdt_metrics['threshold']:.2f}")
print(f"  False alarm rate (approx): {sdt_metrics['far_approx']:.3f}")
print(f"  Lapse rate: {sdt_metrics['lapse_rate']:.3f}")
print(f"  Sensitivity range: {sdt_metrics['sensitivity_range']:.3f}")

# =============================================================================
# Example 5: Comparing Performance Across Conditions
# =============================================================================
print("\n" + "=" * 70)
print("Example 5: Comparing SDT metrics across experimental conditions")
print("=" * 70)

# Simulate data from two different experimental conditions
conditions = {}

for condition_name, slope_param in [("Easy", 3.0), ("Hard", 1.0)]:
    np.random.seed(456)
    
    # Generate trials
    intensities = np.random.uniform(-2, 2, 100)
    probs = 1 / (1 + np.exp(-slope_param * intensities))
    results = (np.random.random(100) < probs).astype(int)
    
    trials_cond = pl.DataFrame({
        "Intensity": intensities,
        "Result": results,
    })
    
    # Compute metrics at criterion 0
    metrics = sdt.sdt_from_trials(trials_cond, criterion_threshold=0.0)
    
    conditions[condition_name] = {
        "d_prime": metrics["d_prime"],
        "criterion": metrics["criterion_c"],
        "hit_rate": metrics["hit_rate"],
        "far": metrics["false_alarm_rate"],
    }

print("\nPerformance comparison:")
print(f"{'Condition':<12} {'d_prime':<8} {'c':<8} {'HR':<8} {'FAR':<8}")
print("-" * 45)
for cond_name, metrics in conditions.items():
    print(f"{cond_name:<12} {metrics['d_prime']:<8.3f} {metrics['criterion']:<8.3f} "
          f"{metrics['hit_rate']:<8.3f} {metrics['far']:<8.3f}")

print("\nInterpretation:")
print("  - Higher d' indicates better sensitivity/discrimination")
print("  - Easy condition shows higher d' (better discrimination)")
print("  - Criterion (c) shows response bias (0 = unbiased)")

# =============================================================================
# Summary
# =============================================================================
print("\n" + "=" * 70)
print("Summary: Using SDT in PsychoAnalyze")
print("=" * 70)
print("""
The Signal Detection Theory module provides:

1. Core metrics:
   - d' (d-prime): Sensitivity measure, independent of bias
   - c (criterion): Response bias measure  
   - β (beta): Likelihood ratio measure of bias

2. Analysis tools:
   - compute_hr_far(): Hit rate and false alarm rate from trials
   - sdt_from_trials(): All metrics from trial data
   - roc_curve(): Generate ROC curves
   - auc(): Calculate area under ROC curve

3. Integration with psychometric functions:
   - sdt_from_params(): Extract SDT metrics from fitted parameters
   - Maps γ (guess rate) → FAR, k (slope) → d'

4. Visualization (when plotly is available):
   - plot_roc(): ROC curve plots
   - plot_sdt_metrics(): SDT metrics across criteria

For more information, see the documentation and test suite.
""")
