
"""Utilities for working with logistic distributions."""

from scipy.special import logit
def to_intercept(location: float, scale: float) -> float:
    """Calculate the intercept of a logistic distribution given location and scale.

    Params:
        location: The location parameter of a logistic distribution.
        scale: The scale parameter of a logistic distribution.

    Returns:
        The intercept of the logistic distribution.

    """
    return -location / scale
def to_slope(scale: float) -> float:
    """Calculate the slope of a logistic distribution given scale.

    Params:
        scale: The scale parameter of a logistic distribution.

    Returns:
        The slope of the logistic distribution at the inflection point.

    """
    return 1 / scale
def min_x(intercept: float, slope: float) -> float:
    """Calculate the minimum x value to be sampled.

    Params:
        intercept: The intercept of the logistic distribution.
        slope: The slope of the logistic distribution at the inflection point.

    Returns:
        The minimum x value of the logistic distribution.

    """
    return (logit(0.01) - intercept) / slope
