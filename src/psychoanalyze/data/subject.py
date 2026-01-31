"""Helpers for subject-aware data handling."""

from __future__ import annotations

import polars as pl

SUBJECT_COLUMN = "Subject"
SUBJECT_ALIASES = ("Subject", "Monkey")


def resolve_subject_column(df: pl.DataFrame) -> str | None:
    """Return the subject column name if present."""
    for name in SUBJECT_ALIASES:
        if name in df.columns:
            return name
    return None


def ensure_subject_column(
    df: pl.DataFrame,
    default_value: str = "All",
) -> pl.DataFrame:
    """Ensure the dataframe has a Subject column."""
    if SUBJECT_COLUMN in df.columns:
        return df
    if "Monkey" in df.columns:
        return df.with_columns(pl.col("Monkey").alias(SUBJECT_COLUMN))
    return df.with_columns(pl.lit(default_value).alias(SUBJECT_COLUMN))
