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
import random
from collections.abc import Hashable
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import (
    ALL,
    MATCH,
    Dash,
    Input,
    Output,
    State,
    callback,
    callback_context,
    dash_table,
    dcc,
)
from dash_bootstrap_components import icons, themes
from scipy.stats import logistic

from dashboard.layout import layout
from psychoanalyze.data import blocks as pa_blocks
from psychoanalyze.data import points as pa_points

app = Dash(
    __name__,
    external_stylesheets=[
        themes.SUPERHERO,
        icons.BOOTSTRAP,
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
    Input({"type": "param", "name": ALL}, "value"),
    Input("n-levels", "value"),
    Input("n-trials", "value"),
)
def update_x_range(
    param: list[float],
    n_levels: int,
    n_trials: int,
) -> tuple[str, str, list[dict[Hashable, Any]]]:
    """Update x range based on threshold and slope."""
    params = dict(zip(["x_0", "k", "gamma", "lambda"], param, strict=True))
    min_, max_ = logistic.ppf([0.01, 0.99], loc=params["x_0"], scale=params["k"])
    ix = pd.Index(np.linspace(min_, max_, n_levels), name="Intensity")
    p = pa_points.psi(ix, params)
    execution_plan = pd.Series(
        [random.choice(ix) for _ in range(n_trials)],
        name="Intensity",
    )
    counts = execution_plan.value_counts().rename("n trials").sort_index()
    hits = pd.Series(
        np.random.default_rng().binomial(counts, p),
        index=counts.index,
        name="Hits",
    )
    hit_rate = pd.Series(hits / counts, name="Hit Rate")
    points = pd.concat([counts, p, hits, hit_rate], axis=1).reset_index()
    return (
        f"{min_:0.2f}",
        f"{max_:0.2f}",
        points.to_dict("records"),
    )


@callback(
    Output("plot", "figure"),
    Input("logit", "value"),
    Input({"type": "param", "name": ALL}, "value"),
    Input("points-table", "data"),
)
def update_fig_model(
    form: str,
    param: list[float],
    data: list[dict[Hashable, Any]],
) -> tuple[go.Figure, dash_table.DataTable]:
    """Update plot and tables based on data store and selected view."""
    params = dict(zip(["x_0", "k", "gamma", "lambda"], param, strict=True))
    model = params["gamma"] + (
        1 - params["gamma"] - params["lambda"]
    ) * pa_blocks.logistic(params)
    y = model["logit(Hit Rate)"] if form == "log" else model["Hit Rate"]
    if data is None:
        fig = px.line(y, y=y.name, template="plotly_white")
    else:
        fig = px.scatter(
            pd.DataFrame.from_records(data),
            x="Intensity",
            y="Hit Rate",
            size="n trials",
            template="plotly_white",
        ).add_trace(
            go.Scatter(
                x=model.index,
                y=y,
                name="Model",
                mode="lines",
                line_color="#636EFA",
            ),
        )
    return fig


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


@callback(
    Output("F-eqn", "is_open"),
    Output("show-eqn", "children"),
    Input("show-eqn", "n_clicks"),
)
def toggle_eqn(n_clicks: int) -> tuple[bool, str]:
    """Toggle equation."""
    if n_clicks:
        n_clicks_is_even = n_clicks % 2 == 0
        label = "Hide Eqn ▴ " if n_clicks_is_even else "Show Eqn ▾ "
        return n_clicks_is_even, label
    return True, "Hide Eqn ▴ "


@callback(
    Output({"type": "param", "name": MATCH}, "disabled"),
    Input({"type": "free", "name": MATCH}, "value"),
)
def toggle_param(free: bool) -> bool:  # noqa: FBT001
    """Toggle parameter."""
    return not free


if __name__ == "__main__":
    app.run(debug=True)
