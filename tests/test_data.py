import psychoanalyze as pa
import pytest
import pandas as pd
import datatest as dt  # type: ignore


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
    mocker.patch("cmdstanpy.CmdStanModel")
    df = pd.DataFrame({"Amp1": [], "n": [], "Hits": []})
    pa.points.fit(df)


def test_mu_two_groups(mocker):
    mocker.patch(
        "psychoanalyze.points.fit",
        return_value=pd.DataFrame(
            {"5%": [1], "50%": [2], "95%": [3]}, index=pd.Index(["mu"])
        ),
    )
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


def test_params():
    x = pd.Index([])
    fit = pd.DataFrame({"5%": [], "50%": [], "95%": []})
    df = pa.data.reshape_fit_results(fit=fit, x=x, y="p")
    dt.validate(df.index, x)
    assert set(df.columns) <= {"err+", "err-", "p"}


def test_construct_index(mocker):
    mocker.patch(
        "psychoanalyze.data.reshape_fit_results", return_value=pd.DataFrame({"x": []})
    )
    days = [1, 2, 3]
    x = [1, 2, 3]
    index = pa.data.construct_index(subjects=None, days=days, x=x)
    assert index.names == ["Day", "x"]
    assert len(index) == len(x) * len(days)


def test_data_load():
    data = pa.data.load()
    assert data.keys() == {"Subjects", "Sessions", "Blocks"}
