import pandas as pd
import cmdstanpy as stan


def from_trials(trials):
    trials = trials[trials["Result"].isin([0, 1])]

    return (
        trials.groupby(trials.index)["Result"]
        .agg(["count", "sum"])
        .rename(columns={"count": "n", "sum": "Hits"})
    )


def dimension(points):
    df = points
    if df["Amp1"].nunique() > 1 and df["Width1"].nunique() == 1:
        return "Amp"
    elif df["Width1"].nunique() > 1 and df["Amp1"].nunique() == 1:
        return "Width"
    elif df["Width1"].nunique() > 1 and df["Amp1"].nunique() > 1:
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
