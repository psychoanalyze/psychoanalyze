"""Components for Dash dashboard."""

# Copyright 2023 Tyler Schlichenmeyer

# This file is part of PsychoAnalyze.
# PsychoAnalyze is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# PsychoAnalyze is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
#  PsychoAnalyze. If not, see <https://www.gnu.org/licenses/>.

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

experiment_params = dbc.Card(
    [
        html.H4("Experimental Design", className="card-title mb-3"),
        dcc.Dropdown(
            id="exp-type",
            options=[
                {
                    "label": html.Span(
                        "Method of Constant Stimuli",
                        style={"color": "black"},
                    ),
                    "value": "moc",
                },
            ],
            value="moc",
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(
                        id={"type": "experiment-param", "name": "n-trials"},
                        type="number",
                        value=70,
                        style={"border-radius": 3},
                    ),
                    width=4,
                ),
                dbc.Label("trials per block", width=6),
            ],
            className="mb-1",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(
                        id={"type": "experiment-param", "name": "n-blocks"},
                        type="number",
                        value=2,
                        style={"border-radius": 3},
                    ),
                    width=4,
                ),
                dbc.Label("blocks", width=6),
            ],
            className="mb-1",
        ),
        html.H5("Sampling strategy", className="mt-4 mb-2"),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(
                        id={"type": "experiment-param", "name": "n-levels"},
                        type="number",
                        value=7,
                        style={"border-radius": 3},
                    ),
                    width=4,
                ),
                dbc.Label("intensity levels", html_for="n-levels", width=6),
            ],
            className="mb-1",
        ),
        dbc.Row(
            [
                dbc.Label("Intensity Range", width=6),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Input(
                                        id={"type": "x", "name": "min"},
                                        type="number",
                                        value=-4,
                                        style={"border-radius": 3},
                                    ),
                                ),
                                dbc.Col(
                                    dbc.Input(
                                        id={"type": "x", "name": "max"},
                                        type="number",
                                        value=4,
                                        style={"border-radius": 3},
                                    ),
                                ),
                            ],
                            className="mb-2",
                        ),
                        dbc.Checklist(
                            options=[{"label": "Fix to model", "value": "fix-range"}],
                            id="fix-range",
                        ),
                    ],
                ),
            ],
        ),
    ],
    body=True,
    className="mb-4",
    style={"border-radius": 7},
)

psi_params = dbc.Card(
    [
        html.H4("Psychometric Model", className="card-title mb-3"),
        dcc.Dropdown(
            id="f",
            options=[{"label": "Logistic (expit)", "value": "expit"}],
            value="expit",
            className="mb-3",
        ),
        dcc.Markdown(
            """
            $$
            f(x) = \\frac{1}{1 + e^{-k(x-x_0)}}
            $$
            """,
            mathjax=True,
        ),
        dbc.Row(
            [
                dbc.Label("Intercept", width=6, style={"text-align": "right"}),
                dbc.Col(
                    dbc.Input(
                        id={"type": "param", "id": 0},
                        type="number",
                        value=0.0,
                        style={"border-radius": 3},
                        className="mb-1",
                    ),
                    width=6,
                ),
            ],
            style={"justify-content": "center"},
        ),
        dbc.Row(
            [
                dbc.Label("Slope", width=6, style={"text-align": "right"}),
                dbc.Col(
                    dbc.Input(
                        id={"type": "param", "id": 1},
                        type="number",
                        value=1.0,
                        step=0.1,
                        style={"border-radius": 3},
                        className="mb-1",
                    ),
                    width=6,
                ),
            ],
            style={"justify-content": "center"},
        ),
        dbc.Row(
            [
                dbc.Label("Guess Rate ", width=6, style={"text-align": "right"}),
                dbc.Col(
                    dbc.Input(
                        id={"type": "param", "id": 2},
                        type="number",
                        value=0.0,
                        step=0.1,
                        style={"border-radius": 3},
                        className="mb-1",
                    ),
                    width=6,
                ),
            ],
            style={"justify-content": "center"},
        ),
        dbc.Row(
            [
                dbc.Label("Lapse Rate", width=6, style={"text-align": "right"}),
                dbc.Col(
                    dbc.Input(
                        id={"type": "param", "id": 3},
                        type="number",
                        value=0.0,
                        step=0.1,
                        style={"border-radius": 3},
                    ),
                    width=6,
                ),
            ],
            style={"justify-content": "center"},
        ),
    ],
    body=True,
    style={"border-radius": 7},
)


points_table = dash_table.DataTable(
    id="table",
    columns=[
        {
            "name": "Intensity",
            "id": "Intensity",
            "type": "numeric",
            "format": dash_table.Format.Format(
                precision=2,
                scheme=dash_table.Format.Scheme.fixed,
            ),
        },
        {
            "name": "Hits",
            "id": "Hits",
            "type": "numeric",
        },
        {
            "name": "n",
            "id": "n",
            "type": "numeric",
        },
        {
            "name": "Hit Rate",
            "id": "Hit Rate",
            "type": "numeric",
            "format": dash_table.Format.Format(
                precision=2,
                scheme=dash_table.Format.Scheme.fixed,
            ),
        },
        {
            "name": "logit(Hit Rate)",
            "id": "logit(Hit Rate)",
            "type": "numeric",
            "format": dash_table.Format.Format(
                precision=2,
                scheme=dash_table.Format.Scheme.fixed,
            ),
        },
    ],
    style_data={"color": "black"},
    style_header={"color": "black"},
    page_size=15,
)

blocks_table = dash_table.DataTable(
    id="blocks-table",
    row_selectable="single",
    selected_rows=[0],
    columns=[
        {
            "name": "Threshold",
            "id": "Threshold",
            "type": "numeric",
            "format": dash_table.Format.Format(
                precision=2,
                scheme=dash_table.Format.Scheme.fixed,
            ),
        },
        {
            "name": "Slope",
            "id": "Slope",
            "type": "numeric",
            "format": dash_table.Format.Format(
                precision=2,
                scheme=dash_table.Format.Scheme.fixed,
            ),
        },
        {
            "name": "Guess Rate",
            "id": "Guess Rate",
            "type": "numeric",
            "format": dash_table.Format.Format(
                precision=2,
                scheme=dash_table.Format.Scheme.fixed,
            ),
        },
        {
            "name": "Lapse Rate",
            "id": "Lapse Rate",
            "type": "numeric",
            "format": dash_table.Format.Format(
                precision=2,
                scheme=dash_table.Format.Scheme.fixed,
            ),
        },
    ],
    style_data={"color": "black"},
    style_header={"color": "black"},
)
