"""Test functions related to Weber's Law analysis."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot(
    data: pd.DataFrame,
    trendline: str = "ols",
    error_y: str | None = None,
) -> go.Figure:
    """Plot data according to Weber's Law."""
    _trendline = "ols" if trendline else None
    return px.scatter(
        data.reset_index(),
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


def aggregate(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate agg stats for Weber data."""
    return (
        data.groupby(["Monkey", "Dimension", "Reference Charge (nC)"])[
            "Difference Threshold (nC)"
        ]
        .agg(["mean", "count", "std"])
        .rename(columns={"mean": "Difference Threshold (nC)"})
    )


def load(path: Path) -> pd.DataFrame:
    """Load weber file from a csv."""
    weber = pd.read_csv(path, parse_dates=["Date"])
    weber["err+"] = (
        weber["location_CI_5"] * weber["Fixed_Param_Value"] / 1000
    ) - weber["Threshold_Charge_nC"]
    weber["err-"] = (
        weber["Threshold_Charge_nC"]
        - (weber["location_CI_95"]) * weber["Fixed_Param_Value"] / 1000
    )
    return weber
