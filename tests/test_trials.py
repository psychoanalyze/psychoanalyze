
"""Tests for psychoanalyze.trials module."""

from typing import Any

import polars as pl
import pytest

from psychoanalyze.data import trials


@pytest.fixture
def subjects() -> list[str]:
    """Subjects."""
    return ["A", "B"]


@pytest.fixture
def x() -> list[int]:
    """Intensity values."""
    return list(range(8))


def test_normalize() -> None:
    """Given a denormalized dataframe, returns normalized data."""
    fields = {
        "Session": ["Monkey", "Block"],
        "Reference Stimulus": ["Amp2", "Width2", "Freq2", "Dur2"],
        "Channel Configuration": ["Active Channels", "Return Channels"],
        "Test Stimulus": ["Amp1", "Width1", "Freq1", "Dur1"],
    }
    data: dict[str, list[Any]] = {
        field: []
        for field in fields["Session"]
        + fields["Reference Stimulus"]
        + fields["Channel Configuration"]
        + fields["Test Stimulus"]
    }
    _trials = pl.DataFrame(data)
    normalized_data = trials.normalize(_trials)
    assert normalized_data.keys() == {
        "Session",
        "Reference Stimulus",
        "Channel Config",
        "Test Stimulus",
    }


def test_labels() -> None:
    """Given trial result integers, translates to labels."""
    assert trials.labels([0, 1]) == ["Miss", "Hit"]
