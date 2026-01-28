
"""Sigmoid functions used in the psychometric function."""
from typing import Any

import numpy as np
def weibull(
    x: np.ndarray[Any, np.dtype[np.floating[Any]]],
    alpha: float,
    beta: float,
) -> float:
    """Calculate psi using Weibull function."""
    return 1 - np.exp(-((x / alpha) ** beta))
def gumbel(x: np.ndarray[Any, np.dtype[Any]], alpha: float, beta: float) -> float:
    """Calculate psi using gumbel function."""
    return 1 - np.exp(-(10 ** (beta * (x - alpha))))
def quick(x: float, alpha: float, beta: float) -> float:
    """Calculate psi using quick function."""
    return 1 - 2 ** (-((x / alpha) ** beta))
def log_quick(x: float, alpha: float, beta: float) -> float:
    """Calculate psi using log_quick function."""
    return 1 - 2 ** (-(10 ** (beta * (x - alpha))))
