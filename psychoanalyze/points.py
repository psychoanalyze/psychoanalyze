import pandas as pd
import cmdstanpy as stan
import plotly.express as px  # type: ignore
from scipy.stats import binom  # type: ignore
import psychoanalyze as pa
from dash import dash_table  # type: ignore
import pathlib


def from_trials(trials):
    trials = trials[trials["Result"].isin([0, 1])]
    df = (
        trials.groupby(trials.index.names)["Result"]
        .agg(["count", "sum"])
        .rename(columns={"count": "n", "sum": "Hits"})
    )
    df["x"] = df.index.get_level_values("Amp1")
    return df


def load(data_path=pathlib.Path("data")):
    trials = pa.trials.load(data_path)
    points = from_trials(trials)
    points["Hit Rate"] = points["Hits"] / points["n"]
    return points


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


def fit(points):
    pass


#     if len(points):
#         options = {"expType": "YesNo"}
#         data = points.to_numpy()
#         result = ps.psignifit(data, options)
#         return {
#             "Threshold": result["Fit"][0],
#             "width": result["Fit"][1],
#             "gamma": result["Fit"][2],
#             "lambda": result["Fit"][3],
#             "beta": result["Fit"][4],
#         }


def plot(df):
    df["Hit Rate"] = df["Hits"] / df["n"]
    df["Amplitude (µA)"] = df.index.get_level_values("Amp1")
    return px.scatter(
        df.reset_index(),
        x="Amplitude (µA)",
        y="Hit Rate",
        color=df.get("Monkey"),
        template="plotly_white",
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
    for trace in fig2.data:
        fig1.add_trace(trace)
    return fig1


def fixed_magnitude(points):
    dim = dimension(points)
    if dim == "Amp":
        return 0
    if dim == "Width":
        return 0


def n(points):
    return len(points)


def to_block(points):
    return pd.Series(
        {
            # "Threshold": fit(points),
            "Dimension": dimension(points),
            "Fixed Magnitude": fixed_magnitude(points),
            "n Levels": n(points),
        }
    )
