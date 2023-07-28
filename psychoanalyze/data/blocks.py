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

"""Block-level data utilities.

**Blocks** are the most analytically significant objects in the PsychoAnalyze
data hierarchy. They represent a specific set of experimental conditions and generally
correspond to a single fit of the psychometric function.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.special import expit
from scipy.stats import logistic as scipy_logistic
from sklearn.linear_model import LogisticRegression

from psychoanalyze.data import (
    sessions,
    stimulus,
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
) -> pd.DataFrame:
    """Generate block-level data."""
    index = pd.Index(np.linspace(x_min, x_max, n_levels), name="x")
    n = [n_trials_per_level] * len(index)
    p = scipy_logistic.cdf(index)
    return pd.DataFrame(
        {"n": n, "Hits": np.random.default_rng().binomial(n, p)},
        index=index,
    )


def plot_fits(blocks: pd.DataFrame) -> go.Figure:
    """Plot fits."""
    x = np.linspace(-3, 3, 100)
    y = expit(x)
    return px.line(blocks.reset_index(), x=x, y=y)


def load(data_path: Path) -> pd.DataFrame:
    """Load block data from csv."""
    full_path = data_path / "blocks.csv"
    channel_config = ["Active Channels", "Return Channels"]
    blocks = pd.read_csv(full_path / "blocks.csv", parse_dates=["Date"]).set_index(
        sessions.dims + stimulus.ref_dims + channel_config,
    )
    blocks["Block"] = days(blocks, subjects.load(full_path))
    return blocks


def days(blocks: pd.DataFrame, intervention_dates: pd.DataFrame) -> pd.Series:
    """Calculate days for block-level data. Possible duplicate."""
    blocks = blocks.join(intervention_dates, on="Subject")
    days = pd.Series(
        blocks.index.get_level_values("Date") - blocks["Surgery Date"],
    ).dt.days
    days.name = "Days"
    return days


def n_trials(trials: pd.DataFrame) -> pd.Series:
    """Calculate n trials for each block."""
    session_cols = ["Subject", "Date"]
    ref_stim_cols = ["Amp2", "Width2", "Freq2", "Dur2"]
    channel_config = ["Active Channels", "Return Channels"]
    return trials.groupby(session_cols + ref_stim_cols + channel_config)[
        "Result"
    ].count()


def is_valid(block: pd.DataFrame) -> bool:
    """Determine if curve data is valid."""
    return any(block["Hit Rate"] > 0.5) & any(block["Hit Rate"] < 0.5)  # noqa: PLR2004


def subject_counts(data: pd.DataFrame) -> pd.DataFrame:
    """Determine how many subjects are in the data."""
    summary = (
        data.index.get_level_values("Subject").value_counts().rename("Total Blocks")
    )
    summary.index.name = "Subject"
    return summary


def fit(trials: pd.DataFrame) -> pd.Series:
    """Fit logistic regression to trial data."""
    fit = LogisticRegression().fit(
        trials[["Intensity"]],
        trials["Result"],
    )
    intercept = fit.intercept_[0]
    slope = fit.coef_[0][0]
    return pd.Series({"intercept": intercept, "slope": slope})


def generate_trials(n_trials: int, model_params: dict[str, float]) -> pd.DataFrame:
    """Generate trials for block-level context."""
    return trials.moc_sample(n_trials, model_params)


def from_points(points: pd.DataFrame) -> pd.DataFrame:
    """Aggregate block measures from points data."""
    return points.groupby("BlockID")[["n"]].sum()


def plot_thresholds(blocks: pd.DataFrame) -> go.Figure:
    """Plot longitudinal threshold data.

    Args:
        blocks: Block-level DataFrame.

    Returns:
        A plotly Graph Object.
    """
    return px.scatter(
        transform_errors(blocks),
        x="Block",
        y="50%",
        error_y="err+",
        error_y_minus="err-",
        color="Subject",
        color_discrete_map={"U": "#e41a1c", "Y": "#377eb8", "Z": "#4daf4a"},
        template=template,
    )


def transform_errors(fit: pd.DataFrame) -> pd.DataFrame:
    """Transform errors from absolute to relative."""
    fit["err+"] = fit["95%"] - fit["50%"]
    fit["err-"] = fit["50%"] - fit["5%"]
    return fit.drop(columns=["95%", "5%"])


def reshape_fit_results(fits: pd.DataFrame, x: pd.Index, y: str) -> pd.DataFrame:
    """Reshape fit params for plotting."""
    rows = [f"{y}[{i}]" for i in range(1, len(x) + 1)]
    param_fits = fits.loc[
        rows,  # row eg 'p[1]:p[8]'
        ["5%", "50%", "95%"],  # col
    ]
    param_fits = transform_errors(param_fits)
    param_fits = param_fits.rename(columns={"50%": y})
    param_fits.index = x
    return param_fits


def standard_logistic() -> pd.Series:
    """Generate points for a line trace of a standard logistic function."""
    x = pd.Index(np.linspace(-3, 3, 100), name="x")
    y = expit(x)
    return pd.Series(y, index=x, name="f(x)")


def logistic(location: float, scale: float) -> pd.Series:
    """Generate points for a line trace of a logistic function."""
    x_min = (location - 4) * scale
    x_max = (location + 4) * scale
    x = pd.Index(np.linspace(x_min, x_max, 100), name="Intensity")
    y = expit((x - location) / scale)
    return pd.Series(y, index=x, name="Ψ(x)")
