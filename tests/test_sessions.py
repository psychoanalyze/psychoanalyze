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

"""Tests for psychoanalyze.sessions module."""
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from psychoanalyze.data import sessions


@pytest.fixture()
def subjects() -> pd.DataFrame:
    """Subjects for session-level data."""
    return pd.DataFrame({"Monkey": ["U"], "Surgery Date": ["2020-01-01"]})


def test_generate_sessions() -> None:
    """Test appropriate number of sessions are generated."""
    assert sessions.generate(3) == [0, 1, 2]


def test_from_trials_csv(tmp_path: Path) -> None:
    """Test loading trials from csv."""
    csv_dir = tmp_path / "data"
    csv_dir.mkdir()
    csv_path = csv_dir / "trials.csv"
    data: dict[str, list[Any]] = {field: [] for field in ["Monkey", "Date"]}
    trials = pd.DataFrame(data)
    trials.to_csv(csv_path)

    _sessions = sessions.from_trials_csv(csv_path)
    assert set(_sessions.columns) == {"Monkey", "Date"}


def test_day_marks_from_monkey_two_sessions(subjects: pd.DataFrame) -> None:
    """Tests calculations of days from dates for multiple subjects."""
    _sessions = pd.DataFrame(
        {"Monkey": ["U", "U"], "Date": ["2020-01-02", "2020-01-03"]},
    )
    assert sessions.day_marks(subjects, _sessions, "U") == {
        1: "2020-01-02",
        2: "2020-01-03",
    }


def test_day_marks_from_monkey_one_session(subjects: pd.DataFrame) -> None:
    """Tests calculations of days from dates for single subject."""
    _sessions = pd.DataFrame({"Monkey": ["U"], "Date": ["2020-01-02"]})

    assert sessions.day_marks(subjects, _sessions, "U") == {1: "2020-01-02"}
