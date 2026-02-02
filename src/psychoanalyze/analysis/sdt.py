"""Signal Detection Theory (SDT) analysis for psychophysical data.

This module implements core Signal Detection Theory metrics and analysis functions
for analyzing psychophysical experiments. SDT provides a framework for quantifying
the ability to discern between signal and noise.

Key metrics:
    - d' (d-prime): Sensitivity measure, quantifies discriminability
    - c (criterion): Response bias, quantifies decision threshold
    - ROC curves: Receiver Operating Characteristic curves
    - AUC: Area Under the ROC Curve

Example:
    >>> import polars as pl
    >>> from psychoanalyze.analysis import sdt
    >>> 
    >>> # Calculate d' from rates
    >>> d_prime = sdt.d_prime(hit_rate=0.8, false_alarm_rate=0.2)
    >>> 
    >>> # Generate ROC curve from trial data
    >>> trials = pl.DataFrame({"Intensity": [...], "Result": [...]})
    >>> roc_df = sdt.roc_curve(trials)
"""

import numpy as np
import polars as pl
from scipy import stats


def d_prime(hit_rate: float, false_alarm_rate: float) -> float:
    """Calculate d' (d-prime) sensitivity index.
    
    d' measures the separation between signal and noise distributions in units
    of standard deviation. A d' of 0 indicates no discriminability, while larger
    values indicate better sensitivity.
    
    Uses the inverse normal (probit) transformation:
        d' = Z(hit_rate) - Z(false_alarm_rate)
    
    Args:
        hit_rate: Proportion of hits (0 to 1). P(response=1 | signal present)
        false_alarm_rate: Proportion of false alarms (0 to 1). 
            P(response=1 | signal absent)
    
    Returns:
        d' value. Positive values indicate sensitivity, 0 indicates chance.
        
    Note:
        Rates are clipped to (0.001, 0.999) to avoid infinite values from
        the inverse normal transform.
    
    Example:
        >>> d_prime(0.8, 0.2)
        1.68...
        >>> d_prime(0.5, 0.5)  # Chance performance
        0.0
    """
    # Clip rates to avoid infinite values from norm.ppf at 0 or 1
    hr = np.clip(hit_rate, 0.001, 0.999)
    far = np.clip(false_alarm_rate, 0.001, 0.999)
    
    return float(stats.norm.ppf(hr) - stats.norm.ppf(far))


def criterion(hit_rate: float, false_alarm_rate: float) -> float:
    """Calculate decision criterion (c).
    
    The criterion measures response bias - how conservative or liberal the
    observer is in making positive responses. A criterion of 0 indicates
    unbiased responding, negative values indicate liberal bias (high response
    rate), and positive values indicate conservative bias (low response rate).
    
    Calculated as:
        c = -0.5 * [Z(hit_rate) + Z(false_alarm_rate)]
    
    Args:
        hit_rate: Proportion of hits (0 to 1)
        false_alarm_rate: Proportion of false alarms (0 to 1)
    
    Returns:
        Criterion value. 0 = unbiased, negative = liberal, positive = conservative.
    
    Example:
        >>> criterion(0.8, 0.2)
        0.0
        >>> criterion(0.9, 0.7)  # Liberal bias
        -0.84...
    """
    # Clip rates to avoid infinite values
    hr = np.clip(hit_rate, 0.001, 0.999)
    far = np.clip(false_alarm_rate, 0.001, 0.999)
    
    return float(-0.5 * (stats.norm.ppf(hr) + stats.norm.ppf(far)))


