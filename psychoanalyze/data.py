import pandas as pd
import random


def subjects(n_subjects):
    return list("ABCDEFG"[:n_subjects])


def generate(subjects, n, name, label):
    index = pd.MultiIndex.from_product(
        [subjects, list(range(n))], names=["Subject", name]
    )
    return pd.DataFrame(
        {
            label: [random.random() for _ in index],
        },
        index=index,
    )
