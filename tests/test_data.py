
"""Test general-purpose data operations."""

import polars as pl
import pytest
from hypothesis import assume, given
from hypothesis.strategies import floats

from psychoanalyze import data
from psychoanalyze.data import logistic


@pytest.fixture
def subjects() -> list[str]:
    """List of subject names."""
    return ["A", "B"]


def test_params():
    x = []
    fits = pl.DataFrame({"5%": [], "50%": [], "95%": []}).cast(
        {"5%": pl.Float64, "50%": pl.Float64, "95%": pl.Float64},
    )
    reshaped = data.blocks.reshape_fit_results(fits=fits, x=x, y="p")
    assert set(reshaped.columns) <= {"err+", "err-", "p", "x"}


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
