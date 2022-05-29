import pandas as pd
import numpy as np


def subjects(n_subjects):
    return list("ABCDEFG"[:n_subjects])


def generate(subjects, n, y):
    X = list(range(8))
    day = list(range(n))
    index = pd.MultiIndex.from_product(
        [subjects, day, X], names=["Subject", "Day", "x"]
    )
    return pd.DataFrame(
        {
            y: np.random.binomial(10, index.get_level_values("x") / max(X), len(index))
            / 10,
            "n": [10] * len(index),
        },
        index=index,
    )


def thresholds(data):
    return data.groupby(["Subject", "Day"]).mean().reset_index()
