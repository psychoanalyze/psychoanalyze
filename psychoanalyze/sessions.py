from typing import List
import pandas as pd


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
    return pd.read_csv("data/normalized/sessions.csv", parse_dates=["Date"])


def days(sessions, subjects):
    df = sessions.join(subjects, on="Monkey")
    return (pd.to_datetime(df["Date"]) - df["Surgery Date"]).dt.days
