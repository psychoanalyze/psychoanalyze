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
import zipfile
from collections.abc import Hashable
from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pytz
from dash import (
    ALL,
    MATCH,
    Dash,
    Input,
    Output,
    State,
    callback,
    callback_context,
    dcc,
)
from dash_bootstrap_components import icons, themes
from scipy.special import expit, logit

from psychoanalyze.dashboard.layout import layout
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

Records = list[dict[Hashable, Any]]


@callback(
    Output("trials-store", "data"),
    Output({"type": "x-param", "name": "min"}, "value"),
    Output({"type": "x-param", "name": "max"}, "value"),
    Input("upload", "contents"),
    State("upload", "filename"),
    Input({"type": "n-param", "name": ALL}, "value"),
    Input({"type": "param", "name": ALL}, "value"),
)
def update_data(
    contents: str,
    filename: str,
    n_param: list[int],
    param: list[float],
) -> tuple[Records, float, float]:
    """Update points table."""
    n_param_values = [
        "n_levels",
        "n_trials",
        "n_blocks",
    ]
    n_params = pd.Series(n_param, index=n_param_values)
    param = [*param, 0.0, 0.0]
    params = pd.Series(param, index=["x_0", "k", "gamma", "lambda"])
    params["intercept"] = -params["x_0"] / params["k"]
    params["slope"] = 1 / params["k"]
    min_x = (logit(0.01) - params["intercept"]) / params["slope"]
    max_x = (logit(0.99) - params["intercept"]) / params["slope"]
    if callback_context.triggered_id == "upload":
        _, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        if "zip" in filename:
            with zipfile.ZipFile(io.BytesIO(decoded)) as z:
                trials = pd.read_csv(z.open("trials.csv"))
        else:
            trials = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    else:
        points_ix = pd.Index(
            np.linspace(min_x, max_x, n_params["n_levels"]),
            name="Intensity",
        )
        all_trials = {}
        for i in range(n_params["n_blocks"]):
            execution_plan = pd.Index(
                [random.choice(points_ix) for _ in range(n_params["n_trials"])],
                name="Intensity",
            )
            trials_i = pd.Series(
                [
                    int(
                        random.random()
                        < expit(x * params["slope"] + params["intercept"]),
                    )
                    for x in execution_plan
                ],
                name="Result",
                index=execution_plan,
            )
            all_trials[i] = trials_i
        trials = pd.concat(all_trials, names=["Block"]).reset_index()
    return trials.to_dict("records"), min_x, max_x


@callback(
    Output("points-store", "data"),
    Input("trials-store", "data"),
)
def update_points_table(trials: Records) -> Records:
    """Update points table."""
    trials_df = pd.DataFrame.from_records(trials)
    trials_df["Intensity"] = trials_df["Intensity"].astype(float)
    points = pa_points.from_trials(trials_df)
    return points.to_dict("records")


@callback(
    Output("blocks-table", "data"),
    Input("trials-store", "data"),
)
def update_blocks_table(trials: Records) -> Records:
    """Update blocks table."""
    trials_df = pd.DataFrame.from_records(trials)

    blocks = trials_df.groupby("Block").apply(pa_blocks.fit).reset_index()
    blocks["gamma"] = 0.0
    blocks["lambda"] = 0.0
    return blocks.to_dict("records")


@callback(
    Output("points-table", "data"),
    Input("blocks-table", "derived_virtual_selected_rows"),
    Input("points-store", "data"),
)
def filter_points(
    selected_rows: list[int],
    points: Records,
) -> Records:
    """Filter points table."""
    points_df = pd.DataFrame.from_records(points)
    return (
        points_df[points_df["Block"].isin(selected_rows)].to_dict("records")
        if selected_rows
        else points_df.to_dict("records")
    )


