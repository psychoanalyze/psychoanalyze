from typing import List
import pandas as pd


def generate(n: int) -> List[int]:
    return list(range(n))


def from_trials_csv(path):
    return pd.read_csv(path)[["Monkey", "Date"]].drop_duplicates()