def beta(hit_rate: float, false_alarm_rate: float) -> float:
    """Calculate likelihood ratio beta (β).
    
    Beta is an alternative measure of response bias expressed as a likelihood
    ratio. Values > 1 indicate conservative bias, < 1 indicate liberal bias,
    and = 1 indicates unbiased responding.
    
    Calculated as the ratio of signal and noise distribution heights at the
    decision criterion:
        β = exp(c × d')
    
    Args:
        hit_rate: Proportion of hits (0 to 1)
        false_alarm_rate: Proportion of false alarms (0 to 1)
    
    Returns:
        Beta value. 1 = unbiased, >1 = conservative, <1 = liberal.
    
    Example:
        >>> beta(0.8, 0.2)
        1.0
    """
    # Clip rates to avoid infinite values
    hr = np.clip(hit_rate, 0.001, 0.999)
    far = np.clip(false_alarm_rate, 0.001, 0.999)
    
    z_hr = stats.norm.ppf(hr)
    z_far = stats.norm.ppf(far)
    
    # Beta = ratio of signal to noise density at criterion
    # Equivalent to exp(z_far * z_far / 2 - z_hr * z_hr / 2)
    return float(np.exp((z_far**2 - z_hr**2) / 2))


def compute_hr_far(
    trials: pl.DataFrame,
    criterion: float,
    intensity_col: str = "Intensity",
    result_col: str = "Result",
) -> dict[str, float]:
    """Compute hit rate and false alarm rate at a given criterion.
    
    Splits trials into signal (intensity >= criterion) and noise 
    (intensity < criterion) categories and computes response rates.
    
    Args:
        trials: DataFrame with trial data
        criterion: Intensity threshold separating signal from noise
        intensity_col: Name of intensity column (default: "Intensity")
        result_col: Name of result column with binary outcomes (default: "Result")
    
    Returns:
        Dictionary with keys:
            - 'hit_rate': P(response=1 | signal)
            - 'false_alarm_rate': P(response=1 | noise)
            - 'n_signal_trials': Number of signal trials
            - 'n_noise_trials': Number of noise trials
    
    Example:
        >>> trials = pl.DataFrame({
        ...     "Intensity": [0, 0, 1, 1, 2, 2],
        ...     "Result": [0, 1, 0, 1, 1, 1]
        ... })
        >>> compute_hr_far(trials, criterion=1.0)
        {'hit_rate': 0.75, 'false_alarm_rate': 0.5, ...}
    """
    # Separate signal and noise trials
    signal_trials = trials.filter(pl.col(intensity_col) >= criterion)
    noise_trials = trials.filter(pl.col(intensity_col) < criterion)
    
    # Compute rates
    n_signal = len(signal_trials)
    n_noise = len(noise_trials)
    
    if n_signal == 0 or n_noise == 0:
        msg = (
            f"Cannot compute HR/FAR: need trials both above and below criterion "
            f"({criterion}). Got {n_signal} signal trials and {n_noise} noise trials."
        )
        raise ValueError(msg)
    
    hit_rate = float(signal_trials[result_col].mean())
    false_alarm_rate = float(noise_trials[result_col].mean())
    
    return {
        "hit_rate": hit_rate,
        "false_alarm_rate": false_alarm_rate,
        "n_signal_trials": n_signal,
        "n_noise_trials": n_noise,
    }


def sdt_from_trials(
    trials: pl.DataFrame,
    criterion_threshold: float,
    intensity_col: str = "Intensity",
    result_col: str = "Result",
) -> dict[str, float]:
    """Compute all SDT metrics from trial data at a given criterion.
    
    Convenience function that computes hit rate, false alarm rate, d', 
    criterion (c), and beta from trial data.
    
    Args:
        trials: DataFrame with trial data
        criterion_threshold: Intensity threshold separating signal from noise
        intensity_col: Name of intensity column (default: "Intensity")
        result_col: Name of result column (default: "Result")
    
    Returns:
        Dictionary containing:
            - hit_rate, false_alarm_rate
            - d_prime, criterion_c, beta
            - n_signal_trials, n_noise_trials
    
    Example:
        >>> trials = pl.DataFrame({
        ...     "Intensity": [0, 0, 1, 1, 2, 2],
        ...     "Result": [0, 0, 1, 1, 1, 1]
        ... })
        >>> metrics = sdt_from_trials(trials, criterion_threshold=1.0)
        >>> metrics['d_prime']
        1.68...
    """
    rates = compute_hr_far(trials, criterion_threshold, intensity_col, result_col)
    
    hr = rates["hit_rate"]
    far = rates["false_alarm_rate"]
    
    return {
        **rates,
        "d_prime": d_prime(hr, far),
        "criterion_c": criterion(hr, far),
        "beta": beta(hr, far),
    }


