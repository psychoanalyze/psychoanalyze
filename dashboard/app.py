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

import dash_bootstrap_components as dbc
import duckdb
import numpy as np
import pandas as pd
import plotly.express as px
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
from scipy.stats import logistic

from dashboard.layout import layout
from psychoanalyze.data import blocks as pa_blocks

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
    Output("x-min", "value"),
    Output("x-max", "value"),
    Output("points-table", "data"),
    Input("x_0", "value"),
    Input("k", "value"),
    Input("n-levels", "value"),
)
def update_x_range(
    x_0: float,
    k: float,
    n_levels: int,
) -> tuple[str, str, list[dict[str, float]]]:
    """Update x range based on threshold and slope."""
    min_, max_ = logistic.ppf([0.01, 0.99], loc=x_0, scale=k)
    return (
        f"{min_:0.2f}",
        f"{max_:0.2f}",
        [{"Intensity": x} for x in np.linspace(min_, max_, n_levels)],
    )


@callback(
    Output("plot", "figure"),
    Input("logit", "value"),
    Input("k", "value"),
    Input("x_0", "value"),
)
def update_fig_model(
    form: str,
    k: float,
    x_0: float,
) -> tuple[go.Figure, dash_table.DataTable]:
    """Update plot and tables based on data store and selected view."""
    params = {"k": k, "x_0": x_0}
    model = pa_blocks.logistic(params)
    y = model["logit(Hit Rate)"] if form == "log" else model["Hit Rate"]
    return px.line(y, y=y.name, template="plotly_white")


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
    State("points-table", "data"),
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


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
