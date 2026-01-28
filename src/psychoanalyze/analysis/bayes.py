
"""Bayesian analysis of psychophysical data."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
def plot(simulated: pd.DataFrame, estimated: pd.Series) -> go.Figure:
    """Plot Psychometric curve to emphasize Bayesian posteriors."""
    combined = pd.concat(
        [simulated.reset_index(), estimated.reset_index()],
        keys=["Simulated", "Estimated"],
        names=["Type"],
    )
    return px.scatter(
        combined.reset_index(),
        x="x",
        y="Hit Rate",
        color="Type",
        template="plotly_white",
    )
