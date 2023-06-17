import pandas as pd
import plotly.express as px
from scipy.stats import binom
import psychoanalyze as pa
from dash import dash_table
import pathlib
from plotly import graph_objects as go
import numpy as np
import pandera as pr
from pandera.typing import DataFrame, Series
from typing import cast
import cmdstanpy as stan


index_levels = ["Amp1", "Width1", "Freq1", "Dur1"]


class Points(pr.DataFrameModel):
    n: int
    Hits: int


def from_trials(trials: Series[int]) -> DataFrame[Points]:
    df = (
        trials.groupby("Intensity")
        .agg(["count", "sum"])
        .rename(columns={"count": "n", "sum": "Hits"})
    )
    df["Hit Rate"] = df["Hits"] / df["n"]
    return cast(DataFrame[Points], df)


def load(data_path=pathlib.Path("data")) -> DataFrame[Points]:
    trials = pa.trials.load(data_path)
    return from_trials(trials)


def dimension(points):
    amp1, width1 = (
        points.index.get_level_values(param) for param in ["Amp1", "Width1"]
    )
    if amp1.nunique() > 1 and width1.nunique() == 1:
        return "Amp"
    elif width1.nunique() > 1 and amp1.nunique() == 1:
        return "Width"
    elif width1.nunique() > 1 and amp1.nunique() > 1:
        return "Both"


def prep_fit(points: pd.DataFrame, dimension="Amp1"):
    points = points.reset_index()
    return {
        "X": len(points),
        "x": points[f"{dimension}"].to_numpy(),
        "N": points["n"].to_numpy(),
        "hits": points["Hits"].to_numpy(),
    }


def model():
    return stan.CmdStanModel(stan_file="models/binomial_regression.stan")


# def fit(ready_for_fit: pd.DataFrame) -> pd.DataFrame:
#     _model = model()
#     return _model.sample(chains=4, data=ready_for_fit)


def fit(points, save_to=None, block=None):
    points = points[["x", "Hits", "n"]]
    if len(points):
        data = points.to_numpy()
        fit = pa.fit(data)
        fit = pd.DataFrame(
            {
                "Threshold": [fit["Fit"][0]],
                "width": [fit["Fit"][1]],
                "gamma": [fit["Fit"][2]],
                "lambda": [fit["Fit"][3]],
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
            fit.to_csv(save_to)
        return fit
    else:
        return pd.Series(
            {
                "Threshold": None,
                "width": None,
                "lambda": None,
                "gamma": None,
                "err+": None,
                "err-": None,
            }
        )


def plot(points, trendline=None):
    points["Hit Rate"] = points["Hits"] / points["n"]
    return px.scatter(
        points.reset_index(),
        x="x",
        y="Hit Rate",
        size="n",
        color=points.get("Monkey"),
        template=pa.plot.template,
        trendline=trendline,
    )


def generate(x, n, p):
    return pd.Series(
        [binom.rvs(n[i], p[i]) for i in range(len(x))],
        index=pd.Index(x, name="Amplitude (µA)"),
        name="Hit Rate",
    )


def datatable(data):
    table = dash_table.DataTable(
        data.reset_index()[["Amp1", "Hit Rate", "n"]].to_dict("records"),
        columns=[
            {
                "id": "Amp1",
                "name": "Amp1",
                "type": "numeric",
                "format": dash_table.Format.Format(
                    precision=2, scheme=dash_table.Format.Scheme.fixed
                ),
            },
            {
                "id": "Hit Rate",
                "name": "Hit Rate",
                "type": "numeric",
                "format": dash_table.Format.Format(
                    precision=2, scheme=dash_table.Format.Scheme.fixed
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
    return table


def from_store(store_data):
    trials = pa.trials.from_store(store_data)
    return from_trials(trials)


def combine_plots(fig1, fig2):
    return go.Figure(data=fig1.data + fig2.data)


def fixed_magnitude(points):
    dim = dimension(points)
    if dim == "Amp":
        return points.index.get_level_values("Width1")[0]
    if dim == "Width":
        return points.index.get_level_values("Amp1")[0]


def n(trials):
    return trials.groupby(level=["Subject", "Block"]).count()


def to_block(points):
    return points.groupby(level=["Subject", "Block"]).sum()


def psi(x: np.ndarray, threshold: float, width: float, gamma: float, lambda_: float):
    return gamma + (1 - gamma - lambda_) / (
        1 + np.exp(-gamma * (x - threshold) / width) ** lambda_
    )
