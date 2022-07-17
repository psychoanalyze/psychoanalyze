import pandas as pd
import cmdstanpy as stan
import plotly.express as px  # type: ignore
from scipy.stats import binom  # type: ignore
import psychoanalyze as pa

dims = ["Amp1", "Width1", "Freq1", "Dur1"]

index_levels = pa.blocks.index_levels + dims


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
    return px.scatter(df.reset_index(), y="Hit Rate", template="plotly_white")


def generate(x, n, p):
    return pd.Series(
        [binom.rvs(n[i], p[i]) for i in range(len(x))],
        index=pd.Index(x, name="Amplitude (µA)"),
        name="Hit Rate",
    )


def load():
    trials = pa.trials.load("data/trials.csv")
    return from_trials(trials)
