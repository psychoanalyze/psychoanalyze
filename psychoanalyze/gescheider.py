"""Exercises from Psychophysics: The Fundamentals by George Gescheider."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def p3_1(data: pd.Series) -> go.Figure:
    """Chapter 3, Problem 1."""
    data.index.name = "φ"
    return px.line(data.rename("P"), y="P")
