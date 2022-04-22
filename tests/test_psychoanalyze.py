from psychoanalyze import __version__
import psychoanalyze as pa
import pandas as pd
import datatest as dt
import pytest
import numpy as np
from scipy.special import expit


@pytest.fixture
def trials() -> pd.DataFrame:
    return pd.DataFrame(
        {"Result": [0, 1], "x": [1, 1]}, index=pd.Index([1, 2], name="Trial")
    )


def test_version():
    assert __version__ == "0.1.0"


def test_faker(trials: pd.DataFrame):
    assert pa.fake().equals(trials)


def test_curve(trials: pd.DataFrame):
    df = pd.DataFrame(trials)
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
