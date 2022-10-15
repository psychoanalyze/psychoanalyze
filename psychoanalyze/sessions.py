from typing import List
import pandas as pd


dims = ["Monkey", "Date"]


def generate(n: int) -> List[int]:
    return list(range(n))


def from_trials_csv(path):
    df = pd.read_csv(path)[["Monkey", "Date"]].drop_duplicates()
    df.to_csv("data/normalized/sessions.csv", index=False)
    return df
