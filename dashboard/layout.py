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

from dashboard.components import (
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
        html.H4("Model"),
        dcc.Markdown(
            """
            $$
            \\psi(x) = \\gamma + (1 - \\gamma - \\lambda)F(x)
            $$

            """,
            mathjax=True,
        ),
        html.H4("Link Function"),
        link_function,
        html.H4("Model Parameters"),
        model_params,
        html.H4("Stimulus"),
        stimulus_params,
        html.H4("Simulate"),
        dbc.Container(simulation_params),
    ],
    width=3,
)

plot_col = dbc.Col(
    [
        dcc.Graph(id="plot", className="mb-3"),
        html.H5("Plot Options"),
        dbc.Container(
            [
                dbc.FormText("Y Transform"),
                html.Div(
                    dbc.RadioItems(
                        options=[
                            {"label": "Hit Rate", "value": "linear"},
                            {
                                "label": "logit(Hit Rate)",
                                "value": "log",
                            },
                        ],
                        value="linear",
                        inline=True,
                        id="logit",
                        className="btn-group",
                        inputClassName="btn-check",
                        labelClassName="btn btn-outline-primary",
                        labelCheckedClassName="active",
                    ),
                    className="radio-group",
                ),
            ],
        ),
    ],
    width=5,
    className="mt-5",
)

data_col = dbc.Col(
    [
        html.H4("Points", className="mt-3"),
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
                                    src="assets/PsychoAnalyze_100x100.png",
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
        dbc.Row(
            [
                input_col,
                plot_col,
                data_col,
            ],
        ),
    ],
)
