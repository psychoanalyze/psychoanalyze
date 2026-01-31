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

"""Main Dash app file.

Contains callbacks.
"""

import base64
import io
import zipfile
from collections.abc import Hashable
from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
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
from psychoanalyze.dashboard.utils import process_upload
from psychoanalyze.data import blocks as pa_blocks
from psychoanalyze.data import points as pa_points
from psychoanalyze.data.logistic import to_intercept, to_slope
from psychoanalyze.data.points import generate_index
from psychoanalyze.data.trials import generate

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
def update_trials(
    contents: str,
    filename: str,
    n_param: list[int],
    param: list[float],
) -> tuple[Records, float, float]:
    """Update points table."""
    n_params = pl.DataFrame(
        {"name": ["n_levels", "n_trials", "n_blocks"], "value": n_param},
    )
    params_dict = dict(zip(["x_0", "k", "gamma", "lambda"], [*param, 0.0, 0.0]))
    params_dict["intercept"] = to_intercept(params_dict["x_0"], params_dict["k"])
    params_dict["slope"] = to_slope(params_dict["k"])
    min_x = (logit(0.01) - params_dict["intercept"]) / params_dict["slope"]
    max_x = (logit(0.99) - params_dict["intercept"]) / params_dict["slope"]
    if callback_context.triggered_id == "upload":
        trials = process_upload(contents, filename)
    else:
        n_levels = n_params.filter(pl.col("name") == "n_levels")["value"][0]
        n_trials = n_params.filter(pl.col("name") == "n_trials")["value"][0]
        n_blocks = n_params.filter(pl.col("name") == "n_blocks")["value"][0]
        trials = generate(
            n_trials=n_trials,
            options=generate_index(n_levels, [min_x, max_x]),
            params=params_dict,
            n_blocks=n_blocks,
        )
    return trials.to_dicts(), min_x, max_x


@callback(
    Output("points-store", "data"),
    Input("trials-store", "data"),
)
def update_points_table(trials: Records) -> Records:
    """Update points table."""
    trials_df = pl.from_dicts(trials)
    trials_df = trials_df.with_columns(pl.col("Intensity").cast(pl.Float64))
    points = pa_points.from_trials(trials_df)
    return points.to_dicts()


@callback(
    Output("blocks-table", "data"),
    Input("trials-store", "data"),
)
def update_blocks_table(trials: Records) -> Records:
    """Update blocks table."""
    trials_df = pl.from_dicts(trials)

    blocks_list = []
    for block_id in trials_df["Block"].unique().to_list():
        block_trials = trials_df.filter(pl.col("Block") == block_id)
        fit_result = pa_blocks.fit(
            block_trials,
            draws=500,
            tune=500,
            chains=1,
            target_accept=0.9,
        )
        summary = pa_blocks.summarize_fit(fit_result)
        summary["Block"] = block_id
        summary["gamma"] = 0.0
        summary["lambda"] = 0.0
        blocks_list.append(summary)
    return blocks_list


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
    points_df = pl.from_dicts(points)
    if selected_rows:
        return points_df.filter(pl.col("Block").is_in(selected_rows)).to_dicts()
    return points_df.to_dicts()


@callback(
    Output("plot", "figure"),
    Input({"type": "param", "name": ALL}, "value"),
    Input("points-table", "data"),
    Input("blocks-table", "data"),
    Input("blocks-table", "derived_virtual_selected_rows"),
    State({"type": "x-param", "name": "min"}, "value"),
    State({"type": "x-param", "name": "max"}, "value"),
)
def update_fig(
    param: list[float],
    points: Records,
    blocks: Records,
    selected_rows: list[int],
    min_x: float,
    max_x: float,
) -> go.Figure:
    """Update plot and tables based on data store and selected view."""
    param = [*param, 0.0, 0.0]
    params_dict = dict(zip(["x_0", "k", "gamma", "lambda"], param))
    params_dict["intercept"] = -params_dict["x_0"] / params_dict["k"]
    params_dict["slope"] = 1 / params_dict["k"]
    blocks = [blocks[i] for i in selected_rows] + [
        {"Block": "Model"} | params_dict,
    ]
    x = np.linspace(min_x, max_x, 100)
    fits_list = []
    for block in blocks:
        y = expit(x * block["slope"] + block["intercept"])
        fits_list.append(
            pl.DataFrame(
                {
                    "Intensity": x,
                    "Hit Rate": y,
                    "Block": [str(block["Block"])] * len(x),
                },
            ),
        )
    fits = pl.concat(fits_list)
    points_df = pl.from_dicts(points).with_columns(pl.col("Block").cast(pl.Utf8))
    fits_fig = px.line(
        fits.to_pandas(),
        x="Intensity",
        y="Hit Rate",
        color="Block",
    )
    results_fig = px.scatter(
        points_df.to_pandas(),
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
    export_clicked: int,
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
    export_clicked: int,
    points: Records,
    blocks: Records,
    trials: Records,
) -> dict[str, Any | None]:
    """Export image."""
    format_suffix = callback_context.triggered_id["name"]
    points_df = pl.from_dicts(points)
    blocks_df = pl.from_dicts(blocks)
    trials_df = pl.from_dicts(trials)
    if format_suffix == "csv":
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(
            zip_buffer,
            mode="a",
            compression=zipfile.ZIP_DEFLATED,
            allowZip64=False,
        ) as zip_file:

            def write_file(df: pl.DataFrame, name: str) -> None:
                buffer = io.StringIO()
                df.write_csv(buffer)
                zip_file.writestr(name, buffer.getvalue())

            data = {
                "points": points_df,
                "blocks": blocks_df,
                "trials": trials_df,
            }
            for level, level_df in data.items():
                write_file(level_df, f"{level}.csv")

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
        download = dcc.send_data_frame(points_df.to_pandas().to_json, "data.json")
    elif format_suffix == "parquet":
        download = dcc.send_data_frame(points_df.to_pandas().to_parquet, "data.parquet")
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
def toggle_param(free: bool) -> bool:
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
