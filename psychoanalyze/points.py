import pathlib

import cmdstanpy as stan
import numpy as np
import pandas as pd
import pandera as pr
import plotly.express as px
from dash import dash_table
from pandera.typing import DataFrame
from plotly import graph_objects as go
from scipy.stats import binom

from psychoanalyze import trials

index_levels = ["Amp1", "Width1", "Freq1", "Dur1"]


class Points(pr.DataFrameModel):
    n: int
    Hits: int
    blockID: int


def from_trials(_trials: DataFrame[trials.Trials]):
    return (
        _trials.groupby("Intensity")[["Result"]]
        .agg(["count", "sum"])
        .rename(columns={"count": "n", "sum": "Hits"})
    )["Result"]


def load(data_path=pathlib.Path("data")) -> DataFrame[Points]:
    _trials = trials.load(data_path)
    return from_trials(_trials)


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


def generate(x: list[float], n: list[int], p: list[float]):
    return pd.Series(
        [binom.rvs(n[i], p[i]) for i in range(len(x))],
        index=pd.Index(x, name="Intensity"),
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
    _trials = trials.from_store(store_data)
    return from_trials(_trials)


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


def plot(df):
    return px.scatter(df.reset_index(), x="Intensity", y="Hit Rate")
