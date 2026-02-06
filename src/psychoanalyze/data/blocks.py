from pathlib import Path

import arviz as az
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from scipy.special import expit
from scipy.stats import logistic as scipy_logistic

from psychoanalyze.data import hierarchical, subjects
from psychoanalyze.plot import template

dims = ["Amp2", "Width2", "Freq2", "Dur2", "Active Channels", "Return Channels"]
index_levels = dims


def generate(
    n_trials_per_level: int,
    x_range: tuple[float, float],
    n_levels: int,
) -> pl.DataFrame:
    x = np.linspace(x_range[0], x_range[1], n_levels)
    n = [n_trials_per_level] * len(x)
    p = scipy_logistic.cdf(x)
    hits = np.random.default_rng().binomial(n, p)
    return pl.DataFrame({"x": x, "n": n, "Hits": hits})


def plot_fits(blocks: pl.DataFrame) -> go.Figure:
    x = np.linspace(-3, 3, 100)
    y = expit(x)
    return px.line(x=x, y=y)


def load(data_path: Path) -> pl.DataFrame:
    full_path = data_path / "blocks.csv"
    blocks = pl.read_csv(full_path / "blocks.csv").with_columns(
        pl.col("Date").str.to_datetime()
    )
    subj = subjects.load(full_path)
    blocks = days(blocks, subj)
    return blocks


def days(blocks: pl.DataFrame, intervention_dates: pl.DataFrame) -> pl.DataFrame:
    intervention_dates = intervention_dates.join(intervention_dates, on="Subject", how="left").with_columns(
        (pl.col("Date") - pl.col("Surgery Date")).dt.total_days().alias("Days"),
    )
    return blocks


def n_trials(trials: pl.DataFrame) -> pl.DataFrame:
    session_cols = ["Subject"]
    if "Date" in trials.columns:
        session_cols.append("Date")
    ref_stim_cols = ["Amp2", "Width2", "Freq2", "Dur2"]
    channel_config = ["Active Channels", "Return Channels"]
    return trials.group_by(session_cols + ref_stim_cols + channel_config).agg(
        pl.len().alias("n_trials"),
    )


def fit(
    trials: pl.DataFrame,
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 2,
    target_accept: float = 0.9,
) -> az.InferenceData:
    return hierarchical.fit(
        trials=trials,
        draws=draws,
        tune=tune,
        chains=chains,
        target_accept=target_accept,
    )


def curve_credible_band(
    idata: az.InferenceData,
    x: np.ndarray | list[float],
    hdi_prob: float = 0.9,
) -> pl.DataFrame:
    return hierarchical.curve_credible_band(
        idata=idata,
        x=x,
        block_idx=0,
        hdi_prob=hdi_prob,
    )


def from_points(points: pl.DataFrame) -> pl.DataFrame:
    return points.group_by("BlockID").agg(pl.sum("n"))


def plot_thresholds(blocks: pl.DataFrame) -> go.Figure:
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
    return fit.with_columns(
        (pl.col("95%") - pl.col("50%")).alias("err+"),
        (pl.col("50%") - pl.col("5%")).alias("err-"),
    ).drop(["95%", "5%"])


def reshape_fit_results(fits: pl.DataFrame, x: list[float], y: str) -> pl.DataFrame:
    rows = [f"{y}[{i}]" for i in range(1, len(x) + 1)]
    param_fits = fits.filter(pl.col("index").is_in(rows)).select(["5%", "50%", "95%"])
    param_fits = transform_errors(param_fits)
    param_fits = param_fits.rename({"50%": y})
    param_fits = param_fits.with_columns(pl.Series("Intensity", x))
    return param_fits


def standard_logistic() -> pl.DataFrame:
    x = np.linspace(-3, 3, 100)
    y = expit(x)
    return pl.DataFrame({"x": x, "f(x)": y})


def logistic(location: float, scale: float) -> pl.DataFrame:
    x_min = (location - 4) * scale
    x_max = (location + 4) * scale
    x = np.linspace(x_min, x_max, 100)
    y = expit((x - location) / scale)
    return pl.DataFrame({"Intensity": x, "Ψ(x)": y})


def plot_logistic(location: float, scale: float) -> go.Figure:
    df = logistic(location, scale)
    return px.line(
        df.to_pandas(),
        x="Intensity",
        y="Ψ(x)",
        template="plotly_white",
    )


def plot_standard_logistic() -> go.Figure:
    df = standard_logistic()
    return px.line(
        df.to_pandas(),
        x="x",
        y="f(x)",
        template="plotly_white",
        title="$f(x) = \\frac{1}{1 + e^{-x}}$",
    )
