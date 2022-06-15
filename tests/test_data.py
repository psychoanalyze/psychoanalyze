import psychoanalyze as pa
import pytest
import pandas as pd
import datatest as dt
from cmdstanpy import CmdStanModel


@pytest.fixture
def subjects():
    return ["A", "B"]


@pytest.fixture
def X():
    return list(range(8))


def test_nonstandard_logistic_mean():
    s = pa.data.logistic(threshold=1)
    assert min(s) > 0
    assert max(s) < 1


def test_nonstandard_logistic_slope():
    s_control = pa.data.logistic()
    s = pa.data.logistic(scale=2)
    assert max(s) < max(s_control)


def test_fit_curve(mocker):
    # df = pa.data.generate(["A"], 1, "Hit Rate", 100, list(range(-4, 5))).reset_index()
    mocker.patch.object(CmdStanModel, "sample")
    df = pd.DataFrame({"x": [], "n": [], "Hits": []})
    pa.data.fit_curve(df)


def test_mu_two_groups():
    data = pd.DataFrame(
        {
            "x": [1, 2],
            "n": [10, 10],
            "Hits": [1, 9],
            "Subject": ["A", "A"],
            "Day": [1, 2],
        }
    )
    output = data.groupby(["Subject", "Day"]).apply(pa.data.mu)
    assert len(output) == 2
    assert {"5%", "50%", "95%"} <= set(output.columns)


def test_params(mocker):
    x = pd.Index([])
    fit = mocker.patch("psychoanalyze.data.fit_curve", return_value=pd.DataFrame())
    df = pa.data.params(fit=fit, x=x, y="p")
    dt.validate(df.index, x)
    assert set(df.columns) <= {"50%", "95%", "5%", "p"}


def test_construct_index(mocker):
    mocker.patch("psychoanalyze.data.params", return_value=pd.DataFrame({"x": []}))
    days = [1, 2, 3]
    x = [1, 2, 3]
    index = pa.data.construct_index(subjects=None, days=days, x=x)
    assert index.names == ["Day", "x"]
    assert len(index) == len(x) * len(days)
