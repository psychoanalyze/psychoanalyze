"""Main Dash app file."""

import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback
from scipy.special import expit

from dashboard.layout import layout
from psychoanalyze import plot
from psychoanalyze.data import points

app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.BOOTSTRAP])

app.layout = layout

server = app.server


@callback(
    Output("plot", "figure"),
    Input("n-trials-per-level", "value"),
    Input("n-levels", "value"),
)
def update_data(n_trials_per_level: int, n_levels: int) -> go.Figure:
    """Update generated data according to user parameter inputs."""
    x = list(np.linspace(-4, 4, n_levels))
    _points = points.generate(
        x=x,
        n=[n_trials_per_level] * n_levels,
        p=expit(x),
    )
    return plot.psi(_points)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)  # noqa: S104
