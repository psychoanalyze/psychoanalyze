
"""Data transformation functions for subject-level data."""
import string
from pathlib import Path

import polars as pl

from psychoanalyze.data import sessions


def load(data_path: Path) -> pl.DataFrame:
    """Load subject data from csv."""
    df = pl.read_csv(data_path / "subjects.csv")
    df = df.with_columns(pl.col("Surgery Date").str.to_datetime())
    return df


def generate_letter_names(n_subjects: int) -> list[str]:
    """Generate a list of dummy subjects using capital letters in alph. order."""
    return list("ABCDEFG"[:n_subjects])


def generate_trials(
    n_trials: int,
    model_params: dict[str, float],
    n_days: int,
    n_subjects: int,
) -> pl.DataFrame:
    """Generate trial-level data, including subject-level info."""
    frames = []
    for subj in string.ascii_uppercase[:n_subjects]:
        df = sessions.generate_trials(n_trials, model_params, n_days)
        df = df.with_columns(pl.lit(subj).alias("Subject"))
        frames.append(df)
    return pl.concat(frames)
