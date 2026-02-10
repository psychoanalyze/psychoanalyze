"""Utilities for points-level data.

**Points** correspond to the aggregate measures of method-of-constant-stimuli
experiments at each stimulus level measured. For example, a block that samples 8
stimulus intensity levels would have 8 corresponding points.
"""

import numpy as np
import plotly.express as px
import polars as pl
from plotly import graph_objects as go
from scipy.special import expit, logit
from scipy.stats import logistic

index_levels = ["Amp1", "Width1", "Freq1", "Dur1"]


def from_trials(trials: pl.DataFrame) -> pl.DataFrame:
    """Aggregate point-level measures from trial data."""
    points = trials.group_by(["Block", "Intensity"]).agg(
        pl.len().alias("n trials"),
        pl.sum("Result").alias("Hits"),
    )
    points = points.with_columns(
        (pl.col("Hits") / pl.col("n trials")).alias("Hit Rate"),
    )
    points = points.with_columns(
        pl.col("Hit Rate")
        .map_elements(
            lambda x: logit(x) if 0 < x < 1 else None,
            return_dtype=pl.Float64,
        )
        .alias("logit(Hit Rate)"),
    )
    return points.sort(["Block", "Intensity"])


def prep_fit(points: pl.DataFrame, dimension: str = "Amp1") -> dict:
    """Transform points data for numpy-related fitting procedures."""
    return {
        "X": len(points),
        "x": points[f"{dimension}"].to_numpy(),
        "N": points["n"].to_numpy(),
        "hits": points["Hits"].to_numpy(),
    }


def hits(
    n: pl.DataFrame,
    params: dict[str, float],
) -> pl.DataFrame:
    """Sample list of n hits from a list of intensity values."""
    intensities = n["Intensity"].to_numpy()
    n_trials = n["n"].to_numpy()
    p = logistic.cdf(intensities, params["Threshold"], params["Slope"])
    psi = params["Guess Rate"] + (1.0 - params["Guess Rate"] - params["Lapse Rate"]) * p
    hit_values = np.random.default_rng().binomial(n_trials, psi, len(n_trials))
    return pl.DataFrame(
        {
            "Intensity": intensities,
            "Hits": hit_values,
        },
    )


def generate_point(n: int, p: float) -> int:
    """Sample n hits from n trials and probability p from binomial dist."""
    return np.random.default_rng().binomial(n, p)


def datatable_data(data: pl.DataFrame) -> list[dict]:
    """Convert dataframe to Dash DataTable-friendly format."""
    return data.select(["Amp1", "Hit Rate", "n"]).to_dicts()


def combine_plots(fig1: go.Figure, fig2: go.Figure) -> go.Figure:
    """Combine two points-level plots. Possible duplicate."""
    return go.Figure(data=fig1.data + fig2.data)


def n(trials: list[float]) -> pl.DataFrame:
    """Count trials at each point."""
    df = pl.DataFrame({"Intensity": trials})
    return df.group_by("Intensity").agg(pl.len().alias("n"))


def to_block(points: pl.DataFrame) -> pl.DataFrame:
    """Aggregate to block-level measures from points-level data."""
    return points.group_by(["Subject", "Block"]).agg(
        pl.sum("n trials"),
        pl.sum("Hits"),
    )


def psi(
    x: list[float],
    params: dict[str, float],
) -> pl.DataFrame:
    """Calculate psi for an array of intensity levels x."""
    x_arr = np.array(x)
    y = params["gamma"] + (1 - params["gamma"] - params["lambda"]) * expit(
        params["x_0"] + params["k"] * x_arr,
    )
    return pl.DataFrame({"Intensity": x, "p(x)": y})


def plot(points: pl.DataFrame, y: str) -> go.Figure:
    """Plot the psychometric function."""
    color = "Subject" if "Subject" in points.columns else "Block"
    return px.scatter(
        points.to_pandas(),
        x="Intensity",
        y=y,
        size="n",
        color=color,
        template="plotly_white",
    )


def hit_rate(df: pl.DataFrame) -> pl.Series:
    """Calculate hit rate from hits and number of trials."""
    return df["Hits"] / df["n"]


def transform(hit_rate: float, y: str) -> float:
    """Logit transform hit rate."""
    return logit(hit_rate) if y == "alpha" else hit_rate


def generate_index(n_levels: int, x_range: list[float]) -> list[float]:
    """Generate evenly-spaced values along the modulated stimulus dimension."""
    min_x = x_range[0]
    max_x = x_range[1]
    return list(np.linspace(min_x, max_x, n_levels))
