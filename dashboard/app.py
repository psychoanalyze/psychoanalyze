"""Main Dash app file.

Contains callbacks.
"""

# Copyright 2023 Tyler Schlichenmeyer

# This file is part of PsychoAnalyze.
# PsychoAnalyze is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# PsychoAnalyze is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# PsychoAnalyze. If not, see <https://www.gnu.org/licenses/>.

from typing import Any

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import ALL, Dash, Input, Output, callback, dash_table

from dashboard.layout import layout
from psychoanalyze.data import blocks as pa_blocks
from psychoanalyze.data import points as pa_points
from psychoanalyze.data import trials as pa_trials

app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.BOOTSTRAP])

app.title = "PsychoAnalyze"
app.layout = layout

server = app.server

@callback(
    Output("points-store", "data"),
    Output("blocks-table", "data"),
    Input("n-trials", "value"),
    Input("n-levels", "value"),
    Input({"type": "param", "id": ALL}, "value"),
    Input("min-x", "value"),
    Input("max-x", "value"),
)
def update_data(
    n_trials: int,
    n_levels: int,
    params: list[float],
    min_x: float,
    max_x: float,
) -> tuple[list[Any], list[dict[str, float]]]:
    """Update generated data according to user parameter inputs."""
    _params = {
        "Threshold": params[0],
        "Slope": params[1],
        "Guess Rate": params[2],
        "Lapse Rate": params[3],
    }
    x = pa_points.generate_index(n_levels, min_x, max_x)
    trials1 = pa_trials.generate(
        n_trials,
        options=x,
        params=_params,
    )
    trials2 = pa_trials.generate(
        n_trials,
        options=x,
        params=_params,
    )
    fits1 = pa_trials.fit(trials1)
    fits2 = pa_trials.fit(trials2)
    fit_params1 = fits1 | {
        "Guess Rate": 0.0,
        "Lapse Rate": 0.0,
    }
    fit_params2 = fits2 | {
        "Guess Rate": 0.0,
        "Lapse Rate": 0.0,
    }
    fit_params = [fit_params1, fit_params2]
    points1 = pa_points.from_trials(trials1).reset_index()
    points2 = pa_points.from_trials(trials2).reset_index()
    all_points = [points1.to_dict("records"), points2.to_dict("records")]
    return all_points, fit_params


@callback(
    Output("plot", "figure"),
    Output("table", "data"),
    Input("points-store", "data"),
    Input("blocks-table", "data"),
    Input("logit", "value"),
    Input("blocks-table", "derived_virtual_selected_rows"),
    Input({"type": "param", "id": ALL}, "value"),
)
def update_downstream(
    points: dict,
    blocks: dict,
    form: str,
    selected_blocks: list[int],
    params: list[float],
) -> tuple[go.Figure, dash_table.DataTable]:
    """Update plot and tables based on data store and selected view."""
    _params = {
        "Threshold": params[0],
        "Slope": params[1],
        "Guess Rate": params[2],
        "Lapse Rate": params[3],
    }
    model = pa_blocks.logistic(_params)
    fit = pa_blocks.logistic(
        blocks[selected_blocks[0]] if selected_blocks else _params,
    )
    y = "logit(Hit Rate)" if form == "log" else "Hit Rate"
    points_df = pd.DataFrame.from_records(
        points[selected_blocks[0]]
        if selected_blocks
        else [
            {
                "Intensity": None,
                "Hit Rate": None,
                "n": 0,
            },
        ],
    )
    return pa_points.plot(points_df, y).add_trace(
        pa_points.plot_logistic(model, y, name="model", color="blue"),
    ).add_trace(
        pa_points.plot_logistic(fit, y, name="predicted", color="red"),
    ), points_df.to_dict(
        "records",
    )


if __name__ == "__main__":
    app.run(debug=False)
