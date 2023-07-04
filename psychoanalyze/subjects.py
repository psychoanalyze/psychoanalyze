"""Data transformation functions for subject-level data."""
import string
from pathlib import Path

import pandas as pd

from psychoanalyze import sessions


def load(data_path: Path) -> pd.DataFrame:
    """Load subject data from csv."""
    return pd.read_csv(
        data_path / "subjects.csv",
        index_col="Monkey",
        parse_dates=["Surgery Date"],
    )


def generate_letter_names(n_subjects: int) -> list[str]:
    """Generate a list of dummy subjects using capital letters in alph. order."""
    return list("ABCDEFG"[:n_subjects])


def generate_trials(
    n_trials: int,
    model_params: dict[str, float],
    n_days: int,
    n_subjects: int,
) -> pd.DataFrame:
    """Generate trial-level data, including subject-level info."""
    return pd.concat(
        {
            subj: sessions.generate_trials(n_trials, model_params, n_days)
            for subj in string.ascii_uppercase[:n_subjects]
        },
        names=["Subject"],
    )
