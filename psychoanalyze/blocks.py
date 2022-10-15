import pandas as pd
import numpy as np
from scipy.stats import logistic  # type: ignore
from scipy.special import logit, expit  # type: ignore
import psychoanalyze as pa
import plotly.express as px  # type: ignore


dims = ["Amp2", "Width2", "Freq1", "Dur1", "Active Channels", "Return Channels"]


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


def from_points(points: pd.DataFrame):
    return pd.DataFrame(
        {"Fixed Magnitude": [], "Dimension": []},
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


def from_trials(trials: pd.DataFrame) -> pd.Series:
    points = pa.points.from_trials(trials)
    return from_points(points)


def dimension(points, dims=None):
    if dims is None:
        return pa.points.dimension(points)
    return points.groupby(
        [dim for dim in list(points.index.names) if dim not in dims]
    ).apply(pa.points.dimension)


def fit(df):
    return (
        df.groupby(pa.schemas.block_index_levels)
        .apply(pa.points.fit, dimension="Amp1")
        .agg(lambda: 1)
    )


def empty():
    return pd.Series(
        [], name="Hit Rate", index=pd.Index([], name="Amplitude (µA)"), dtype=float
    )


def plot_fits(df):
    x = np.linspace(-3, 3, 100)
    y = expit(x)
    return px.line(df.reset_index(), x=x, y=y)


def load():
    return from_trials(pa.trials.load())
