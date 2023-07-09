"""Strength-duration analysis.

Contains functions assessing the relationship
between the amplitude and the time course of the stimulus.

---
Copyright 2023 Tyler Schlichenmeyer

This file is part of PsychoAnalyze.
PsychoAnalyze is free software: you can redistribute it and/or modify it under the terms
of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

PsychoAnalyze is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Foobar.
If not, see <https://www.gnu.org/licenses/>.

"""
import pandas as pd


def from_blocks(blocks: pd.DataFrame, dim: str) -> pd.DataFrame:
    """Calculate strength-duration measures from block data."""
    if dim == "Amp":
        ylabel = "Threshold Amplitude (μA)"
        xlabel = "Fixed Pulse Width (μs)"
    elif dim == "Width":
        ylabel = "Fixed Amplitude (μA)"
        xlabel = "Threshold Pulse Width (μs)"

    blocks[ylabel] = blocks["Threshold"]
    blocks[xlabel] = blocks["Fixed Magnitude"]
    return blocks.drop(columns=["Threshold", "Fixed Magnitude"])