@callback(
    Output("plot", "figure"),
    Input({"type": "param", "name": ALL}, "value"),
    Input("points-table", "data"),
    Input("blocks-table", "data"),
    Input("blocks-table", "derived_virtual_selected_rows"),
    State({"type": "x-param", "name": "min"}, "value"),
    State({"type": "x-param", "name": "max"}, "value"),
)
def update_fig(  # noqa: PLR0913
    param: list[float],
    points: Records,
    blocks: Records,
    selected_rows: list[int],
    min_x: float,
    max_x: float,
) -> go.Figure:
    """Update plot and tables based on data store and selected view."""
    param = [*param, 0.0, 0.0]
    params = pd.Series(param, index=["x_0", "k", "gamma", "lambda"])
    params["intercept"] = -params["x_0"] / params["k"]
    params["slope"] = 1 / params["k"]
    blocks = [blocks[i] for i in selected_rows] + [
        {"Block": "Model"} | params.to_dict(),
    ]
    x = pd.Index(
        np.linspace(min_x, max_x, 100),
        name="Intensity",
    )
    fits = pd.concat(
        {
            block["Block"]: pd.Series(
                expit(x.to_numpy() * block["slope"] + block["intercept"]),
                name="Hit Rate",
                index=x,
            )
            for block in blocks
        },
        names=["Block"],
    ).reset_index()
    fits["Block"] = fits["Block"].astype(str)
    points_df = pd.DataFrame.from_records(points)
    points_df["Block"] = points_df["Block"].astype(str)
    fits_fig = px.line(
        fits,
        x="Intensity",
        y="Hit Rate",
        color="Block",
    )
    results_fig = px.scatter(
        points_df,
        x="Intensity",
        y="Hit Rate",
        size="n trials",
        color="Block",
        template="plotly_white",
    )
    return results_fig.add_traces(fits_fig.data)


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
    State("blocks-table", "data"),
    State("trials-store", "data"),
    prevent_initial_call=True,
)
def export_data(
    export_clicked: int,  # noqa: ARG001
    points: Records,
    blocks: Records,
    trials: Records,
) -> dict[str, Any | None]:
    """Export image."""
    format_suffix = callback_context.triggered_id["name"]
    points_df = pd.DataFrame.from_records(points)
    blocks_df = pd.DataFrame.from_records(blocks)
    trials_df = pd.DataFrame.from_records(trials)
    if format_suffix == "csv":
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(
            zip_buffer,
            mode="a",
            compression=zipfile.ZIP_DEFLATED,
            allowZip64=False,
        ) as zip_file:

            def write_file(df: pd.DataFrame, name: str) -> None:
                buffer = io.StringIO()
                df.to_csv(buffer, index=False)
                zip_file.writestr(name, buffer.getvalue())

            data = {
                "points": points_df,
                "blocks": blocks_df,
                "trials": trials_df,
            }
            for level, points_df in data.items():
                write_file(points_df, f"{level}.csv")

        zip_buffer.seek(0)
        zip_bytes = zip_buffer.read()

        base64_bytes = base64.b64encode(zip_bytes)
        base64_string = base64_bytes.decode("utf-8")
        timestamp = datetime.now(tz=pytz.timezone("America/Chicago")).strftime(
            "%Y-%m-%d_%H%M",
        )
        download = {
            "base64": True,
            "content": base64_string,
            "filename": f"{timestamp}_psychoanalyze.zip",
        }

    elif format_suffix == "json":
        download = dcc.send_data_frame(points_df.to_json, "data.json")
    elif format_suffix == "parquet":
        download = dcc.send_data_frame(points_df.to_parquet, "data.parquet")
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
    Output("plot-equation", "children"),
    Input("show-eqn", "n_clicks"),
)
def toggle_eqn(n_clicks: int) -> tuple[bool, str, str]:
    """Toggle equation."""
    equation_abstracted = """
    $$
    \\psi(x) = \\gamma + (1 - \\gamma - \\lambda)F(x)
    $$
    """
    if n_clicks:
        n_clicks_is_even = n_clicks % 2 == 0
        label = "Show F(x) ▾ " if n_clicks_is_even else "Hide F(x) ▴ "
        equation_expanded = """
        $$
        \\psi(x) = \\frac{\\gamma + (1 - \\gamma - \\lambda)}{1 + e^{-k(x - x_0)}}
        $$
        """
        equation = equation_abstracted if n_clicks_is_even else equation_expanded
        return not n_clicks_is_even, label, equation
    return False, "Show F(x) ▾ ", equation_abstracted


@callback(
    Output({"type": "param", "name": MATCH}, "disabled"),
    Input({"type": "free", "name": MATCH}, "value"),
    prevent_initial_call=True,
)
def toggle_param(free: bool) -> bool:  # noqa: FBT001
    """Toggle parameter."""
    return not free


@callback(
    Output({"type": "param", "name": ALL}, "value"),
    Input("preset", "value"),
    State({"type": "param", "name": ALL}, "value"),
    prevent_initial_call=True,
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
    prevent_initial_call=True,
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
    Output("points-table", "page_size"),
    Input({"type": "n-param", "name": "n-levels"}, "value"),
)
def update_page_size(n_levels: int) -> int:
    """Update page size."""
    return n_levels


if __name__ == "__main__":
    app.run(debug=True)
