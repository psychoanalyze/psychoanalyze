# Copyright 2023 Tyler Schlichenmeyer

# This file is part of PsychoAnalyze.
# PsychoAnalyze is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# PsychoAnalyze is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# PsychoAnalyze. If not, see <https://www.gnu.org/licenses/>.

"""Utilities for points-level data.

**Points** correspond to the aggregate measures of method-of-constant-stimuli
experiments at each stimulus level measured. For example, a block that samples 8
stimulus intensity levels would have 8 corresponding points.
"""
from pathlib import Path

import cmdstanpy as stan
import numpy as np
import pandas as pd
import plotly.express as px
from dash import dash_table
from pandera import check_io, check_output
from plotly import graph_objects as go
from scipy.special import logit
from scipy.stats import logistic

from psychoanalyze.data import trials as pa_trials
from psychoanalyze.data import types

index_levels = ["Amp1", "Width1", "Freq1", "Dur1"]


@check_io(trials=types.trials, out=types.points)
def from_trials(trials: pd.DataFrame) -> pd.DataFrame:
    """Aggregate point-level measures from trial data."""
    points = trials.groupby("Intensity").agg(["count", "sum"])
    points.columns = points.columns.droplevel()
    points = points.rename(columns={"count": "n", "sum": "Hits"})
    points["Hit Rate"] = points["Hits"] / points["n"]
    points["logit(Hit Rate)"] = logit(points["Hit Rate"])
    return points


@check_output(types.points)
def load(data_path: Path) -> pd.DataFrame:
    """Load points data from csv."""
    trials = pa_trials.load(data_path)
    return from_trials(trials)


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


def fit(
    points: pd.DataFrame,
) -> pd.DataFrame:
    """Fit psychometric curve to points."""
    if len(points):
        fit = pa_trials.fit(points[["x", "Hits", "n"]])
        return pd.DataFrame(
            {
                "Threshold": [fit["Threshold"]],
                "Slope": [fit["Slope"]],
            },
        )
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


def hits(
    n: pd.Series,
    params: dict[str, float],
) -> pd.Series:
    """Sample list of n hits from a list of intensity values."""
    p = logistic.cdf(n.index.to_numpy(), params["Threshold"], params["Slope"])
    psi = params["Guess Rate"] + (1.0 - params["Guess Rate"] - params["Lapse Rate"]) * p
    return pd.Series(
        np.random.default_rng().binomial(
            n,
            psi,
            len(n),
        ),
        index=n.index,
        name="Hits",
    )


def generate(
    n_trials: int,
    options: pd.Index,
    params: dict[str, float],
) -> pd.DataFrame:
    """Generate points-level data."""
    n = generate_n(n_trials, options)
    _hits = hits(
        n,
        params,
    )
    points = pd.concat([n, _hits], axis=1)
    _hit_rate = hit_rate(points)
    logit_hit_rate = pd.Series(
        logit(_hit_rate),
        name="logit(Hit Rate)",
        index=n.index,
    )
    return pd.concat([points, _hit_rate, logit_hit_rate], axis=1)


def generate_point(n: int, p: float) -> int:
    """Sample n hits from n trials and probability p from binomial dist."""
    return np.random.default_rng().binomial(n, p)


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
    trials = pa_trials.from_store(store_data)
    return from_trials(trials)


def combine_plots(fig1: go.Figure, fig2: go.Figure) -> go.Figure:
    """Combine two points-level plots. Possible duplicate."""
    return go.Figure(data=fig1.data + fig2.data)


def n(trials: pd.Series) -> pd.Series:
    """Count trials at each point."""
    return pd.Series(trials.value_counts(), name="n")


def generate_n(n_trials: int, options: pd.Index) -> pd.Series:
    """Simulate how many trials were performed per intensity level."""
    return n(pa_trials.generate_trial_index(n_trials, options))


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


def plot(points: pd.DataFrame, y: str) -> go.Figure:
    """Plot the psychometric function."""
    return px.scatter(
        points.reset_index(),
        x="Intensity",
        y=y,
        size="n",
        template="plotly_white",
    )


def hit_rate(df: pd.DataFrame) -> pd.Series:
    """Calculate hit rate from hits and number of trials."""
    return pd.Series(df["Hits"] / df["n"], name="Hit Rate")


def transform(hit_rate: float, y: str) -> float:
    """Logit transform hit rate."""
    return logit(hit_rate) if y == "alpha" else hit_rate


def plot_logistic(logistic: pd.DataFrame, y: str, name: str, color: str) -> go.Scatter:
    """Plot a smooth logistic function."""
    logistic = logistic.reset_index()
    return go.Scatter(
        x=logistic["Intensity"],
        y=logistic[y],
        mode="lines",
        name=name,
        marker_color=color,
    )


def generate_index(n_levels: int, x_range: list[float]) -> pd.Index:
    """Generate evenly-spaced values along the modulated stimulus dimension."""
    min_x = x_range[0]
    max_x = x_range[1]
    return pd.Index(np.linspace(min_x, max_x, n_levels), name="Intensity")
