
"""Empirical Distribution Functions (eCDF)."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
def plot(blocks: pd.DataFrame, param: str) -> go.Figure:
    """Plot empirical cumulative distrubtion function (eCDF) of fitted params."""
    return px.ecdf(
        blocks.reset_index(),
        x=param,
        color=blocks.get("Monkey"),
    ).update_layout(xaxis_title=param)
