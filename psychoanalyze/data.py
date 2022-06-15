from typing import List
import pandas as pd
import numpy as np
from scipy.stats import logistic as scipy_logistic
import psychoanalyze as pa
from itertools import accumulate


def subjects(n_subjects):
    return list("ABCDEFG"[:n_subjects])


def construct_index(subjects: List[str], days: List[int], x: List[float]):
    levels = [days, x]
    names = ["Day", "x"]
    if subjects:
        levels = [subjects] + levels
        names = ["Subject"] + names
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
    df["Hit Rate"] = pa.curve.hit_rate
    return df


def logistic(threshold=0, scale=1, gamma=0, lambda_=0):
    x = np.linspace(scipy_logistic.ppf(0.01), scipy_logistic.ppf(0.99), 100)
    index = pd.Index(x, name="x")
    return pd.Series(
        gamma + (1 - gamma - lambda_) * scipy_logistic.cdf(x, threshold, scale),
        index=index,
        name="Hit Rate",
    )


def mu(points: pd.DataFrame):
    fit = pa.curve.fit(points)
    df = fit.loc["mu", "5%":"95%"]
    return df.T


def params(fit: pd.DataFrame, x: pd.Index, y: str) -> pd.DataFrame:
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
