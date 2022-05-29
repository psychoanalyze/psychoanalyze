import pandas as pd
import numpy as np
from scipy.stats import logistic as scipy_logistic


def subjects(n_subjects):
    return list("ABCDEFG"[:n_subjects])


def generate(subjects, n_sessions, y, n_trials_per_stim_level, X, threshold=0, scale=1):
    day = list(range(n_sessions))
    index = pd.MultiIndex.from_product(
        [subjects, day, X], names=["Subject", "Day", "x"]
    )
    return pd.DataFrame(
        {
            y: np.random.binomial(
                n_trials_per_stim_level,
                scipy_logistic.cdf(index.get_level_values("x"), threshold, scale),
                len(index),
            )
            / n_trials_per_stim_level,
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