def sdt_from_params(params: dict[str, float]) -> dict[str, float]:
    """Extract SDT metrics from psychometric function parameters.
    
    Converts fitted psychometric function parameters to equivalent SDT measures.
    The psychometric function ψ(x) = γ + (1 - γ - λ) * F(x; x₀, k) has natural
    correspondences to SDT:
        - γ (guess rate) ≈ false alarm rate at low intensities
        - k (slope) ≈ d' (sensitivity)
        - x₀ (threshold) ≈ location of decision criterion
    
    Args:
        params: Dictionary with psychometric function parameters:
            - x_0: threshold (50% point)
            - k: slope (steepness)
            - gamma: guess rate (lower asymptote)
            - lambda: lapse rate (upper asymptote deviation from 1)
    
    Returns:
        Dictionary with approximate SDT metrics:
            - d_prime_approx: slope k (proportional to sensitivity)
            - far_approx: gamma (baseline false alarm rate)
            - sensitivity_range: (1 - gamma - lambda) (effective dynamic range)
    
    Note:
        These are approximations. The psychometric function models the full
        intensity-response relationship, while SDT assumes a single criterion.
        Use sdt_from_trials() for direct SDT analysis with a specific criterion.
    
    Example:
        >>> params = {"x_0": 0.0, "k": 1.5, "gamma": 0.1, "lambda": 0.05}
        >>> sdt = sdt_from_params(params)
        >>> sdt['d_prime_approx']
        1.5
    """
    return {
        "d_prime_approx": params["k"],  # Slope proportional to sensitivity
        "threshold": params["x_0"],  # 50% point location
        "far_approx": params["gamma"],  # Baseline false alarm rate
        "lapse_rate": params.get("lambda", 0.0),  # Miss rate at high intensities
        "sensitivity_range": 1 - params["gamma"] - params.get("lambda", 0.0),
    }


def roc_curve(
    trials: pl.DataFrame,
    n_points: int = 20,
    intensity_col: str = "Intensity",
    result_col: str = "Result",
) -> pl.DataFrame:
    """Generate ROC curve by varying criterion across intensity range.
    
    Computes hit rate and false alarm rate at multiple criterion values,
    creating a Receiver Operating Characteristic (ROC) curve. The ROC curve
    shows the tradeoff between sensitivity (hit rate) and specificity 
    (1 - false alarm rate) across different decision thresholds.
    
    Args:
        trials: DataFrame with trial data
        n_points: Number of criterion points to sample (default: 20)
        intensity_col: Name of intensity column (default: "Intensity")
        result_col: Name of result column (default: "Result")
    
    Returns:
        DataFrame with columns:
            - criterion: Intensity threshold value
            - hit_rate: P(response=1 | intensity >= criterion)
            - false_alarm_rate: P(response=1 | intensity < criterion)
            - d_prime: d' at this criterion (if computable)
    
    Note:
        Some criterion values may not yield valid ROC points if all trials
        fall on one side of the criterion. These are omitted from results.
    
    Example:
        >>> trials = pl.DataFrame({
        ...     "Intensity": np.linspace(-2, 2, 100),
        ...     "Result": np.random.binomial(1, 0.5, 100)
        ... })
        >>> roc = roc_curve(trials, n_points=10)
        >>> len(roc)
        10
    """
    intensities = trials[intensity_col].to_numpy()
    min_intensity = float(np.min(intensities))
    max_intensity = float(np.max(intensities))
    
    # Create criterion values spanning the intensity range
    # Add small margins to include all data
    margin = (max_intensity - min_intensity) * 0.05
    criterion_values = np.linspace(
        min_intensity - margin, 
        max_intensity + margin, 
        n_points,
    )
    
    roc_data = []
    
    for crit in criterion_values:
        try:
            rates = compute_hr_far(trials, crit, intensity_col, result_col)
            hr = rates["hit_rate"]
            far = rates["false_alarm_rate"]
            
            roc_data.append({
                "criterion": crit,
                "hit_rate": hr,
                "false_alarm_rate": far,
                "d_prime": d_prime(hr, far),
            })
        except ValueError:
            # Skip criterion values that don't split data
            continue
    
    return pl.DataFrame(roc_data)


