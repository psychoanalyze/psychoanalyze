"""Layout for Dash dashboard."""

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

import dash_bootstrap_components as dbc
from dash import dcc, html

from psychoanalyze.dashboard.components import (
    blocks_table,
    link_function,
    model_params,
    points_table,
    simulation_params,
    stimulus_params,
)

font_family = "Comfortaa, Times, serif"
subtitle = "Interactive data simulation & analysis for psychophysics."


input_col = dbc.Col(
    [
        dcc.Upload(
            [
                html.P("Upload CSV/parquet with columns:", className="mb-0"),
                html.P("Block, Intensity, Result."),
                html.P("Your data stays in the browser.", className="mb-0"),
            ],
            id="upload",
            style={
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
            },
            className="mb-3 p-3",
        ),
        html.H4("Link Function"),
        link_function,
        dbc.Row(
            [
                dbc.Col(html.H4("Model Parameters")),
                dbc.Col(
                    html.I(className="bi bi-info-circle", id="fixed-param-info"),
                    width="auto",
                ),
            ],
            justify="start",
            align="center",
        ),
        dbc.Tooltip(
            "Checked: free parameter\nUnchecked: fixed parameter",
            target="fixed-param-info",
        ),
        model_params,
        html.H4("Stimulus"),
        stimulus_params,
        html.H4("Simulate"),
        dbc.Container(dbc.Row(simulation_params, justify="center")),
    ],
    width=3,
    class_name="mt-4",
    id="input-col",
)

plot_col = dbc.Col(
    [
        dcc.Markdown(
            """
            $$
            \\psi(x) = \\gamma + (1 - \\gamma - \\lambda)F(x)
            $$

            """,
            mathjax=True,
            id="plot-equation",
        ),
        dcc.Graph(id="plot", className="mb-3"),
    ],
    width=5,
)

data_col = dbc.Col(
    [
        html.H4("Blocks", className="mt-3 mb-2"),
        dbc.Container(blocks_table, className="mb-3"),
        dcc.Markdown(
            """
            $$
            F(x) = \\frac{1}{1 + e^{-(\\beta_0 + \\beta_1 x)}}
            $$
            """,
            mathjax=True,
        ),
        html.H4("Points", className="mb-2"),
        dbc.Container(points_table, className="mb-3"),
        dbc.Row(
            [
                dbc.Col(
                    dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem(
                                "SVG",
                                id={
                                    "type": "img-export",
                                    "name": "svg",
                                },
                            ),
                            dbc.DropdownMenuItem(
                                "PNG",
                                id={
                                    "type": "img-export",
                                    "name": "png",
                                },
                            ),
                            dbc.DropdownMenuItem(
                                "PDF",
                                id={
                                    "type": "img-export",
                                    "name": "pdf",
                                },
                            ),
                        ],
                        label="Download plot",
                        id="figure-download",
                        toggle_style={"border-radius": 5},
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem(
                                "Parquet",
                                id={
                                    "type": "data-export",
                                    "name": "parquet",
                                },
                            ),
                            dbc.DropdownMenuItem(
                                "CSV",
                                id={
                                    "type": "data-export",
                                    "name": "csv",
                                },
                            ),
                            dbc.DropdownMenuItem(
                                "JSON",
                                id={
                                    "type": "data-export",
                                    "name": "json",
                                },
                            ),
                            dbc.DropdownMenuItem(
                                "DuckDB",
                                id={
                                    "type": "data-export",
                                    "name": "duckdb",
                                },
                            ),
                        ],
                        label="Download data",
                        id="data-export",
                        toggle_style={"border-radius": 5},
                    ),
                    width="auto",
                ),
            ],
            justify="around",
        ),
        dcc.Download(id="img-download"),
        dcc.Download(id="data-download"),
    ],
)


layout = dbc.Container(
    [
        dcc.Store(id="points-store"),
        dcc.Store(id="blocks-store"),
        dcc.Store(id="trials-store"),
        dbc.NavbarSimple(
            [
                dbc.NavItem(
                    [
                        dbc.NavLink(
                            "GitHub",
                            href="https://github.com/psychoanalyze/psychoanalyze",
                        ),
                        html.I(className="bi bi-github"),
                    ],
                    className="d-flex align-items-center mx-2",
                ),
                dbc.NavItem(
                    [
                        dbc.NavLink(
                            "Docs",
                            href="https://docs.psychoanalyze.io",
                        ),
                        html.I(className="bi bi-book"),
                    ],
                    className="d-flex align-items-center mx-2",
                ),
            ],
            brand=dbc.Col(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Img(
                                    src="assets/logo_transparent_100x100.png",
                                ),
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    html.H1(
                                        "PsychoAnalyze",
                                        style={"font-family": font_family},
                                    ),
                                    html.P(subtitle),
                                ],
                                align="end",
                            ),
                        ],
                        align="center",
                        justify="start",
                        className="ms-4",
                    ),
                    dbc.Row(),
                ],
            ),
            brand_href="/",
            class_name="mb-2",
            style={"border-radius": "0 0 7px 7px"},
        ),
        dbc.Collapse(
            id="upload-collapse",
        ),
        dbc.Row(
            [
                input_col,
                plot_col,
                data_col,
            ],
        ),
    ],
)
