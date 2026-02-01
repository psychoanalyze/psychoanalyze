
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
        "Session": ["Subject", "Block"],
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


def test_fit_returns_inferencedata() -> None:
    """Fit returns posterior draws for trial data."""
    trials_df = pl.DataFrame(
        {
            "Intensity": [0.0, 1.0, 2.0, 3.0],
            "Result": [0, 0, 1, 1],
        },
    )
    idata = trials.fit(trials_df, draws=50, tune=50, chains=1, random_seed=1)
    summary = trials.summarize_fit(idata)
    assert set(summary) == {"Threshold", "Slope"}


def test_load_preserves_subject_column() -> None:
    """Loading sample data should preserve Subject column with actual subject IDs."""
    from pathlib import Path

    data_path = Path(__file__).parent.parent / "data" / "trials.csv"
    if not data_path.exists():
        pytest.skip("Sample data not available")

    trials_df = trials.load(data_path)
    assert "Subject" in trials_df.columns, (
        "Subject column should be present in loaded data"
    )
    unique_subjects = trials_df["Subject"].unique().to_list()
    assert "Y" in unique_subjects or "U" in unique_subjects, (
        f"Expected subjects like 'Y' or 'U', got {unique_subjects}"
    )
    assert "All" not in unique_subjects, "Subject should not be default 'All' value"
