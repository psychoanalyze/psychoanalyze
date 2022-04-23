import pandas as pd
import numpy as np
import random
from scipy.special import expit

__version__ = "0.1.0"


def fake(n: int, x: set) -> pd.DataFrame:
    """Generate a small set of trial data"""
    return pd.DataFrame(
        {
            "Result": [np.random.binomial(1, 0.5) for _ in range(n)],
            "x": random.choices(list(x), k=n),
        }
    )


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
