import pandas as pd
import numpy as np
from scipy.stats import logistic as scipy_logistic
from cmdstanpy import CmdStanModel
from unittest.mock import MagicMock


def subjects(n_subjects):
    return list("ABCDEFG"[:n_subjects])


def generate(subjects, n_sessions, y, n_trials_per_stim_level, X, threshold=0, scale=1):
    day = list(range(n_sessions))
    index = pd.MultiIndex.from_product(
        [subjects, day, X], names=["Subject", "Day", "x"]
    )
    hits = np.random.binomial(
        n_trials_per_stim_level,
        scipy_logistic.cdf(index.get_level_values("x"), threshold, scale),
        len(index),
    )
    return pd.DataFrame(
        {
            "Hits": hits,
            y: hits / n_trials_per_stim_level,
            "n": [n_trials_per_stim_level] * len(index),
        },
        index=index,
    )


def thresholds(data):
    return data.groupby(["Subject", "Day"]).mean().reset_index()


def logistic(threshold=0, scale=1):
    x = np.linspace(scipy_logistic.ppf(0.01), scipy_logistic.ppf(0.99), 100)
    index = pd.Index(x, name="x")
    return pd.Series(
        scipy_logistic.cdf(x, threshold, scale), index=index, name="Hit Rate"
    )


def fit_curve(points: pd.DataFrame):
    points = points.reset_index()
    stan_data = {
        "X": len(points),
        "x": points["x"].to_numpy(),
        "N": points["n"].to_numpy(),
        "hits": points["Hits"].to_numpy(),
    }
    model = CmdStanModel(stan_file="models/binomial_regression.stan")
    df = model.sample(chains=4, data=stan_data).summary()
    posterior_estimates = df.loc["p[1]":"p[9]", "50%"]
    posterior_estimates.index = points.set_index("x").index
    return posterior_estimates
