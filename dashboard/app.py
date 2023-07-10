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
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback

from dashboard.layout import layout
from psychoanalyze.data import blocks as pa_blocks
from psychoanalyze.data import points as pa_points
from psychoanalyze.data import trials as pa_trials

app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.BOOTSTRAP])

app.layout = layout

server = app.server


@callback(
    Output("plot", "figure"),
    Output("table", "data"),
    Output("x_0_fit", "children"),
    Output("k_fit", "children"),
    Input("n-trials", "value"),
    Input("n-levels", "value"),
    Input("x_0", "value"),
    Input("model-k", "value"),
    Input("guess-rate", "value"),
    Input("lapse-rate", "value"),
    Input("min-x", "value"),
    Input("max-x", "value"),
    Input("logit", "value"),
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
    form: str,
) -> go.Figure:
    """Update generated data according to user parameter inputs."""
    params = {
        "Threshold": intercept,
        "Slope": slope,
        "Guess Rate": guess_rate,
        "Lapse Rate": lapse_rate,
    }
    trials = pa_trials.generate(
        n_trials,
        options=pa_points.generate_index(n_levels, min_x, max_x),
        params=params,
    )
    fits = pa_trials.fit(trials)
    fit_params = {
        "Threshold": -fits.intercept_[0],
        "Slope": fits.coef_[0][0],
        "Guess Rate": 0.0,
        "Lapse Rate": 0.0,
    }
    points = pa_points.from_trials(trials)
    logistic = pa_blocks.logistic(params).reset_index()
    fit_logistic = pa_blocks.logistic(fit_params).reset_index()
    y = "logit(Hit Rate)" if form == "log" else "Hit Rate"
    fig = (
        pa_points.plot(points.reset_index(), y)
        .add_trace(
            pa_points.plot_logistic(logistic, y, name="model", color="blue"),
        )
        .add_trace(
            pa_points.plot_logistic(fit_logistic, y, name="predicted", color="red"),
        )
    )
    return (
        fig,
        points.reset_index().sort_values(by="Intensity").to_dict("records"),
        fits.coef_[0],
        fits.intercept_,
    )


if __name__ == "__main__":
    app.run(debug=False)
