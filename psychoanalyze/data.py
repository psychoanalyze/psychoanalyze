import pandas as pd
import random


def subjects(n_subjects):
    return list("ABCDEFG"[:n_subjects])


def generate(subjects, n, y):
    index = pd.MultiIndex.from_product(
        [subjects, list(range(n)), list(range(8))], names=["Subject", "Day", "x"]
    )
    return pd.DataFrame(
        {y: [random.random() for _ in index]},
        index=index,
    )


def thresholds(data):
    return data.groupby(["Subject", "Day"]).mean().reset_index()
