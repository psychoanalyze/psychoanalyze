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
from psychoanalyze.data import blocks as pa_blocks
from psychoanalyze.data import points as pa_points

app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.BOOTSTRAP])

app.layout = layout

server = app.server


@callback(
    Output("plot", "figure"),
    Output("table", "data"),
    Input("n-trials", "value"),
    Input("n-levels", "value"),
    Input("x_0", "value"),
    Input("model-k", "value"),
    Input("guess-rate", "value"),
    Input("lapse-rate", "value"),
    Input("min-x", "value"),
    Input("max-x", "value"),
)
def update_data(  # noqa: PLR0913
    n_trials: int,
    n_levels: int,
    intercept: float,
    slope: float,
    guess_rate: float,
    lapse_rate: float,
    min_x: float,
    max_x: float,
) -> go.Figure:
    """Update generated data according to user parameter inputs."""
    x = list(np.linspace(min_x, max_x, n_levels))
    points = pa_points.generate(
        n_trials=n_trials,
        options=x,
        threshold=intercept,
        slope=slope,
        guess_rate=guess_rate,
        lapse_rate=lapse_rate,
    )
    logistic = pa_blocks.logistic(
        intercept,
        slope,
        guess_rate,
        lapse_rate,
    ).reset_index()
    return (
        pa_points.plot(points).add_trace(
            go.Scatter(
                x=logistic["Intensity"],
                y=logistic["Hit Rate"],
                mode="lines",
                name="model",
            ),
        ),
        points.reset_index().sort_values(by="Intensity").to_dict("records"),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)  # noqa: S104
