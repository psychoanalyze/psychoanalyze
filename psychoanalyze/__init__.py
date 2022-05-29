import pandas as pd
import numpy as np
import plotly.express as px
from plotly import graph_objects as go
from scipy.special import expit
from psychoanalyze import trials, plot, data

pd.options.plotting.backend = "plotly"

__version__ = "0.1.0"


def curve(trials: pd.DataFrame) -> pd.Series:
    """Arrange *method of constant stimuli* performance curves using trial data"""
    return trials.groupby("x").mean().rename(columns={"Result": "Hit Rate"})


def weber_coefficient(curves: pd.DataFrame) -> float:
    """Calculate weber coefficient for a set of psychometric curves"""
    return 1


def psi() -> pd.Series:
    """Basic sigmoid psychometric function psi (Ψ) = expit/logistic"""
    expected_x = np.linspace(-3, 3)
    expected_y = expit(expected_x)
    return pd.Series(expected_y, index=expected_x)


def fit(points):
    return {"location": 1, "width": None, "gamma": None, "lambda": None}
