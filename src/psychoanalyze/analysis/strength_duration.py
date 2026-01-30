
"""Strength-duration analysis.

Contains functions assessing the relationship
between the amplitude and the time course of the stimulus.
"""
import plotly.express as px
import plotly.graph_objects as go
import polars as pl

from psychoanalyze.plot import labels, template


def from_blocks(blocks: pl.DataFrame, dim: str) -> pl.DataFrame:
    """Calculate strength-duration measures from block data."""
    if dim == "Amp":
        ylabel = "Threshold Amplitude (μA)"
        xlabel = "Fixed Pulse Width (μs)"
    elif dim == "Width":
        ylabel = "Fixed Amplitude (μA)"
        xlabel = "Threshold Pulse Width (μs)"

    blocks = blocks.with_columns(
        pl.col("Threshold").alias(ylabel),
        pl.col("Fixed Magnitude").alias(xlabel),
    )
    return blocks.drop(["Threshold", "Fixed Magnitude"])


def plot(
    blocks: pl.DataFrame | None,
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
        sd_df = blocks.filter(pl.col("Dimension") == dim).to_pandas()
    else:
        sd_df = {x: x_data, y: y_data}
    return px.scatter(
        sd_df,
        x=x,
        y=y,
        template=template,
    )
