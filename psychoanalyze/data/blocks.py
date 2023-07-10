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
from pandera.typing import DataFrame
from scipy.special import expit, logit
from scipy.stats import logistic as scipy_logistic
from sklearn.linear_model import LogisticRegression

from psychoanalyze.data import (
    points,
    sessions,
    stimulus,
    subjects,
    trials,
    types,
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


def prep_psych_curve(curves_data: pd.DataFrame, x: pd.Index, y: str) -> pd.DataFrame:
    """Transform & fit curve data."""
    curves_data.index = x
    fits = points.fit(curves_data)
    return reshape_fit_results(fits, x, y)


def dimensions(_points: pd.DataFrame, dims: list[str]) -> pd.Series:
    """Calculate dimensions for multiple blocks."""
    return _points.groupby(
        [dim for dim in list(_points.index.names) if dim not in dims],
    ).apply(points.dimension)


def fits(_points: pd.DataFrame) -> pd.DataFrame:
    """Apply fits to multiple blocks."""
    if len(_points):
        return _points.groupby(types.block_index_levels).apply(points.fit)
    return pd.DataFrame(
        {"Threshold": [], "Fixed Magnitude": [], "Dimension": []},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {
                    "Subject": [],
                    "Date": [],
                    "Amp2": [],
                    "Width2": [],
                    "Freq2": [],
                    "Dur2": [],
                    "Active Channels": [],
                    "Return Channels": [],
                },
            ),
        ),
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


def experiment_type(blocks: pd.DataFrame) -> pd.Series:
    """Determine experimental type (detection/discrimination) from data."""
    ref_stim = blocks.reset_index()[["Amp2", "Width2", "Freq2", "Dur2"]]
    ref_charge = ref_stim["Amp2"] * ref_stim["Width2"]
    blocks.loc[ref_charge == 0, "Experiment Type"] = "Detection"
    blocks.loc[ref_charge != 0, "Experiment Type"] = "Discrimination"
    return blocks["Experiment Type"]


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


def model_predictions(
    intensity_choices: list[float],
    k: float,
    x_0: float = 0.0,
) -> pd.Series:
    """Calculate psi for array of x values. Possible duplicate."""
    return pd.Series(
        [1 / (1 + np.exp(-k * (x - x_0))) for x in intensity_choices],
        index=intensity_choices,
        name="Hit Rate",
    )


def make_predictions(fit: pd.Series, intensity_choices: list[float]) -> pd.Series:
    """Get psi value for array of x values."""
    return pd.Series(
        fit.predict_proba(pd.DataFrame({"Intensity": intensity_choices}))[:, 1],
        name="Hit Rate",
        index=pd.Index(intensity_choices, name="Intensity"),
    )


def get_fit(trials: pd.DataFrame) -> pd.Series:
    """Get parameter fits for given trial data."""
    fit = LogisticRegression().fit(trials[["Intensity"]], trials["Result"])
    return pd.Series(
        {
            "slope": fit.coef_[0][0],
            "intercept": fit.intercept_[0],
        },
    )


def generate_trials(n_trials: int, model_params: dict[str, float]) -> pd.DataFrame:
    """Generate trials for block-level context."""
    return trials.moc_sample(n_trials, model_params)


def from_points(points: DataFrame[types.Points]) -> pd.DataFrame:
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


def logistic(params: dict[str, float]) -> pd.DataFrame:
    """Generate logistic function from parameters."""
    x = np.linspace(
        scipy_logistic.ppf(0.01) + params["Threshold"],
        scipy_logistic.ppf(0.99) + params["Threshold"],
        100,
    )
    y = params["Guess Rate"] + (
        1 - params["Guess Rate"] - params["Lapse Rate"]
    ) * scipy_logistic.cdf(x, params["Threshold"], params["Slope"])
    index = pd.Index(x, name="Intensity")
    logistic_points = pd.Series(
        y,
        index=index,
        name="Hit Rate",
    )
    logit_hit_rate = pd.Series(
        logit(logistic_points),
        index=logistic_points.index,
        name="logit(Hit Rate)",
    )
    return pd.concat([logistic_points, logit_hit_rate], axis=1)
