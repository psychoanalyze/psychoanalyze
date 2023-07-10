# Copyright 2023 Tyler Schlichenmeyer

# This file is part of PsychoAnalyze.
# PsychoAnalyze is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# PsychoAnalyze is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# PsychoAnalyze. If not, see <https://www.gnu.org/licenses/>.

"""Utilities for session-level data.

**Sessions** represent a single day of experiments performed by a subject. It may
contain several blocks.
"""
from pathlib import Path

import pandas as pd

from psychoanalyze.data import blocks

dims = ["Monkey", "Date"]
index_levels = dims


def generate(n: int) -> list[int]:
    """Generate session-level data."""
    return list(range(n))


def cache_results(sessions: pd.DataFrame) -> None:
    """Save session data to csv."""
    sessions.to_csv("data/normalized/sessions.csv", index=False)


def from_trials_csv(path: Path) -> pd.DataFrame:
    """Aggregate to session level from trial-level data."""
    return pd.read_csv(path)[["Monkey", "Date"]].drop_duplicates()


def day_marks(subjects: pd.DataFrame, sessions: pd.DataFrame, monkey: str) -> dict:
    """Calculate days since surgery date for a given subject."""
    surgery_date = pd.to_datetime(
        subjects.loc[subjects["Monkey"] == monkey, "Surgery Date"],
    )[0]
    sessions = sessions[sessions["Monkey"] == "U"]
    sessions["Days"] = (pd.to_datetime(sessions["Date"]) - surgery_date).dt.days
    return {sessions.loc[i, "Days"]: sessions.loc[i, "Date"] for i in sessions.index}


def days(sessions: pd.DataFrame, subjects: pd.DataFrame) -> pd.Series:
    """Calculate days since surgery date."""
    sessions_subjects = sessions.join(subjects, on="Monkey")
    return (
        pd.to_datetime(sessions_subjects.index.get_level_values("Date"))
        - sessions_subjects["Surgery Date"]
    ).dt.days


def n_trials(trials: pd.DataFrame) -> pd.DataFrame:
    """Count trials per session."""
    return trials.groupby(["Monkey", "Date"])[["Result"]].count()


def load(data_dir: Path) -> pd.DataFrame:
    """Load session-level data from csv."""
    return pd.read_csv(data_dir / "sessions.csv", index_col=["Monkey", "Date"])


def generate_trials(
    n_trials: int,
    model_params: dict[str, float],
    n_days: int,
) -> pd.DataFrame:
    """Generate trial-level data for session-level context."""
    return pd.concat(
        {day: blocks.generate_trials(n_trials, model_params) for day in range(n_days)},
        names=["Block"],
    )
