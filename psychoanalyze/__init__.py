import pandas as pd
import numpy as np
from psychoanalyze import (
    schemas,
    sessions,
    points,
    plot,
    data,
    trials,
    blocks,
    weber,
    strength_duration,
    subjects,
    stimulus,
    simulate,
)
from psychoanalyze.dashboard import layout

pd.options.plotting.backend = "plotly"

__version__ = "0.4.5"

__all__ = [
    "schemas",
    "plot",
    "data",
    "trial",
    "blocks",
    "sessions",
    "weber",
    "points",
    "blocks",
    "trials",
    "strength_duration",
    "subjects",
    "stimulus",
    "simulate",
    "layout",
]

# def curve(trials: pd.DataFrame) -> pd.Series:
#     """Arrange *method of constant stimuli* performance curves using trial data"""
#     df = trials.groupby("x").mean().rename(columns={"Result": "Hit Rate"})
#     return df


def weber_coefficient(curves: pd.DataFrame) -> float:
    """Calculate weber coefficient for a set of psychometric curves"""
    return 1


def psi(threshold=0, slope=1, lambda_=0, gamma=0, x_range=(-3, 3)) -> pd.Series:
    """Basic sigmoid psychometric function psi (Ψ) = expit/logistic"""
    x = np.linspace(x_range[0], x_range[1])
    y = gamma + (1 - lambda_ - gamma) * 1 / (1 + np.exp((-slope) * (x - threshold)))
    return pd.Series(y, index=x)


def fit(data):
    return {"Fit": [1, 1, 0, 0]}
