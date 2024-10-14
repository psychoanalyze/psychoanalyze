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

"""Tests for psychoanalyze.points module."""

from typing import Any

import pandas as pd
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
    _trials = pd.DataFrame(data)
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
