from psychoanalyze import data
import pytest
import pandas as pd
import datatest as dt


@pytest.fixture
def subjects():
    return ["A", "B"]


@pytest.fixture
def X():
    return list(range(8))


def test_nonstandard_logistic_mean():
    s = data.logistic(threshold=1)
    assert min(s) > 0
    assert max(s) < 1


def test_nonstandard_logistic_slope():
    s_control = data.logistic()
    s = data.logistic(scale=2)
    assert max(s) < max(s_control)


def test_params():
    x = pd.Index([])
    fit = pd.DataFrame({"5%": [], "50%": [], "95%": []})
    df = data.reshape_fit_results(fit=fit, x=x, y="p")
    dt.validate(df.index, x)
    assert set(df.columns) <= {"err+", "err-", "p"}
