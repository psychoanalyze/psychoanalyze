
"""Patito schemas for psychoanalyze dataframes.

Contains data table schemas of the hierarchical entities described above.
Uses patito for Polars DataFrame validation.
"""
from datetime import datetime

import patito as pt

session_dims = ["Monkey", "Date"]
block_stim_dims = ["Amp2", "Width2", "Freq2", "Dur2"]
block_channel_dims = ["Active Channels", "Return Channels"]
block_dims = block_stim_dims + block_channel_dims
point_dims = ["Amp1", "Width1", "Freq1", "Dur1"]

block_index_levels = session_dims + block_dims
points_index_levels = block_index_levels + point_dims


class Trials(pt.Model):
    """Trial-level data schema."""

    Intensity: float
    Result: int
    Block: int


class Points(pt.Model):
    """Points-level data schema."""

    Block: int
    Intensity: float
    n_trials: int = pt.Field(alias="n trials")
    Hits: int
    Hit_Rate: float = pt.Field(alias="Hit Rate")
    logit_Hit_Rate: float | None = pt.Field(alias="logit(Hit Rate)", default=None)


class Blocks(pt.Model):
    """Block-level data schema."""

    Threshold: float
    width: float | None = None
    Monkey: str | None = None
    Date: datetime | None = None


class PsiAnimation(pt.Model):
    """Psychometric function animation dataset."""

    trial_id: int
    intensity: float
    hit_rate: float


class PsiAnimationFrame(pt.Model):
    """Single psychometric function animation frame."""

    intensity: float
    hit_rate: float


def validate_trials(df: pt.DataFrame) -> pt.DataFrame:
    """Validate a trials DataFrame."""
    return Trials.validate(df)


def validate_points(df: pt.DataFrame) -> pt.DataFrame:
    """Validate a points DataFrame."""
    return Points.validate(df)


def validate_blocks(df: pt.DataFrame) -> pt.DataFrame:
    """Validate a blocks DataFrame."""
    return Blocks.validate(df)
