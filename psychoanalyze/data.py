import pandas as pd
import random


def subjects(n_subjects):
    return list("ABCDEFG"[:n_subjects])


def generate(subjects, n, x, y):
    index = pd.MultiIndex.from_product([subjects, list(range(n))], names=["Subject", x])
    return pd.DataFrame(
        {
            y: [random.random() for _ in index],
        },
        index=index,
    )
