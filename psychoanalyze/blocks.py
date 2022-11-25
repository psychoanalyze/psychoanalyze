import pandas as pd
import numpy as np
from scipy.stats import logistic  # type: ignore
from scipy.special import logit, expit  # type: ignore
import psychoanalyze as pa
import plotly.express as px  # type: ignore
import os
import pathlib


dims = ["Amp2", "Width2", "Freq2", "Dur2", "Active Channels", "Return Channels"]
index_levels = dims


def add_posterior(data, posterior):
    return pd.concat(
        [data, posterior],
        keys=["Observed", "Posterior"],
        names=["Type"],
    ).reset_index()


def generate(n_trials_per_level=100):
    index = pd.Index(range(-3, 4), name="x")
    n = [n_trials_per_level] * len(index)
    p = logistic.cdf(index)
    return pd.DataFrame({"n": n, "Hits": np.random.binomial(n, p)}, index=index)


def hit_rate(df: pd.DataFrame) -> pd.Series:
    return df["Hits"] / df["n"]


def xrange_index(x_min, x_max):
    return pd.Index(list(range(x_min, x_max + 1)), name="x")


def transform(hit_rate, y: str):
    return logit(hit_rate) if y == "alpha" else hit_rate


def prep_psych_curve(curves_data: pd.DataFrame, x: pd.Index, y: str):
    curves_data.index = x
    df = pa.points.fit(curves_data)
    df = pa.data.reshape_fit_results(df, x, y)
    return df


def get_fit_param(fit: pd.DataFrame, name: str):
    return fit.loc[name, "50%"]


def from_points(points: pd.DataFrame, dim=None):
    levels = pa.schemas.block_index_levels
    if dim == "Amp":
        levels = levels + ["Width1"]
        df = points.groupby(levels).apply(pa.points.to_block)
        return df[df["n Levels"] > 1].drop(columns="Dimension")
    return points.groupby(levels).apply(pa.points.to_block)


def from_trials(trials: pd.DataFrame) -> pd.Series:
    points = pa.points.from_trials(trials)
    return from_points(points)


def dimensions(points, dims=None):
    if dims is None:
        return pa.points.dimension(points)
    return points.groupby(
        [dim for dim in list(points.index.names) if dim not in dims]
    ).apply(pa.points.dimension)


def fits(points):
    if len(points):
        return points.groupby(pa.schemas.block_index_levels).apply(pa.points.fit)
    else:
        return pd.DataFrame(
            {"Threshold": [], "Fixed Magnitude": [], "Dimension": []},
            index=pd.MultiIndex.from_frame(
                pd.DataFrame(
                    {
                        "Monkey": [],
                        "Date": [],
                        "Amp2": [],
                        "Width2": [],
                        "Freq2": [],
                        "Dur2": [],
                        "Active Channels": [],
                        "Return Channels": [],
                    }
                )
            ),
        )


def empty():
    return pd.Series(
        [], name="Hit Rate", index=pd.Index([], name="Amplitude (µA)"), dtype=float
    )


def plot_fits(df):
    x = np.linspace(-3, 3, 100)
    y = expit(x)
    return px.line(df.reset_index(), x=x, y=y)


def load_cached(data_path):
    channel_config = ["Active Channels", "Return Channels"]
    blocks = pd.read_csv(data_path / "blocks.csv", parse_dates=["Date"]).set_index(
        pa.sessions.dims + pa.stimulus.ref_dims + channel_config
    )
    blocks["Day"] = days(blocks, pa.subjects.load(data_path))
    return blocks


def load(data_path=pathlib.Path("data"), monkey=None, day=None, dim=None):
    blocks_path = data_path / "blocks.csv"
    if os.path.exists(blocks_path):
        blocks = load_cached(data_path)
        if monkey:
            if day:
                blocks = blocks[blocks["Day"] == day]
            else:
                blocks = blocks.xs(monkey, drop_level=False)
        blocks = blocks[blocks["n Levels"] > 1]
        return blocks
    else:
        blocks = from_trials(pa.trials.load(data_path))
        blocks.to_csv(blocks_path)
        return blocks


def fixed_magnitudes(points):
    return points.groupby(pa.schemas.block_index_levels).agg(pa.points.fixed_magnitude)


def days(blocks, intervention_dates):
    blocks = blocks.join(intervention_dates, on="Monkey")
    days = (blocks.index.get_level_values("Date") - blocks["Surgery Date"]).dt.days
    days.name = "Days"
    return days


def n_trials(trials):
    session_cols = ["Monkey", "Date"]
    ref_stim_cols = ["Amp2", "Width2", "Freq2", "Dur2"]
    channel_config = ["Active Channels", "Return Channels"]
    return trials.groupby(session_cols + ref_stim_cols + channel_config)[
        "Result"
    ].count()


def read_fit(path, block):
    session_cols = ["Monkey", "Date"]
    ref_stim_cols = ["Amp2", "Width2", "Freq2", "Dur2"]
    channel_config = ["Active Channels", "Return Channels"]
    fits = pd.read_csv(
        path,
        index_col=session_cols + ref_stim_cols + channel_config,
        parse_dates=["Date"],
    )
    fits["err+"] = 0.0
    fits["err-"] = 0.0
    if block in fits.index:
        return fits.loc[block]
    else:
        return pd.Series()


def experiment_type(blocks):
    ref_stim = blocks.reset_index()[["Amp2", "Width2", "Freq2", "Dur2"]]
    ref_charge = ref_stim["Amp2"] * ref_stim["Width2"]
    blocks.loc[ref_charge == 0, "Experiment Type"] = "Detection"
    blocks.loc[ref_charge != 0, "Experiment Type"] = "Discrimination"
    return blocks["Experiment Type"]


def isValid(block):
    return any(block["Hit Rate"] > 0.5) & any(block["Hit Rate"] < 0.5)


def monkey_counts(data):
    summary = (
        data.index.get_level_values("Monkey").value_counts().rename("Total Blocks")
    )
    summary.index.name = "Monkey"
    return summary
