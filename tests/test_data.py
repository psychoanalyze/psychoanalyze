import psychoanalyze as pa
import pytest
import pandas as pd
import datatest as dt


@pytest.fixture
def subjects():
    return ["A", "B"]


@pytest.fixture
def X():
    return list(range(8))


def test_generate_curve(subjects, X):
    data = pa.data.generate(
        subjects=subjects, n_sessions=8, y="Hit Rate", n_trials_per_stim_level=10, X=X
    )
    assert data.index.get_level_values("Subject").nunique() == 2
    assert set(data.index.names) == {"Subject", "Day", "x"}
    assert "Hit Rate" in set(data.columns)


@pytest.mark.parametrize("subjects", [["A", "B"], ["A", "B", "C"]])
def test_generate_n_subjects(subjects, X):
    data = pa.data.generate(subjects, 10, "Threshold", n_trials_per_stim_level=10, X=X)
    assert {"Subject", "Day"} <= set(data.index.names)
    assert data.index.get_level_values("Subject").nunique() == len(subjects)
    assert "Threshold" in set(data.columns)


def test_nonstandard_logistic_mean():
    s = pa.data.logistic(threshold=1)
    assert min(s) > 0
    assert max(s) < 1


def test_nonstandard_logistic_slope():
    s_control = pa.data.logistic()
    s = pa.data.logistic(scale=2)
    assert max(s) < max(s_control)


def test_fit_curve():
    df = pa.data.generate(["A"], 1, "Hit Rate", 100, list(range(-4, 5))).reset_index()
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
