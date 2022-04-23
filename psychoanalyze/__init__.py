import pandas as pd
import numpy as np
from scipy.special import expit
import psychoanalyze as pa

__version__ = "0.1.0"


def fake(n=100) -> pd.DataFrame:
    """Generate a small set of trial data"""
    return pd.DataFrame(
        {"Result": [np.random.binomial(1, 0.5) for _ in range(n)], "x": [1] * n}
    )


def curve(trials: pd.DataFrame) -> pd.Series:
    """Arrange *method of constant stimuli* performance curves using trial data"""
    return trials.groupby("x").mean()


def weber_coefficient(curves: pd.DataFrame) -> float:
    """Calculate weber coefficient for a set of psychometric curves"""
    return 1


def psi() -> pd.Series:
    """Basic sigmoid psychometric function psi (Ψ) = expit/logistic"""
    expected_x = np.linspace(-3, 3)
    expected_y = expit(expected_x)
    return pd.Series(expected_y, index=expected_x)
