import pandas as pd
import numpy as np
from scipy.special import expit


def subjects(n_subjects):
    return list("ABCDEFG"[:n_subjects])


def generate(subjects, n_sessions, y, n_trials_per_stim_level):
    X = list(range(8))
    day = list(range(n_sessions))
    index = pd.MultiIndex.from_product(
        [subjects, day, X], names=["Subject", "Day", "x"]
    )
    return pd.DataFrame(
        {
            y: np.random.binomial(
                n_trials_per_stim_level,
                index.get_level_values("x") / max(X),
                len(index),
            )
            / n_trials_per_stim_level,
            "n": [n_trials_per_stim_level] * len(index),
        },
        index=index,
    )


def thresholds(data):
    return data.groupby(["Subject", "Day"]).mean().reset_index()


def logistic():
    index = pd.Index(np.linspace(-6, 6), name="x")
    return pd.Series(expit(index), index=index, name="Hit Rate")