def auc(hit_rates: list[float], false_alarm_rates: list[float]) -> float:
    """Calculate Area Under the ROC Curve (AUC).
    
    AUC is a single-number summary of discriminability. An AUC of 0.5 indicates
    chance performance (no discriminability), while 1.0 indicates perfect 
    discrimination. AUC is equivalent to the probability that a randomly chosen
    signal trial has a higher response strength than a randomly chosen noise trial.
    
    Uses trapezoidal integration to compute the area under the ROC curve.
    
    Args:
        hit_rates: List of hit rates (y-axis of ROC)
        false_alarm_rates: List of false alarm rates (x-axis of ROC)
    
    Returns:
        AUC value between 0 and 1. 0.5 = chance, 1.0 = perfect.
    
    Note:
        ROC points should be sorted by false_alarm_rate for accurate integration.
        This function will sort them automatically if needed.
    
    Example:
        >>> hrs = [0.0, 0.5, 0.8, 1.0]
        >>> fars = [0.0, 0.1, 0.3, 1.0]
        >>> auc(hrs, fars)
        0.8...
    """
    # Sort by false alarm rate (x-axis)
    sorted_indices = np.argsort(false_alarm_rates)
    sorted_far = np.array(false_alarm_rates)[sorted_indices]
    sorted_hr = np.array(hit_rates)[sorted_indices]
    
    # Compute AUC using trapezoidal rule
    # Use scipy.integrate.trapezoid for numpy 2.x compatibility
    try:
        from scipy.integrate import trapezoid
        return float(trapezoid(sorted_hr, sorted_far))
    except ImportError:
        # Fallback for older scipy versions
        return float(np.trapezoid(sorted_hr, sorted_far))


def auc_from_roc(roc_df: pl.DataFrame) -> float:
    """Calculate AUC from an ROC curve DataFrame.
    
    Convenience function that extracts hit rates and false alarm rates
    from an ROC DataFrame and computes the area under the curve.
    
    Args:
        roc_df: DataFrame from roc_curve() with 'hit_rate' and 
            'false_alarm_rate' columns
    
    Returns:
        AUC value between 0 and 1.
    
    Example:
        >>> trials = pl.DataFrame({"Intensity": [...], "Result": [...]})
        >>> roc = roc_curve(trials)
        >>> auc_from_roc(roc)
        0.85
    """
    hit_rates = roc_df["hit_rate"].to_list()
    false_alarm_rates = roc_df["false_alarm_rate"].to_list()
    return auc(hit_rates, false_alarm_rates)


