
"""Bayesian analysis of psychophysical data."""
import plotly.express as px
import plotly.graph_objects as go
import polars as pl


def plot(simulated: pl.DataFrame, estimated: pl.DataFrame) -> go.Figure:
    """Plot Psychometric curve to emphasize Bayesian posteriors."""
    simulated_df = simulated.with_columns(pl.lit("Simulated").alias("Type"))
    estimated_df = estimated.with_columns(pl.lit("Estimated").alias("Type"))
    combined = pl.concat([simulated_df, estimated_df])
    return px.scatter(
        combined.to_pandas(),
        x="x",
        y="Hit Rate",
        color="Type",
        template="plotly_white",
    )
