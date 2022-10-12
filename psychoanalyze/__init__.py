import pandas as pd
import numpy as np
from scipy.special import expit  # type: ignore
from psychoanalyze import (
    schemas,
    sessions,
    blocks,
    points,
    plot,
    data,
    trials,
    weber,
    detection,
    amp,
)

pd.options.plotting.backend = "plotly"

__version__ = "0.1.0"

__all__ = [
    "schemas",
    "plot",
    "data",
    "trial",
    "blocks",
    "sessions",
    "weber",
    "detection",
    "amp",
    "points",
    "trials",
    "blocks",
]

# def curve(trials: pd.DataFrame) -> pd.Series:
#     """Arrange *method of constant stimuli* performance curves using trial data"""
#     df = trials.groupby("x").mean().rename(columns={"Result": "Hit Rate"})
#     return df


def weber_coefficient(curves: pd.DataFrame) -> float:
    """Calculate weber coefficient for a set of psychometric curves"""
    return 1


def psi() -> pd.Series:
    """Basic sigmoid psychometric function psi (Ψ) = expit/logistic"""
    expected_x = np.linspace(-3, 3)
    expected_y = expit(expected_x)
    return pd.Series(expected_y, index=expected_x)  # type: ignore


def fit(points):
    return {"location": 1, "width": None, "gamma": None, "lambda": None}


def strength_duration(dim=None):
    df = pd.DataFrame({"Monkey": [], "Day": []})
    if dim == "amp":
        df["Threshold Amplitude (μA)"] = []
        df["Fixed Pulse Width (μs)"] = []
    elif dim == "pw":
        df["Fixed Amplitude (μA)"] = []
        df["Threshold Pulse Width (μs)"] = []
    return df
