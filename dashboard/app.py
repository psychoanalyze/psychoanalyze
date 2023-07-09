"""Main Dash app file.

---
Copyright 2023 Tyler Schlichenmeyer

This file is part of PsychoAnalyze.
PsychoAnalyze is free software: you can redistribute it and/or modify it under the terms
of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

PsychoAnalyze is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Foobar.
If not, see <https://www.gnu.org/licenses/>.
"""

import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback

from dashboard.layout import layout
from psychoanalyze.data import points

app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.BOOTSTRAP])

app.layout = layout

server = app.server


@callback(
    Output("plot", "figure"),
    Input("n-trials-per-level", "value"),
    Input("n-levels", "value"),
    Input("x_0", "value"),
    Input("model-k", "value"),
)
def update_data(
    n_trials_per_level: int,
    n_levels: int,
    intercept: float,
    slope: float,
) -> go.Figure:
    """Update generated data according to user parameter inputs."""
    x = list(np.linspace(-4, 4, n_levels))
    _points = points.generate_series(
        x=x,
        n=[n_trials_per_level] * n_levels,
        threshold=intercept,
        scale=slope,
    )
    return points.plot(_points.to_frame())


if __name__ == "__main__":
    app.run(debug=True)
