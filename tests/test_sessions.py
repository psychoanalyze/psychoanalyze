
"""Tests for psychoanalyze.sessions module."""

from pathlib import Path
from typing import Any

import polars as pl
import pytest

from psychoanalyze.data import sessions


@pytest.fixture
def subjects() -> pl.DataFrame:
    """Subjects for session-level data."""
    return pl.DataFrame({"Subject": ["U"], "Surgery Date": ["2020-01-01"]})


def test_generate_sessions() -> None:
    """Test appropriate number of sessions are generated."""
    assert sessions.generate(3) == [0, 1, 2]


def test_from_trials_csv(tmp_path: Path) -> None:
    """Test loading trials from csv."""
    csv_dir = tmp_path / "data"
    csv_dir.mkdir()
    csv_path = csv_dir / "trials.csv"
    data: dict[str, list[Any]] = {field: [] for field in ["Subject", "Date"]}
    trials = pl.DataFrame(data)
    trials.write_csv(csv_path)

    _sessions = sessions.from_trials_csv(csv_path)
    assert set(_sessions.columns) == {"Subject", "Date"}


def test_day_marks_from_monkey_two_sessions(subjects: pl.DataFrame) -> None:
    """Tests calculations of days from dates for multiple subjects."""
    _sessions = pl.DataFrame(
        {"Subject": ["U", "U"], "Date": ["2020-01-02", "2020-01-03"]},
    )
    assert sessions.day_marks(subjects, _sessions, "U") == {
        1: "2020-01-02",
        2: "2020-01-03",
    }


def test_day_marks_from_monkey_one_session(subjects: pl.DataFrame) -> None:
    """Tests calculations of days from dates for single subject."""
    _sessions = pl.DataFrame({"Subject": ["U"], "Date": ["2020-01-02"]})

    assert sessions.day_marks(subjects, _sessions, "U") == {1: "2020-01-02"}
