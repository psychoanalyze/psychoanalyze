
"""Psychometric function parameter conversions."""
def intercept_to_location(intercept: float, scale: float) -> float:
    """Convert intercept to location."""
    return -intercept * scale
def location_to_intercept(location: float, scale: float) -> float:
    """Convert location to intercept."""
    return -location / scale
def slope_to_scale(slope: float) -> float:
    """Convert slope to scale."""
    return 1 / slope
def scale_to_slope(scale: float) -> float:
    """Convert scale to slope."""
    return 1 / scale
