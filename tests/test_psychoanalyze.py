from psychoanalyze import __version__
import psychoanalyze as pa
import pandas as pd
import datatest as dt
import numpy as np
from scipy.special import expit


def test_version():
    assert __version__ == "0.1.0"


def test_faker():
    assert all(pa.fake(100, set(range(8)))["Result"].isin({0, 1}))


def test_faker_size():
    assert len(pa.fake(100, set(range(8)))) == 100


def test_faker_x_values():
    dt.validate(pa.fake(100, set(range(8)))["x"], set(range(8)))


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
