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
    reshaped = data.reshape_fit_results(fits=fits, x=x, y="p")
    dt.validate(reshaped.index, x)
    assert set(reshaped.columns) <= {"err+", "err-", "p"}


def test_generate() -> None:
    """Test generation of complete data set."""
    assert set(data.generate().columns) == {"Intensity", "Hit Rate"}
