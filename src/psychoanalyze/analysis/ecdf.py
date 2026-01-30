
"""Empirical Distribution Functions (eCDF)."""
import plotly.express as px
import plotly.graph_objects as go
import polars as pl


def plot(blocks: pl.DataFrame, param: str) -> go.Figure:
    """Plot empirical cumulative distrubtion function (eCDF) of fitted params."""
    df = blocks.to_pandas()
    return px.ecdf(
        df,
        x=param,
        color=df.get("Monkey"),
    ).update_layout(xaxis_title=param)
