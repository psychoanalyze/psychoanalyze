
"""Block-level data utilities.

**Blocks** are the most analytically significant objects in the PsychoAnalyze
data hierarchy. They represent a specific set of experimental conditions and generally
correspond to a single fit of the psychometric function.

Note: As of the hierarchical model update, `blocks.fit()` now uses hierarchical
Bayesian modeling by default, which provides better estimates through information
sharing across blocks. For full control over hierarchical parameters, use
`psychoanalyze.data.hierarchical.fit()` directly.
"""
from pathlib import Path
from typing import cast

import arviz as az
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
import pymc as pm
import pytensor.tensor as pt
from scipy.special import expit
from scipy.stats import logistic as scipy_logistic

from psychoanalyze.data import (
    subject as subject_utils,
)
from psychoanalyze.data import (
    subjects,
    trials,
)
from psychoanalyze.plot import template

dims = ["Amp2", "Width2", "Freq2", "Dur2", "Active Channels", "Return Channels"]
index_levels = dims


def generate(
    n_trials_per_level: int,
    x_min: float,
    x_max: float,
    n_levels: int,
) -> pl.DataFrame:
    """Generate block-level data."""
    x = np.linspace(x_min, x_max, n_levels)
    n = [n_trials_per_level] * len(x)
    p = scipy_logistic.cdf(x)
    hits = np.random.default_rng().binomial(n, p)
    return pl.DataFrame({"x": x, "n": n, "Hits": hits})


def plot_fits(blocks: pl.DataFrame) -> go.Figure:
    """Plot fits."""
    x = np.linspace(-3, 3, 100)
    y = expit(x)
    return px.line(x=x, y=y)


def load(data_path: Path) -> pl.DataFrame:
    """Load block data from csv."""
    full_path = data_path / "blocks.csv"
    channel_config = ["Active Channels", "Return Channels"]
    blocks = pl.read_csv(full_path / "blocks.csv")
    blocks = blocks.with_columns(pl.col("Date").str.to_datetime())
    subj = subjects.load(full_path)
    blocks = days(blocks, subj)
    return blocks


def days(blocks: pl.DataFrame, intervention_dates: pl.DataFrame) -> pl.DataFrame:
    """Calculate days for block-level data. Possible duplicate."""
    blocks = subject_utils.ensure_subject_column(blocks)
    intervention_dates = subject_utils.ensure_subject_column(intervention_dates)
    blocks = blocks.join(intervention_dates, on="Subject", how="left")
    blocks = blocks.with_columns(
        (pl.col("Date") - pl.col("Surgery Date")).dt.total_days().alias("Days"),
    )
    return blocks


def n_trials(trials: pl.DataFrame) -> pl.DataFrame:
    """Calculate n trials for each block."""
    trials = subject_utils.ensure_subject_column(trials)
    session_cols = ["Subject"]
    if "Date" in trials.columns:
        session_cols.append("Date")
    ref_stim_cols = ["Amp2", "Width2", "Freq2", "Dur2"]
    channel_config = ["Active Channels", "Return Channels"]
    return trials.group_by(session_cols + ref_stim_cols + channel_config).agg(
        pl.len().alias("n_trials"),
    )


def is_valid(block: pl.DataFrame) -> bool:
    """Determine if curve data is valid."""
    hit_rates = block["Hit Rate"].to_list()
    return any(h > 0.5 for h in hit_rates) and any(h < 0.5 for h in hit_rates)


def subject_counts(data: pl.DataFrame) -> pl.DataFrame:
    """Determine how many subjects are in the data."""
    return data.group_by("Subject").agg(pl.len().alias("Total Blocks"))


def fit(
    trials: pl.DataFrame,
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 2,
    target_accept: float = 0.9,
    random_seed: int | None = None,
) -> az.InferenceData:
    """Fit logistic regression to trial data using hierarchical PyMC model.
    
    This function now uses the hierarchical model by default, which provides
    better estimates especially for sparse data. For backward compatibility,
    if no 'Block' column is present, a default block is created.
    
    Args:
        trials: DataFrame with 'Intensity' and 'Result' columns. 
                Optionally includes 'Block' for multi-block hierarchical fitting.
        draws: Number of posterior samples per chain
        tune: Number of tuning samples
        chains: Number of MCMC chains
        target_accept: Target acceptance probability for NUTS sampler
        random_seed: Random seed for reproducibility
        
    Returns:
        InferenceData object with posterior samples. For single-block data,
        returns parameters for that block. For multi-block data, returns
        hierarchical parameters for all blocks.
    """
    from psychoanalyze.data import hierarchical
    
    # Ensure Block column exists for hierarchical model
    if "Block" not in trials.columns:
        trials = trials.with_columns(pl.lit(0).alias("Block"))
    
    # Use hierarchical model
    return hierarchical.fit(
        trials=trials,
        draws=draws,
        tune=tune,
        chains=chains,
        target_accept=target_accept,
        random_seed=random_seed,
    )


