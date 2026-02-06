
"""Utilities for session-level data.

**Sessions** represent a single day of experiments performed by a subject. It may
contain several blocks.
"""
from pathlib import Path

import polars as pl

from psychoanalyze.data import blocks

dims = ["Subject", "Date"]
index_levels = dims


def generate(n: int) -> list[int]:
    """Generate session-level data."""
    return list(range(n))


def cache_results(sessions: pl.DataFrame) -> None:
    """Save session data to csv."""
    sessions.write_csv("data/normalized/sessions.csv")


def from_trials_csv(path: Path) -> pl.DataFrame:
    """Aggregate to session level from trial-level data."""
    trials = pl.read_csv(path)
    return trials.select(["Subject", "Date"]).unique()


def day_marks(subjects: pl.DataFrame, sessions: pl.DataFrame, monkey: str) -> dict:
    """Calculate days since surgery date for a given subject."""
    surgery_date_str = subjects.filter(pl.col("Subject") == monkey)["Surgery Date"][0]
    surgery_date = pl.Series([surgery_date_str]).str.to_datetime()[0]
    sessions = sessions.filter(pl.col("Subject") == monkey)
    sessions = sessions.with_columns(
        (pl.col("Date").str.to_datetime() - surgery_date).dt.total_days().alias("Days"),
    )
    return dict(zip(sessions["Days"].to_list(), sessions["Date"].to_list()))


def days(sessions: pl.DataFrame, subjects: pl.DataFrame) -> pl.Series:
    """Calculate days since surgery date."""
    sessions_subjects = sessions.join(subjects, on="Subject")
    return (
        sessions_subjects["Date"] - sessions_subjects["Surgery Date"]
    ).dt.total_days()


def n_trials(trials: pl.DataFrame) -> pl.DataFrame:
    """Count trials per session."""
    return trials.group_by(["Subject", "Date"]).agg(pl.len().alias("n_trials"))


def load(data_dir: Path) -> pl.DataFrame:
    """Load session-level data from csv."""
    return pl.read_csv(data_dir / "sessions.csv")


def generate_trials(
    n_trials: int,
    model_params: dict[str, float],
    n_days: int,
) -> pl.DataFrame:
    """Generate trial-level data for session-level context."""
    frames = []
    for day in range(n_days):
        df = blocks.generate_trials(n_trials, model_params).with_columns(pl.lit(day).alias("Block"))
        frames.append(df)
    return pl.concat(frames)
