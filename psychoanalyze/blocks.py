import pandas as pd
import numpy as np
from scipy.stats import logistic  # type: ignore
from scipy.special import logit, expit  # type: ignore
import psychoanalyze as pa
import plotly.express as px
import pandera as pr

stim_dims = ["Amp2", "Width2", "Freq2", "Dur2"]
channel_dims = ["Active Channels", "Return Channels"]

dims = stim_dims + channel_dims
index_levels = pa.sessions.dims + dims

schema = pr.DataFrameSchema(
    columns={"Threshold": pr.Column(dtype=float), "width": pr.Column(dtype=float)},
    index=pr.MultiIndex(
        [
            pr.Index(str, name="Monkey", checks=pr.Check.isin(["U", "Y", "Z"])),
            pr.Index("datetime64", name="Date", coerce=True),
        ]
        + [pr.Index(float, name=dim) for dim in stim_dims]
        + [pr.Index(int, name=dim) for dim in channel_dims]
    ),
)


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


def from_trials(trials: pd.DataFrame) -> pd.Series:
    """Arrange *method of constant stimuli* performance curves using trial data"""
    return trials["Result"].to_frame().mean()


def dimension(points, dims=None):
    if dims is None:
        return pa.points.dimension(points)
    return points.groupby(
        [dim for dim in list(points.index.names) if dim not in dims]
    ).apply(pa.points.dimension)


def fit(df):
    return df.groupby(pa.blocks.index_levels).apply(pa.points.fit, dimension="Amp1")


def empty():
    return pd.Series(
        [], name="Hit Rate", index=pd.Index([], name="Amplitude (µA)"), dtype=float
    )


def plot_fits(df):
    print(df["Mean"])
    x = np.linspace(-3, 3, 100)
    y = expit(x)
    return px.line(df.reset_index(), x=x, y=y)
