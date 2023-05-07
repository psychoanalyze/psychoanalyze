import pandas as pd


def load(data_path):
    return pd.read_csv(
        data_path / "subjects.csv",
        index_col="Monkey",
        parse_dates=["Surgery Date"],
    )
