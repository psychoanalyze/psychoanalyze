
"""Test functions related to Weber's Law analysis.

Contains functions assessing how discriminability of two stimuli
relates to the baseline intensities of the stimuli according to Weber's Law.
"""
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import polars as pl


def plot(
    data: pl.DataFrame,
    trendline: str = "ols",
    error_y: str | None = None,
) -> go.Figure:
    """Plot data according to Weber's Law."""
    _trendline = "ols" if trendline else None
    return px.scatter(
        data.to_pandas(),
        x="Reference Charge (nC)",
        y="Difference Threshold (nC)",
        error_y="err+" if error_y == "error bars" else None,
        error_y_minus="err-" if error_y == "error bars" else None,
        color="Monkey",
        symbol="Dimension",
        trendline=_trendline,
        template="plotly_white",
        hover_data=["Date"],
    )


def aggregate(data: pl.DataFrame) -> pl.DataFrame:
    """Calculate agg stats for Weber data."""
    return data.group_by(["Monkey", "Dimension", "Reference Charge (nC)"]).agg(
        pl.mean("Difference Threshold (nC)").alias("Difference Threshold (nC)"),
        pl.len().alias("count"),
        pl.std("Difference Threshold (nC)").alias("std"),
    )


def load(path: Path) -> pl.DataFrame:
    """Load weber file from a csv."""
    weber = pl.read_csv(path).with_columns(pl.col("Date").str.to_datetime())
    weber = weber.with_columns(
        (
            pl.col("location_CI_5") * pl.col("Fixed_Param_Value") / 1000
            - pl.col("Threshold_Charge_nC")
        ).alias("err+"),
        (
            pl.col("Threshold_Charge_nC")
            - pl.col("location_CI_95") * pl.col("Fixed_Param_Value") / 1000
        ).alias("err-"),
    )
    return weber
