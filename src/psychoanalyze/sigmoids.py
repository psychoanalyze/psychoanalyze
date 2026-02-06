import numpy as np


def weibull(
    x,
    alpha: float,
    beta: float
) -> float:
    return 1 - np.exp(-((x / alpha) ** beta))

def gumbel(x, alpha: float, beta: float) -> float:
    return 1 - np.exp(-(10 ** (beta * (x - alpha))))

def quick(x: float, alpha: float, beta: float) -> float:
    return 1 - 2 ** (-((x / alpha) ** beta))

def log_quick(x: float, alpha: float, beta: float) -> float:
    return 1 - 2 ** (-(10 ** (beta * (x - alpha))))
