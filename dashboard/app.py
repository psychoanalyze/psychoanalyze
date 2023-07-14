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

import base64
from pathlib import Path
from typing import Any

import dash_bootstrap_components as dbc
import duckdb
import pandas as pd
import plotly.graph_objects as go
from dash import (
    ALL,
    Dash,
    Input,
    Output,
    State,
    callback,
    callback_context,
    dash_table,
    dcc,
)

from dashboard.layout import layout
from psychoanalyze.data import blocks as pa_blocks
from psychoanalyze.data import points as pa_points
from psychoanalyze.data import trials as pa_trials

app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.SUPERHERO,
        dbc.icons.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Comfortaa:wght@500&family=Glegoo:wght@700&display=swap",
    ],
)
app.title = "PsychoAnalyze"
app.layout = layout
server = app.server


@callback(
    Output("points-store", "data"),
    Output("blocks-table", "data"),
    Input({"type": "experiment-param", "name": ALL}, "value"),
    State({"type": "experiment-param", "name": ALL}, "id"),
    Input({"type": "param", "id": ALL}, "value"),
    Input({"type": "x", "name": ALL}, "value"),
)
def update_data(
    experiment_param_values: list[int],
    dash_ids: list[dict[str, str]],
    params: list[float],
    x_range: list[float],
) -> tuple[list[Any], list[dict[str, float]]]:
    """Update generated data according to user parameter inputs."""
    experiment_params = {
        dash_id["name"]: experiment_param_values[i]
        for i, dash_id in enumerate(dash_ids)
    }
    param_names = ["Threshold", "Slope", "Guess Rate", "Lapse Rate"]
    _params = dict(zip(param_names, params, strict=True))
    x = pa_points.generate_index(experiment_params["n-levels"], x_range)
    trials = [
        pa_trials.generate(
            experiment_params["n-trials"],
            options=x,
            params=_params,
        )
        for _ in range(experiment_params["n-blocks"])
    ]
    fits = [pa_trials.fit(trial_block) for trial_block in trials]
    fit_params = [
        fit
        | {
            "Guess Rate": 0.0,
            "Lapse Rate": 0.0,
        }
        for fit in fits
    ]
    points = [
        pa_points.from_trials(trial_block).reset_index() for trial_block in trials
    ]
    all_points = [points_block.to_dict("records") for points_block in points]
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
        pa_points.plot_logistic(model, y, name="model", color="#636EFA"),
    ).add_trace(
        pa_points.plot_logistic(fit, y, name="predicted", color="#EF553B"),
    ), points_df.to_dict(
        "records",
    )


@callback(
    Output("img-download", "data"),
    Input({"type": "img-export", "name": ALL}, "n_clicks"),
    State("plot", "figure"),
    prevent_initial_call=True,
)
def export_image(
    export_clicked: int,  # noqa: ARG001
    fig: go.Figure,
) -> dict[str, str | bool | bytes]:
    """Export image."""
    format_suffix = callback_context.triggered_id["name"]
    return {
        "base64": True,
        "content": base64.b64encode(
            go.Figure(fig)
            .update_layout(showlegend=False)
            .to_image(format=format_suffix, width=500, height=500),
        ).decode("utf-8"),
        "filename": f"fig.{format_suffix}",
    }


@callback(
    Output("data-download", "data"),
    Input({"type": "data-export", "name": ALL}, "n_clicks"),
    State("table", "data"),
    prevent_initial_call=True,
)
def export_data(
    export_clicked: int,  # noqa: ARG001
    data: go.Figure,
) -> dict[str, str | bool | bytes]:
    """Export image."""
    format_suffix = callback_context.triggered_id["name"]
    _data = pd.DataFrame.from_records(data)
    if format_suffix == "csv":
        download = dcc.send_data_frame(_data.to_csv, "data.csv")
    elif format_suffix == "json":
        download = dcc.send_data_frame(_data.to_json, "data.json")
    elif format_suffix == "parquet":
        download = dcc.send_data_frame(_data.to_parquet, "data.parquet")
    elif format_suffix == "duckdb":
        connection = duckdb.connect("psychoanalyze.duckdb")
        connection.sql("CREATE TABLE points AS SELECT * FROM _data")
        connection.close()
        with Path("psychoanalyze.duckdb").open("rb") as f:
            download = {
                "base64": True,
                "content": base64.b64encode(f.read()).decode("utf-8"),
                "filename": f"psychoanalyze.{format_suffix}",
            }

    return download


@callback(
    Output({"type": "x", "name": ALL}, "disabled"),
    Input("fix-range", "value"),
    prevent_initial_call=True,
)
def disable_range(fix_range: list[str]) -> tuple[bool, bool]:
    """Disable range inputs if range is fixed."""
    return "fix-range" in fix_range, "fix-range" in fix_range


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
