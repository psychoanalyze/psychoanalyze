from typing import List
import pandas as pd

import psychoanalyze as pa


dims = ["Monkey", "Date"]


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


def load():
    sessions = (
        pd.read_csv("data/trials.csv", parse_dates=["Date"])[["Monkey", "Date"]]
        .drop_duplicates()
        .set_index(["Monkey", "Date"])
    )
    sessions["Day"] = days(sessions, pa.subjects.load())
    return sessions


def days(sessions, subjects):
    df = sessions.join(subjects, on="Monkey")
    return (
        pd.to_datetime(df.index.get_level_values("Date")) - df["Surgery Date"]
    ).dt.days


def n_trials(sessions, trials):
    trials = trials.join(sessions)
    return trials.groupby(["Monkey", "Day"])[["Result"]].count()
