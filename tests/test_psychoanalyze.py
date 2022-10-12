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


def test_strength_duration_amp():
    s_d = pa.strength_duration(fixed="pw")
    assert set(s_d.columns) <= {
        "Monkey",
        "Day",
        "Threshold Amplitude (μA)",
        "Fixed Pulse Width (μs)",
    }


def test_strength_duration_pw():
    s_d = pa.strength_duration(fixed="amp")
    assert set(s_d.columns) <= {
        "Monkey",
        "Day",
        "Fixed Amplitude (μA)",
        "Threshold Pulse Width (μs)",
    }
