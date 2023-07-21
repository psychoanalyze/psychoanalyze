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
