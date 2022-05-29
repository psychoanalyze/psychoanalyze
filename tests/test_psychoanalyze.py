from psychoanalyze import __version__
import psychoanalyze as pa
import pandas as pd
import datatest as dt
import numpy as np
import pytest
from scipy.special import expit


@pytest.fixture
def trials():
    return pa.trials.fake(100, set(range(8)))


def test_version():
    assert __version__ == "0.1.0"


def test_faker(trials):
    assert all(trials["Result"].isin({0, 1}))


def test_faker_size(trials):
    assert len(trials) == 100


def test_faker_x_values(trials):
    dt.validate(trials["x"], set(range(8)))


def test_curve():
    df = pd.DataFrame({"Result": [0, 1], "x": [1, 1]}, index=[1, 2])
    dt.validate(pa.curve(df), pd.Series([0.5], index=pd.Index([1], name="x")))


def test_weber():
    curves = pd.DataFrame(
        {"Difference Threshold": [0, 1], "Base Stimulus Intensity": [0, 1]},
        index=pd.Index([1, 2], name="Trial"),
    )
    assert pa.weber_coefficient(curves) == 1


def test_psi():
    expected_x = np.linspace(-3, 3)
    expected_y = expit(expected_x)
    dt.validate(pa.psi(), pd.Series(expected_y, index=expected_x))


def test_curve_fit():
    points = pd.DataFrame({"Hit Rate": [0, 2], "x": [0, 2]})
    fit = pa.fit(points)
    assert fit["location"] == 1


def test_curve_fit_fields():
    points = pd.Series([0, 2], name="Hit Rate", index=pd.Index([0, 2], name="x"))
    fit = pa.fit(points)
    assert fit.keys() == {"location", "width", "gamma", "lambda"}


@pytest.mark.parametrize("n", [2, 3])
def test_generate_data_n_subjects(n):
    subjects = pa.data.subjects(n_subjects=n)
    data = pa.data.generate(label="Threshold", name="Day", n=10, subjects=subjects)
    assert set(data.index.names) == {"Subject", "Day"}
    assert data.index.get_level_values("Subject").nunique() == n
    assert set(data.columns) == {"Threshold"}


def test_data_index():
    index = pa.data.generate(subjects=["A", "B"], n=10, name="Day", label="Threshold")
    assert len(index) == 20


def test_generate_data_n_trials():
    n_sessions = 10
    subjects = ["A", "B"]
    days = list(range(n_sessions))
    index = pd.MultiIndex.from_product([subjects, days], names=["Subject", "Day"])
    data = pa.data.generate(subjects=["A", "B"], n=10, name="Day", label="Threshold")
    assert set(data.columns) == {"Threshold"}


def test_generate_curve_data():
    data = pa.data.generate(subjects=["A", "B"], n=8, name="x", label="Hit Rate")
    assert data.index.get_level_values("Subject").nunique() == 2
    assert set(data.index.names) == {"Subject", "x"}
    assert set(data.columns) == {"Hit Rate"}
