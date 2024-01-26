# Copyright 2023 Tyler Schlichenmeyer

# This file is part of PsychoAnalyze.
# PsychoAnalyze is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# PsychoAnalyze is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# PsychoAnalyze. If not, see <https://www.gnu.org/licenses/>.

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
