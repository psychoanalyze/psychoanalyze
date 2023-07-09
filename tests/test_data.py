# Copyright 2023 Tyler Schlichenmeyer

# This file is part of PsychoAnalyze.
# PsychoAnalyze is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# PsychoAnalyze is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with Foobar.
# If not, see <https://www.gnu.org/licenses/>.

"""Test general-purpose data operations."""
import datatest as dt
import pandas as pd
import pytest

from psychoanalyze import data


@pytest.fixture()
def subjects() -> list[str]:
    """List of subject names."""
    return ["A", "B"]


def test_nonstandard_logistic_mean() -> None:
    """Tests the y bounds of a nonstandard logistic."""
    s = data.logistic(threshold=1)
    assert min(s) > 0
    assert max(s) < 1


def test_nonstandard_logistic_slope() -> None:
    """Tests slope value for nonstandard logistic parameters."""
    s_control = data.logistic()
    s = data.logistic(scale=2)
    assert max(s) < max(s_control)


def test_params() -> None:
    """Test that params are in the right format."""
    x = pd.Index([])
    fits = pd.DataFrame({"5%": [], "50%": [], "95%": []})
    reshaped = data.blocks.reshape_fit_results(fits=fits, x=x, y="p")
    dt.validate(reshaped.index, x)
    assert set(reshaped.columns) <= {"err+", "err-", "p"}
