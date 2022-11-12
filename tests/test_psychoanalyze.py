import pandas as pd
import datatest as dt  # type: ignore
import numpy as np
from scipy.special import expit  # type: ignore

import psychoanalyze as pa


def test_version():
    assert pa.__version__ == "0.1.0"


def test_weber():
    curves = pd.DataFrame(
        {"Difference Threshold": [0, 1], "Base Stimulus Intensity": [0, 1]},
        index=pd.Index([1, 2], name="Trial"),
    )
    assert pa.weber_coefficient(curves) == 1


def test_psi():
    x = np.linspace(-3, 3)
    y = expit(x)
    dt.validate(pa.psi(), pd.Series(y, index=x))


def test_psi_nuisance_params():
    s = pa.psi(lambda_=0.1, gamma=0.1)
    assert all(s.values < 0.9) & all(s.values > 0.1)


def test_psi_xrange():
    s = pa.psi(x_range=(-5, 5))
    assert s.index.values.min() == -5
    assert s.index.values.max() == 5


def test_curve_fit():
    points = pd.DataFrame({"Hit Rate": [0, 2], "x": [0, 2]})
    fit = pa.fit(points)
    assert fit["location"] == 1


def test_curve_fit_fields():
    points = pd.Series([0, 2], name="Hit Rate", index=pd.Index([0, 2], name="x"))
    fit = pa.fit(points)
    assert fit.keys() == {"location", "width", "gamma", "lambda"}
