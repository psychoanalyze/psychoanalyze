
"""Empirical Distribution Functions (eCDF)."""
import plotly.express as px
import plotly.graph_objects as go
import polars as pl

from psychoanalyze.data import subject as subject_utils


def plot(blocks: pl.DataFrame, param: str) -> go.Figure:
    """Plot empirical cumulative distrubtion function (eCDF) of fitted params."""
    df = blocks.to_pandas()
    subject_col = subject_utils.resolve_subject_column(blocks)
    return px.ecdf(
        df,
        x=param,
        color=df.get(subject_col) if subject_col else None,
    ).update_layout(xaxis_title=param)
