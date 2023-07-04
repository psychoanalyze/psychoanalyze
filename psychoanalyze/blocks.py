"""Block-level data."""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pandera import DataFrameModel
from pandera.typing import DataFrame
from scipy.special import expit, logit
from scipy.stats import logistic
from sklearn.linear_model import LogisticRegression

from psychoanalyze import data, points, schemas, sessions, stimulus, subjects, trials

dims = ["Amp2", "Width2", "Freq2", "Dur2", "Active Channels", "Return Channels"]
index_levels = dims


class Blocks(DataFrameModel):

    """Blocks type for Pandera."""

    slope: float
    threshold: float


def add_posterior(data: pd.Series, posterior: pd.Series) -> pd.DataFrame:
    """Combine observed and simulated data."""
    return pd.concat(
        [data, posterior],
        keys=["Observed", "Posterior"],
        names=["Type"],
    ).reset_index()


def generate(n_trials_per_level: int = 100) -> pd.DataFrame:
    """Generate block-level data."""
    index = pd.Index(range(-3, 4), name="x")
    n = [n_trials_per_level] * len(index)
    p = logistic.cdf(index)
    return pd.DataFrame(
        {"n": n, "Hits": np.random.default_rng().binomial(n, p)},
        index=index,
    )


def hit_rate(df: pd.DataFrame) -> pd.Series:
    """Calculate hit rate from hits and number of trials."""
    return df["Hits"] / df["n"]


def xrange_index(x_min: float, x_max: float, n_levels: int) -> pd.Index:
    """Generate x range values from min and max."""
    return pd.Index(np.linspace(x_min, x_max, n_levels), name="x")


def transform(hit_rate: float, y: str) -> float:
    """Logit transform hit rate."""
    return logit(hit_rate) if y == "alpha" else hit_rate


def prep_psych_curve(curves_data: pd.DataFrame, x: pd.Index, y: str) -> pd.DataFrame:
    """Transform & fit curve data."""
    curves_data.index = x
    fits = points.fit(curves_data)
    return data.reshape_fit_results(fits, x, y)


def dimensions(_points: pd.DataFrame, dims: list[str]) -> pd.Series:
    """Calculate dimensions for multiple blocks."""
    return _points.groupby(
        [dim for dim in list(_points.index.names) if dim not in dims],
    ).apply(points.dimension)


def fits(_points: pd.DataFrame) -> pd.DataFrame:
    """Apply fits to multiple blocks."""
    if len(_points):
        return _points.groupby(schemas.block_index_levels).apply(points.fit)
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


def empty() -> pd.Series:
    """Return empty block Series."""
    return pd.Series(
        [],
        name="Hit Rate",
        index=pd.Index([], name="Amplitude (µA)"),
        dtype=float,
    )


def plot_fits(blocks: pd.DataFrame) -> go.Figure:
    """Plot fits."""
    x = np.linspace(-3, 3, 100)
    y = expit(x)
    return px.line(blocks.reset_index(), x=x, y=y)


def load_cached(data_path: Path) -> pd.DataFrame:
    """Load block data from csv."""
    channel_config = ["Active Channels", "Return Channels"]
    blocks = pd.read_csv(data_path / "blocks.csv", parse_dates=["Date"]).set_index(
        sessions.dims + stimulus.ref_dims + channel_config,
    )
    blocks["Block"] = days(blocks, subjects.load(data_path))
    return blocks


def load(
    data_path: Path = Path("data"),
) -> pd.DataFrame:
    """Load blocks data from csv."""
    return load_cached(data_path / "blocks.csv")


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


def from_points(points: DataFrame[points.Points]) -> pd.DataFrame:
    """Aggregate block measures from points data."""
    return points.groupby("BlockID")[["n"]].sum()
