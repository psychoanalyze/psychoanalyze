import pandas as pd

__version__ = "0.1.0"


def fake() -> pd.DataFrame:
    return pd.DataFrame(
        {"Result": [0, 1], "x": [1, 1]}, index=pd.Index([1, 2], name="Trial")
    )


def curve(trials: pd.DataFrame):
    return trials.groupby("x").mean()
