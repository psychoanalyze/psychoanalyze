"""Layout for Dash dashboard.

---
Copyright 2023 Tyler Schlichenmeyer

This file is part of PsychoAnalyze.
PsychoAnalyze is free software: you can redistribute it and/or modify it under the terms
of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

PsychoAnalyze is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Foobar.
If not, see <https://www.gnu.org/licenses/>.
"""

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from dashboard.components import experiment_params, psi_params

component_column = dbc.Col(
    [
        html.H3("Simulation Parameters"),
        experiment_params,
        psi_params,
    ],
    width=3,
)

upload_component = dcc.Upload(
    """Upload your own data -
                        drag and drop, or click to open file browser
                        """,
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

empirical_data_components = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(upload_component),
                dbc.Col(dataset_component),
            ],
        ),
    ],
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
            class_name="my-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id="plot",
                        ),
                    ],
                    width=7,
                ),
                dbc.Col(
                    [
                        dash_table.DataTable(
                            id="table",
                            columns=[
                                {
                                    "name": "Subject",
                                    "id": "Subject",
                                },
                                {
                                    "name": "Block",
                                    "id": "Block",
                                },
                                {
                                    "name": "Slope",
                                    "id": "slope",
                                    "type": "numeric",
                                    "format": dash_table.Format.Format(
                                        precision=2,
                                        scheme=dash_table.Format.Scheme.fixed,
                                    ),
                                },
                                {
                                    "name": "Threshold",
                                    "id": "Threshold",
                                    "type": "numeric",
                                    "format": dash_table.Format.Format(
                                        precision=2,
                                        scheme=dash_table.Format.Scheme.fixed,
                                    ),
                                },
                            ],
                            row_selectable="multi",
                            style_data={"color": "black"},
                            style_header={"color": "black"},
                            page_size=15,
                        ),
                    ],
                    width=4,
                ),
            ],
        ),
    ],
)

layout = dbc.Container(
    [
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
                    dbc.Row(html.H1("PsychoAnalyze")),
                    dbc.Row(
                        html.P(
                            "Interactive data simulation & analysis for psychophysics.",
                        ),
                    ),
                ],
            ),
            brand_href="/",
            class_name="mb-3",
        ),
        dbc.Row(
            [
                component_column,
                plot_tabs,
            ],
        ),
    ],
)
