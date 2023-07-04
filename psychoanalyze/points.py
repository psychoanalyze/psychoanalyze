"""Utilities for points-level data."""
from pathlib import Path

import cmdstanpy as stan
import numpy as np
import pandas as pd
import pandera as pr
import plotly.express as px
from dash import dash_table
from plotly import graph_objects as go
from scipy.stats import binom

from psychoanalyze import trials

index_levels = ["Amp1", "Width1", "Freq1", "Dur1"]


class Points(pr.DataFrameModel):

    """Pandera data type."""

    n: int
    Hits: int
    block_id: int


def from_trials(_trials: pd.DataFrame) -> pd.Series:
    """Aggregate point-level measures from trial data."""
    return (
        _trials.groupby("Intensity")[["Result"]]
        .agg(["count", "sum"])
        .rename(columns={"count": "n", "sum": "Hits"})
    )["Result"]


def load(data_path: Path) -> pd.Series:
    """Load points data from csv."""
    _trials = trials.load(data_path)
    return from_trials(_trials)


def dimension(points: pd.DataFrame) -> str:
    """Determine modulated dimension from point-level data."""
    amp1, width1 = (
        points.index.get_level_values(param) for param in ["Amp1", "Width1"]
    )
    if amp1.nunique() > 1 and width1.nunique() == 1:
        return "Amp"
    if width1.nunique() > 1 and amp1.nunique() == 1:
        return "Width"
    if width1.nunique() > 1 and amp1.nunique() > 1:
        return "Both"
    return "Neither"


def prep_fit(points: pd.DataFrame, dimension: str = "Amp1") -> dict:
    """Transform points data for numpy-related fitting procedures."""
    points = points.reset_index()
    return {
        "X": len(points),
        "x": points[f"{dimension}"].to_numpy(),
        "N": points["n"].to_numpy(),
        "hits": points["Hits"].to_numpy(),
    }


def model() -> stan.CmdStanModel:
    """Instantiate Stan binomial regression model."""
    return stan.CmdStanModel(stan_file="models/binomial_regression.stan")


# def fit(ready_for_fit: pd.DataFrame) -> pd.DataFrame:


def fit(
    points: pd.DataFrame,
    save_to: Path | None = None,
    block: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Fit psychometric curve to points."""
    points = points[["x", "Hits", "n"]]
    if len(points):
        data = points
        _fit = trials.fit(data)
        _fit = pd.DataFrame(
            {
                "Threshold": [_fit["Fit"][0]],
                "width": [_fit["Fit"][1]],
                "gamma": [_fit["Fit"][2]],
                "lambda": [_fit["Fit"][3]],
                "err+": [None],
                "err-": [None],
            },
            index=pd.MultiIndex.from_tuples(
                [block],
                names=[
                    "Monkey",
                    "Date",
                    "Amp2",
                    "Width2",
                    "Freq2",
                    "Dur2",
                    "Active Channels",
                    "Return Channels",
                ],
            ),
        )
        if save_to:
            _fit.to_csv(save_to)
        return _fit
    return pd.DataFrame(
        {
            "Threshold": [],
            "width": [],
            "lambda": [],
            "gamma": [],
            "err+": [],
            "err-": [],
        },
    )


def generate(x: list[float], n: list[int], p: list[float]) -> pd.Series:
    """Generate points-level data."""
    return pd.Series(
        [binom.rvs(n[i], p[i]) for i in range(len(x))],
        index=pd.Index(x, name="Intensity"),
        name="Hit Rate",
    )


def datatable(data: pd.DataFrame) -> dash_table.DataTable:
    """Convert dataframe to Dash DataTable-friendly format."""
    return dash_table.DataTable(
        data.reset_index()[["Amp1", "Hit Rate", "n"]].to_dict("records"),
        columns=[
            {
                "id": "Amp1",
                "name": "Amp1",
                "type": "numeric",
                "format": dash_table.Format.Format(
                    precision=2,
                    scheme=dash_table.Format.Scheme.fixed,
                ),
            },
            {
                "id": "Hit Rate",
                "name": "Hit Rate",
                "type": "numeric",
                "format": dash_table.Format.Format(
                    precision=2,
                    scheme=dash_table.Format.Scheme.fixed,
                ),
            },
            {
                "id": "n",
                "name": "n",
                "type": "numeric",
            },
        ],
        id="experiment-psych-table",
    )


def from_store(store_data: str) -> pd.DataFrame:
    """Get points-level measures from trials-level data store."""
    _trials = trials.from_store(store_data)
    return from_trials(_trials).to_frame()


def combine_plots(fig1: go.Figure, fig2: go.Figure) -> go.Figure:
    """Combine two points-level plots. Possible duplicate."""
    return go.Figure(data=fig1.data + fig2.data)


def n(trials: pd.DataFrame) -> pd.DataFrame:
    """Count trials at each point."""
    return trials.groupby(level="Block").count()


def to_block(points: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to block-level measures from points-level data."""
    return points.groupby(level="Block").sum()


def psi(
    x: np.ndarray,
    threshold: float,
    width: float,
    gamma: float,
    lambda_: float,
) -> float:
    """Calculate psi for an array of intensity levels x."""
    return gamma + (1 - gamma - lambda_) / (
        1 + np.exp(-gamma * (x - threshold) / width) ** lambda_
    )


def plot(points: pd.DataFrame) -> go.Figure:
    """Plot points data."""
    return px.scatter(points.reset_index(), x="Intensity", y="Hit Rate")
