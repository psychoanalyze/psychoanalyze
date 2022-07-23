import pandas as pd
import cmdstanpy as stan
import plotly.express as px  # type: ignore
from scipy.stats import binom  # type: ignore
import psychoanalyze as pa
from dash import dash_table
import pandera as pr

dims = ["Amp1", "Width1", "Freq1", "Dur1"]

index_levels = pa.blocks.index_levels + dims

schema = pr.DataFrameSchema(
    {
        "n": pr.Column(int, checks=pr.Check.isin([0, 1, 2, 3]), coerce=True),
        "Hits": pr.Column(int, checks=pr.Check.isin([0, 1, 2, 3]), coerce=True),
    },
    index=pr.MultiIndex(
        [
            pr.Index(str, name="Monkey", checks=pr.Check.isin(["U", "Y", "Z"])),
            pr.Index("datetime64", name="Date", coerce=True),
        ]
        + [pr.Index(float, name=dim) for dim in pa.blocks.stim_dims]
        + [pr.Index(int, name=dim) for dim in pa.blocks.channel_dims]
        + [pr.Index(float, name=dim) for dim in dims]
    ),
    coerce=True,
)


def from_trials(trials):
    trials = trials[trials["Result"].isin([0, 1])]
    return (
        trials.groupby(trials.index.names)["Result"]
        .agg(["count", "sum"])
        .rename(columns={"count": "n", "sum": "Hits"})
    )


def dimension(points):
    points
    amp1, width1 = (
        points.index.get_level_values(param) for param in ["Amp1", "Width1"]
    )
    if amp1.nunique() > 1 and width1.nunique() == 1:
        return "Amp"
    elif width1.nunique() > 1 and amp1.nunique() == 1:
        return "Width"
    elif width1.nunique() > 1 and amp1.nunique() > 1:
        return "Both"


def fit(points: pd.DataFrame, dimension="Amp1") -> pd.DataFrame:
    points = points.reset_index()
    stan_data = {
        "X": len(points),
        "x": points[f"{dimension}"].to_numpy(),
        "N": points["n"].to_numpy(),
        "hits": points["Hits"].to_numpy(),
    }
    model = stan.CmdStanModel(stan_file="models/binomial_regression.stan")
    return model.sample(chains=4, data=stan_data).summary()


def plot(df):
    df["Hit Rate"] = df["Hits"] / df["n"]
    df["Amplitude (µA)"] = df.index.get_level_values("Amp1")
    return px.scatter(
        df.reset_index(),
        x="Amplitude (µA)",
        y="Hit Rate",
        color="Monkey",
        template="plotly_white",
    )


def generate(x, n, p):
    return pd.Series(
        [binom.rvs(n[i], p[i]) for i in range(len(x))],
        index=pd.Index(x, name="Amplitude (µA)"),
        name="Hit Rate",
    )


def load():
    trials = pa.trials.load("data/trials.csv")
    return from_trials(trials)


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