def summarize_fit(idata: az.InferenceData) -> dict[str, float]:
    """Summarize posterior draws for block-level fits.
    
    For hierarchical models (multi-block), returns the first block's parameters
    for backward compatibility. For full hierarchical summary including all blocks,
    use hierarchical.summarize_fit() directly.
    
    Args:
        idata: InferenceData from fit()
        
    Returns:
        Dictionary with 'intercept', 'slope', and 'threshold' for the first block.
    """
    from psychoanalyze.data import hierarchical
    
    # Get hierarchical summary
    hier_summary = hierarchical.summarize_fit(idata)
    
    # Check if this is a multi-block fit
    if isinstance(hier_summary.get("intercept"), np.ndarray):
        # Multi-block: return first block for backward compatibility
        return {
            "intercept": float(hier_summary["intercept"][0]),
            "slope": float(hier_summary["slope"][0]),
            "threshold": float(hier_summary["threshold"][0]),
        }
    else:
        # Should not happen with current implementation, but handle gracefully
        return {
            "intercept": float(hier_summary["intercept"]),
            "slope": float(hier_summary["slope"]),
            "threshold": float(hier_summary["threshold"]),
        }


def curve_credible_band(
    idata: az.InferenceData,
    x: np.ndarray | list[float],
    hdi_prob: float = 0.9,
) -> pl.DataFrame:
    """Compute a credible band for the psychometric curve.
    
    Delegates to hierarchical.curve_credible_band for the first block.
    For multi-block credible bands, use hierarchical.curve_credible_band directly.
    
    Args:
        idata: InferenceData from fit()
        x: Array of intensity values to evaluate curve at
        hdi_prob: Probability mass for credible interval
        
    Returns:
        DataFrame with columns 'Intensity', 'lower', 'upper'
    """
    from psychoanalyze.data import hierarchical
    
    # Use hierarchical version for first block
    return hierarchical.curve_credible_band(
        idata=idata,
        x=x,
        block_idx=0,
        hdi_prob=hdi_prob,
    )



def generate_trials(n_trials: int, model_params: dict[str, float]) -> pl.DataFrame:
    """Generate trials for block-level context."""
    return trials.moc_sample(n_trials, model_params)


def from_points(points: pl.DataFrame) -> pl.DataFrame:
    """Aggregate block measures from points data."""
    return points.group_by("BlockID").agg(pl.sum("n"))


def plot_thresholds(blocks: pl.DataFrame) -> go.Figure:
    """Plot longitudinal threshold data.

    Args:
        blocks: Block-level DataFrame.

    Returns:
        A plotly Graph Object.
    """
    blocks = transform_errors(blocks)
    return px.scatter(
        blocks.to_pandas(),
        x="Block",
        y="50%",
        error_y="err+",
        error_y_minus="err-",
        color="Subject",
        color_discrete_map={"U": "#e41a1c", "Y": "#377eb8", "Z": "#4daf4a"},
        template=template,
    )


def transform_errors(fit: pl.DataFrame) -> pl.DataFrame:
    """Transform errors from absolute to relative."""
    return fit.with_columns(
        (pl.col("95%") - pl.col("50%")).alias("err+"),
        (pl.col("50%") - pl.col("5%")).alias("err-"),
    ).drop(["95%", "5%"])


def reshape_fit_results(fits: pl.DataFrame, x: list[float], y: str) -> pl.DataFrame:
    """Reshape fit params for plotting."""
    rows = [f"{y}[{i}]" for i in range(1, len(x) + 1)]
    param_fits = fits.filter(pl.col("index").is_in(rows)).select(["5%", "50%", "95%"])
    param_fits = transform_errors(param_fits)
    param_fits = param_fits.rename({"50%": y})
    param_fits = param_fits.with_columns(pl.Series("Intensity", x))
    return param_fits


def standard_logistic() -> pl.DataFrame:
    """Generate points for a line trace of a standard logistic function."""
    x = np.linspace(-3, 3, 100)
    y = expit(x)
    return pl.DataFrame({"x": x, "f(x)": y})


def logistic(location: float, scale: float) -> pl.DataFrame:
    """Generate points for a line trace of a logistic function."""
    x_min = (location - 4) * scale
    x_max = (location + 4) * scale
    x = np.linspace(x_min, x_max, 100)
    y = expit((x - location) / scale)
    return pl.DataFrame({"Intensity": x, "Ψ(x)": y})


def plot_logistic(location: float, scale: float) -> go.Figure:
    """Plot a logistic function.

    Parameters:
        location: x₀ in the location-scale parameterization, corresponds to threshold.
        scale: σ corresponds to the width of the curve (inverse of slope)

    Returns:
        A Plotly figure of the psychometric function with a logistic link function.
    """
    df = logistic(location, scale)
    return px.line(
        df.to_pandas(),
        x="Intensity",
        y="Ψ(x)",
        template="plotly_white",
    )


def plot_standard_logistic() -> go.Figure:
    """Plot a standard logistic function."""
    df = standard_logistic()
    return px.line(
        df.to_pandas(),
        x="x",
        y="f(x)",
        template="plotly_white",
        title="$f(x) = \\frac{1}{1 + e^{-x}}$",
    )
