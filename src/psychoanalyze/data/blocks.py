
"""Block-level data utilities.

**Blocks** are the most analytically significant objects in the PsychoAnalyze
data hierarchy. They represent a specific set of experimental conditions and generally
correspond to a single fit of the psychometric function.
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
    """Fit logistic regression to trial data using PyMC."""
    x = trials["Intensity"].to_numpy()
    y = trials["Result"].to_numpy()

    with pm.Model():
        intercept = pm.Normal("intercept", mu=0.0, sigma=2.5)
        slope = pm.Normal("slope", mu=0.0, sigma=2.5)
        pm.Bernoulli("obs", logit_p=intercept + slope * x, observed=y)
        intercept_t = pt.as_tensor_variable(intercept)
        slope_t = pt.as_tensor_variable(slope)
        threshold = pt.true_div(pt.mul(intercept_t, -1), slope_t)
        pm.Deterministic("threshold", threshold)
        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            cores=1,
            target_accept=target_accept,
            random_seed=random_seed,
            progressbar=False,
            return_inferencedata=True,
        )
    return idata


def summarize_fit(idata: az.InferenceData) -> dict[str, float]:
    """Summarize posterior draws for block-level fits."""
    summary = cast(
        "pd.DataFrame", az.summary(idata, var_names=["intercept", "slope", "threshold"]),
    )
    return {
        "intercept": float(summary.loc["intercept", "mean"]),
        "slope": float(summary.loc["slope", "mean"]),
        "threshold": float(summary.loc["threshold", "mean"]),
    }


def curve_credible_band(
    idata: az.InferenceData,
    x: np.ndarray | list[float],
    hdi_prob: float = 0.9,
) -> pl.DataFrame:
    """Compute a credible band for the psychometric curve."""
    x_array = np.asarray(x, dtype=float)
    posterior = idata.posterior
    intercept = posterior["intercept"].stack(sample=("chain", "draw")).values
    slope = posterior["slope"].stack(sample=("chain", "draw")).values
    logits = intercept[:, None] + slope[:, None] * x_array[None, :]
    probs = expit(logits)
    alpha = (1.0 - hdi_prob) / 2.0
    lower = np.quantile(probs, alpha, axis=0)
    upper = np.quantile(probs, 1.0 - alpha, axis=0)
    return pl.DataFrame({"Intensity": x_array, "lower": lower, "upper": upper})


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
