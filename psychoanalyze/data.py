import pandas as pd
import random


def generate(n_subjects=2, n_sessions=10):
    subjects = list("ABCDEFG"[:n_subjects])
    index = pd.MultiIndex.from_product(
        [subjects, list(range(n_sessions))], names=["Subject", "Day"]
    )
    return pd.DataFrame([{"Threshold": random.random()} for _ in index], index=index)
