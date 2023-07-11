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
    blocks_table,
    experiment_params,
    points_table,
    psi_params,
)

font_family = "Comfortaa, Times, serif"
subtitle = "Interactive data simulation & analysis for psychophysics."


component_column = dbc.Col(
    [
        html.H3("Simulation Parameters"),
        experiment_params,
        psi_params,
    ],
    width=3,
)

upload_component = dcc.Upload(
    "Upload data - drag-and-drop OR click to open upload tool",
    id="upload-data",
    style={
        "width": "100%",
        "height": "60px",
        "lineHeight": "60px",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "textAlign": "center",
    },
    multiple=True,
)

dataset_component = dcc.Dropdown(
    options=[
        {
            "label": html.Span(
                ["Schlichenmeyer et al. 2022"],
                style={"color": "black"},
            ),
            "value": "schlich2022",
        },
    ],
    placeholder="Select an open dataset...",
    id="dataset",
)

empirical_data_components = dbc.Row(
    [
        dbc.Col(upload_component),
        dbc.Col(dataset_component),
    ],
    align="center",
    className="mb-3",
)

psi_tab = dbc.Tab(
    tab_id="psi-tab",
    label="Psychometric Function",
    activeTabClassName="fw-bold fst-italic",
)

ecdf_tab = dbc.Tab(
    label="eCDF",
    tab_id="ecdf-tab",
)

time_series_tab = dbc.Tab(
    tab_id="time-series-tab",
    label="Time Series",
    activeTabClassName="fw-bold fst-italic",
)

sd_tab = dbc.Tab(
    label="Strength-Duration",
    tab_id="sd-tab",
)

plot_tabs = dbc.Col(
    [
        empirical_data_components,
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Tabs(
                            [
                                psi_tab,
                                ecdf_tab,
                                time_series_tab,
                                sd_tab,
                            ],
                            active_tab="psi-tab",
                            id="plot-tabs",
                        ),
                        dcc.Graph(id="plot", className="mb-3"),
                        html.H5("Plot Options"),
                        html.H6("Y Axis"),
                        html.Div(
                            dbc.RadioItems(
                                options=[
                                    {"label": "logit(Hit Rate)", "value": "log"},
                                    {"label": "Hit Rate", "value": "linear"},
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
                    width=7,
                ),
                dbc.Col(
                    [
                        html.H4("Blocks", className="mt-2"),
                        html.Div(blocks_table, className="mb-3"),
                        html.H4("Points"),
                        html.Div(points_table, className="mb-3"),
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
                                        label="Download figure as... ",
                                        id="figure-download",
                                        toggle_style={"border-radius": 5},
                                    ),
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
                                        label="Download data as... ",
                                        id="data-export",
                                        toggle_style={"border-radius": 5},
                                    ),
                                ),
                            ],
                        ),
                        dcc.Download(id="img-download"),
                        dcc.Download(id="data-download"),
                    ],
                ),
            ],
        ),
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
            class_name="mb-3",
            style={"border-radius": "0 0 7px 7px"},
            fluid=True,
        ),
        dbc.Row(
            [
                component_column,
                plot_tabs,
            ],
        ),
    ],
)
