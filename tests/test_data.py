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

"""Test general-purpose data operations."""
import datatest as dt
import pandas as pd
import pytest
from hypothesis import assume, given
from hypothesis.strategies import floats

from psychoanalyze import data
from psychoanalyze.data import logistic


@pytest.fixture()
def subjects() -> list[str]:
    """List of subject names."""
    return ["A", "B"]


def test_params():
    x = pd.Index([])
    fits = pd.DataFrame({"5%": [], "50%": [], "95%": []})
    reshaped = data.blocks.reshape_fit_results(fits=fits, x=x, y="p")
    dt.validate(reshaped.index, x)
    assert set(reshaped.columns) <= {"err+", "err-", "p"}


finite = floats(allow_nan=False, allow_infinity=False)


@given(finite, finite)
def test_to_intercept(location: float, scale: float):
    assume(scale != 0)
    intercept = logistic.to_intercept(location=location, scale=scale)
    assert intercept == -location / scale


@given(finite)
def test_to_slope(scale: float):
    assume(scale != 0)
    slope = logistic.to_slope(scale=scale)
    assert slope == 1 / scale
