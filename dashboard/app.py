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
import io
import random
from collections.abc import Hashable
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
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
from scipy.special import logit
from scipy.stats import logistic
from statsmodels.discrete.discrete_model import Logit

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
    Output("points-store", "data", allow_duplicate=True),
    Output("blocks-table", "data"),
    Input({"type": "param", "name": ALL}, "value"),
    Input("n-levels", "value"),
    Input("n-trials", "value"),
    Input("n-blocks", "value"),
    Input("tabs", "active_tab"),
    prevent_initial_call=True,
)
def update_x_range(
    param: list[float],
    n_levels: int,
    n_trials: int,
    n_blocks: int,
    active_tab: str,
) -> tuple[str, str, list[dict[Hashable, Any]], list[dict[Hashable, Any]]]:
    """Update x range based on threshold and slope."""
    params = dict(zip(["x_0", "k", "gamma", "lambda"], param, strict=True))
    min_, max_ = logistic.ppf([0.01, 0.99], loc=params["x_0"], scale=params["k"])
    ix = pd.Index(np.linspace(min_, max_, n_levels), name="Intensity")
    p = pa_points.psi(ix, params)
    all_points = {}
    all_blocks = []
    for i in range(n_blocks):
        execution_plan = pd.Series(
            [random.choice(ix) for _ in range(n_trials)],
            name="Intensity",
        )
        results = pd.Series(
            [int(random.random() < p.loc[x]) for x in execution_plan],
            name="Result",
        )
        fit = Logit(
            results,
            sm.add_constant(execution_plan.to_frame()),
        ).fit(disp=False)
        fit_params = fit.params
        block = fit_params.rename({"const": "x_0", "Intensity": "k"}).to_dict() | {
            "gamma": 0.0,
            "lambda": 0.0,
            "Block": i,
        }
        counts = execution_plan.value_counts().rename("n trials").sort_index()
        hits = results.groupby(execution_plan).sum().rename("Hits")
        hit_rate = pd.Series(hits / counts, name="Hit Rate")
        logit_hit_rate = pd.Series(logit(hit_rate), name="logit(Hit Rate)")
        points = pd.concat(
            [counts, p, hits, hit_rate, logit_hit_rate],
            axis=1,
        ).reset_index()
        points["Block"] = i
        all_points[i] = points
        all_blocks.append(block)
    final_points = pd.concat(all_points, names=["Block"])
    return (
        f"{min_:0.2f}",
        f"{max_:0.2f}",
        final_points.to_dict("records"),
        [] if active_tab == "upload" else all_blocks,
    )


@callback(
    Output("plot", "figure"),
    Input("logit", "value"),
    Input({"type": "param", "name": ALL}, "value"),
    Input("points-table", "data"),
    Input("blocks-table", "data"),
    Input("tabs", "active_tab"),
)
def update_fig_model(
    form: str,
    param: list[float],
    data: list[dict[str, float]],
    fits: list[dict[str, float]],
    active_tab: str,
) -> tuple[go.Figure, dash_table.DataTable]:
    """Update plot and tables based on data store and selected view."""
    if data is None or active_tab == "upload":
        fig = px.scatter(pd.DataFrame({"Intensity": []}), template="plotly_white")
    else:
        params = dict(zip(["x_0", "k", "gamma", "lambda"], param, strict=True))
        model = params["gamma"] + (
            1 - params["gamma"] - params["lambda"]
        ) * pa_blocks.logistic(params)
        fit_params = fits[0]
        fit_psi = fit_params["gamma"] + (
            1 - fit_params["gamma"] - fit_params["lambda"]
        ) * pa_blocks.logistic(fit_params)
        y = model["logit(Hit Rate)"] if form == "log" else model["Hit Rate"]
        y_fit = fit_psi["logit(Hit Rate)"] if form == "log" else fit_psi["Hit Rate"]
        fig = (
            px.scatter(
                pd.DataFrame.from_records(data),
                x="Intensity",
                y=y.name,
                size="n trials",
                template="plotly_white",
            )
            .add_trace(
                go.Scatter(
                    x=model.index,
                    y=y,
                    name="Model",
                    mode="lines",
                    line_color="#636EFA",
                ),
            )
            .add_trace(
                go.Scatter(
                    x=fit_psi.index,
                    y=y_fit,
                    name="Predicted",
                    mode="lines",
                    line_dash="dash",
                    line_color="#636EFA",
                ),
            )
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


@callback(
    Output({"type": "param", "name": ALL}, "value"),
    Input("preset", "value"),
    State({"type": "param", "name": ALL}, "value"),
)
def set_params_to_preset(
    preset: str,
    param: list[float],
) -> list[float]:
    """Set parameters to preset values."""
    presets = {
        "standard": [0.0, 1.0, 0.0, 0.0],
        "non-standard": [10, 2, 0.2, 0.1],
        "2AFC": [0, 1, 0.5, 0.0],
    }
    return presets.get(preset, param)


@callback(
    Output({"type": "free", "name": ALL}, "value"),
    Input("preset", "value"),
    State({"type": "free", "name": ALL}, "value"),
)
def set_fixed_params_to_preset(
    preset: str,
    param: list[bool],
) -> list[bool]:
    """Set parameters to preset values."""
    presets = {
        "standard": [True] * 4,
        "non-standard": [True] * 4,
        "2AFC": [True, True, False, True],
    }
    return presets.get(preset, param)


@callback(
    Output("points-table", "data"),
    Input("blocks-table", "derived_virtual_selected_rows"),
    State("points-store", "data"),
)
def filter_points(
    selected_rows: list[int],
    points: list[dict[Hashable, Any]],
) -> list[dict[Hashable, Any]]:
    """Filter points table."""
    if not selected_rows:
        return []
    points_df = pd.DataFrame.from_records(points)
    return points_df[points_df["Block"].isin(selected_rows)].to_dict("records")


@callback(
    Output("points-store", "data"),
    Input("upload", "contents"),
    State("upload", "filename"),
)
def upload_data(contents: str, filename: str) -> list[dict[Hashable, Any]]:
    """Upload data."""
    if contents is None:
        return []
    content_type, content_string = contents.split(",")
    decoded = io.StringIO(base64.b64decode(content_string).decode("utf-8"))
    if "csv" in filename:
        points = pd.read_csv(decoded)
    return points.to_dict("records")


@callback(
    Output("upload-collapse", "is_open"),
    Input("tabs", "active_tab"),
)
def toggle_upload(active_tab: str) -> bool:
    """Toggle upload."""
    return active_tab == "upload"


if __name__ == "__main__":
    app.run(debug=True)
