import os
from typing import List
import pandas as pd
import pathlib

import psychoanalyze as pa


dims = ["Monkey", "Date"]
index_levels = dims


def generate(n: int) -> List[int]:
    return list(range(n))


def from_trials_csv(path, cache=False):
    df = pd.read_csv(path)[["Monkey", "Date"]].drop_duplicates()
    if cache:
        df.to_csv("data/normalized/sessions.csv", index=False)
    return df


def day_marks(subjects, sessions, monkey):
    surgery_date = pd.to_datetime(
        subjects.loc[subjects["Monkey"] == monkey, "Surgery Date"]
    )[0]
    sessions = sessions[sessions["Monkey"] == "U"]
    sessions["Days"] = (pd.to_datetime(sessions["Date"]) - surgery_date).dt.days
    return {sessions.loc[i, "Days"]: sessions.loc[i, "Date"] for i in sessions.index}


def cache():
    pd.read_csv("data/trials.csv")[["Monkey", "Date"]].drop_duplicates().to_csv(
        "data/normalized/sessions.csv", index=False
    )


def load(data_path=pathlib.Path("data"), monkey=None):
    if os.path.exists(data_path / "sessions.csv"):
        sessions = pd.read_csv(data_path / "sessions.csv")
    else:
        trials = pa.trials.load(data_path)
        if monkey:
            trials = trials[trials.index.get_level_values("Monkey") == monkey]
        sessions = (
            trials.groupby(["Monkey", "Date"])[["Result"]]
            .count()
            .rename(columns={"Result": "n Trials"})
        )
    sessions["Block"] = days(sessions, pa.subjects.load(data_path))
    return sessions


def days(sessions: pd.DataFrame, subjects):
    df = sessions.join(subjects, on="Monkey")
    return (
        pd.to_datetime(df.index.get_level_values("Date")) - df["Surgery Date"]
    ).dt.days


def n_trials(sessions, trials):
    return trials.groupby(["Monkey", "Date"])[["Result"]].count()


def load_cached(data_dir, monkey=None):
    sessions = pd.read_csv(data_dir / "sessions.csv", index_col=["Monkey", "Date"])
    return sessions[sessions.index.get_level_values("Monkey") == monkey]


def generate_trials(
    n_trials: int,
    model_params: dict[str, float],
    n_days: int,
) -> pd.Series:
    return pd.concat(
        {
            day: pa.blocks.generate_trials(n_trials, model_params)
            for day in range(n_days)
        },
        names=["Block"],
    )
