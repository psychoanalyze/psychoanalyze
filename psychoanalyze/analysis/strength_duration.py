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

"""Strength-duration analysis.

Contains functions assessing the relationship
between the amplitude and the time course of the stimulus.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from psychoanalyze.plot import labels, template


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


def plot(
    blocks: pd.DataFrame,
    dim: str,
    x_data: list[float],
    y_data: list[float],
) -> go.Figure:
    """Plot strength-duration curve given detection data."""

    def _get_labels_given_dim(
        labels: dict[str, dict[str, str]],
        dim: str,
    ) -> dict[str, str]:
        """Get appropriate axis labels for different choices of modulated dimension."""
        return {"x": labels[dim]["x"], "y": labels[dim]["y"]}

    labels_given_dim = _get_labels_given_dim(labels=labels, dim=dim)
    x = labels_given_dim["x"]
    y = labels_given_dim["y"]
    if blocks is not None:
        sd_df = blocks[blocks["Dimension"] == dim]
    else:
        sd_df = pd.DataFrame({x: x_data, y: y_data})
    return px.scatter(
        sd_df,
        x=x,
        y=y,
        template=template,
    )
