import pandas as pd


def load():
    return pd.read_csv(
        "data/normalized/subjects.csv", index_col="Monkey", parse_dates=["Surgery Date"]
    )