def plot_roc(
    roc_df: pl.DataFrame,
    show_diagonal: bool = True,
    show_auc: bool = True,
    title: str = "ROC Curve",
) -> "go.Figure":
    """Plot ROC curve with optional diagonal reference line and AUC annotation.
    
    Creates a publication-quality ROC curve plot showing the tradeoff between
    hit rate (sensitivity) and false alarm rate (1-specificity).
    
    Args:
        roc_df: DataFrame from roc_curve() with 'hit_rate' and 
            'false_alarm_rate' columns
        show_diagonal: If True, show chance performance diagonal line (default: True)
        show_auc: If True, display AUC value in legend (default: True)
        title: Plot title (default: "ROC Curve")
    
    Returns:
        Plotly Figure object
    
    Example:
        >>> trials = pl.DataFrame({"Intensity": [...], "Result": [...]})
        >>> roc = roc_curve(trials)
        >>> fig = plot_roc(roc)
        >>> fig.show()
    """
    import plotly.graph_objects as go
    
    # Sort by false alarm rate for proper line plotting
    roc_sorted = roc_df.sort("false_alarm_rate")
    
    # Calculate AUC if requested
    auc_value = auc_from_roc(roc_sorted) if show_auc else None
    
    # Create figure
    fig = go.Figure()
    
    # Add ROC curve
    name = f"ROC (AUC = {auc_value:.3f})" if show_auc else "ROC"
    fig.add_trace(go.Scatter(
        x=roc_sorted["false_alarm_rate"].to_list(),
        y=roc_sorted["hit_rate"].to_list(),
        mode="lines+markers",
        name=name,
        line={"color": "#377eb8", "width": 2},
        marker={"size": 6},
    ))
    
    # Add diagonal chance line
    if show_diagonal:
        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            name="Chance",
            line={"color": "gray", "width": 1, "dash": "dash"},
            showlegend=True,
        ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="False Alarm Rate",
        yaxis_title="Hit Rate",
        xaxis={"range": [0, 1], "constrain": "domain"},
        yaxis={"range": [0, 1], "scaleanchor": "x", "scaleratio": 1},
        template="plotly_white",
        width=600,
        height=600,
    )
    
    return fig


def plot_sdt_metrics(
    trials: pl.DataFrame,
    n_criteria: int = 20,
    intensity_col: str = "Intensity",
    result_col: str = "Result",
) -> "go.Figure":
    """Plot how SDT metrics vary across different criterion values.
    
    Shows d', criterion (c), and beta as functions of the decision criterion,
    useful for understanding how performance changes with decision threshold.
    
    Args:
        trials: DataFrame with trial data
        n_criteria: Number of criterion points to sample (default: 20)
        intensity_col: Name of intensity column (default: "Intensity")
        result_col: Name of result column (default: "Result")
    
    Returns:
        Plotly Figure with subplots for different metrics
    
    Example:
        >>> trials = pl.DataFrame({"Intensity": [...], "Result": [...]})
        >>> fig = plot_sdt_metrics(trials)
        >>> fig.show()
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Generate ROC curve (contains d' at each criterion)
    roc_df = roc_curve(trials, n_criteria, intensity_col, result_col)
    
    # Calculate additional metrics
    criterion_c_values = []
    beta_values = []
    
    for row in roc_df.iter_rows(named=True):
        hr = row["hit_rate"]
        far = row["false_alarm_rate"]
        criterion_c_values.append(criterion(hr, far))
        beta_values.append(beta(hr, far))
    
    criterion_values = roc_df["criterion"].to_list()
    d_prime_values = roc_df["d_prime"].to_list()
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=("Sensitivity (d')", "Criterion (c)", "Beta (β)"),
        vertical_spacing=0.12,
    )
    
    # d' plot
    fig.add_trace(
        go.Scatter(
            x=criterion_values,
            y=d_prime_values,
            mode="lines+markers",
            name="d'",
            line={"color": "#377eb8"},
        ),
        row=1, col=1,
    )
    
    # Criterion plot
    fig.add_trace(
        go.Scatter(
            x=criterion_values,
            y=criterion_c_values,
            mode="lines+markers",
            name="c",
            line={"color": "#e41a1c"},
        ),
        row=2, col=1,
    )
    
    # Beta plot
    fig.add_trace(
        go.Scatter(
            x=criterion_values,
            y=beta_values,
            mode="lines+markers",
            name="β",
            line={"color": "#4daf4a"},
        ),
        row=3, col=1,
    )
    
    # Update layout
    fig.update_xaxes(title_text="Intensity Criterion", row=3, col=1)
    fig.update_yaxes(title_text="d'", row=1, col=1)
    fig.update_yaxes(title_text="c", row=2, col=1)
    fig.update_yaxes(title_text="β", row=3, col=1)
    
    fig.update_layout(
        template="plotly_white",
        height=900,
        showlegend=False,
        title_text="SDT Metrics Across Decision Criteria",
    )
    
    return fig
