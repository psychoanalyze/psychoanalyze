from typing import List
import pandas as pd
import numpy as np
from scipy.stats import logistic as scipy_logistic
from cmdstanpy import CmdStanModel
import psychoanalyze as pa
from itertools import accumulate


def xrange_index(x_min, x_max):
    return pd.Index(list(range(x_min, x_max + 1)), name="x")


def subjects(n_subjects):
    return list("ABCDEFG"[:n_subjects])


def construct_index(subjects: List[str], days: List[int], x: List[float]):
    # structure levels based on presence of subject column
    if subjects:
        levels = [subjects, days, x]
        names = ["Subject", "Day", "x"]
    else:
        levels = [days, x]
        names = ["Day", "X"]
    return pd.MultiIndex.from_product(levels, names=names)


def generate_outcomes(n_trials_per_stim_level, index, threshold, scale):
    return np.random.binomial(
        n_trials_per_stim_level,
        scipy_logistic.cdf(index.get_level_values("x"), threshold, scale),
        len(index),
    )


def psych(hits, n_trials_per_stim_level, index, y):
    df = pd.DataFrame(
        {
            "Hits": hits,
            y: hits / n_trials_per_stim_level,
            "n": [n_trials_per_stim_level] * len(index),
        },
        index=index,
    )
    df["Hit Rate"] = df["Hits"] / df["n"]
    return df


def generate(
    subjects: List[str],
    n_sessions: int,
    y: str,
    n_trials_per_stim_level: int,
    X: List[int],
    threshold=0,
    scale=1,
):
    days = pa.session.generate(n_sessions)
    index = construct_index(subjects, days, X)
    hits = generate_outcomes(
        n_trials_per_stim_level=n_trials_per_stim_level,
        index=index,
        threshold=threshold,
        scale=scale,
    )
    psi = psych(hits, n_trials_per_stim_level, index, y)

    return psi


def logistic(threshold=0, scale=1, gamma=0, lambda_=0):
    x = np.linspace(scipy_logistic.ppf(0.01), scipy_logistic.ppf(0.99), 100)
    index = pd.Index(x, name="x")
    return pd.Series(
        gamma + (1 - gamma - lambda_) * scipy_logistic.cdf(x, threshold, scale),
        index=index,
        name="Hit Rate",
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
    return model.sample(chains=4, data=stan_data).summary()


def mu(points: pd.DataFrame):
    fit = fit_curve(points)
    df = fit.loc["mu", "5%":"95%"]
    return df.T


def params(points: pd.DataFrame, x: pd.Index, y: str) -> pd.DataFrame:
    fit = fit_curve(points)
    df = fit.loc[f"{y}[1]":f"{y}[{len(x)}]", "5%":"95%"]
    df[y] = df["50%"]
    df.index = x
    return df


def generate_animation_curves():
    n_blocks = 10
    n_trials_per_level_per_block = 10
    df = pd.concat(
        list(
            accumulate(
                [
                    pa.curve.generate(n_trials_per_level_per_block)
                    for _ in range(n_blocks)
                ]
            )
        )
    )
    df["Hit Rate"] = pa.curve.hit_rate
    return df
