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
        html.H4("Experimental Design", className="mb-4"),
        dcc.Dropdown(
            id="exp-type",
            options=[{"label": "Method of Constant Stimuli", "value": "moc"}],
            value="moc",
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("n trials", width=6),
                dbc.Col(
                    dbc.Input(
                        id={"type": "experiment-param", "name": "n-trials"},
                        type="number",
                        value=70,
                    ),
                    width=6,
                ),
            ],
            className="mb-1",
        ),
        dbc.Row(
            [
                dbc.Label("n levels", html_for="n-levels", width=6),
                dbc.Col(
                    dbc.Input(
                        id={"type": "experiment-param", "name": "n-levels"},
                        type="number",
                        value=7,
                    ),
                    width=6,
                ),
            ],
            className="mb-1",
        ),
        dbc.Row(
            [
                dbc.Label("min(x)", html_for="min-x", width=3),
                dbc.Col(
                    dbc.Input(id="min-x", type="number", value=-4),
                    width=3,
                ),
                dbc.Col(
                    dbc.Input(id="max-x", type="number", value=4),
                    width=3,
                ),
                dbc.Label("max(x)", html_for="max-x", width=3),
            ],
            className="mb-1",
        ),
        dbc.Row(
            [
                dbc.Label("n blocks", html_for="n-blocks", width=6),
                dbc.Col(
                    dbc.Input(
                        id={"type": "experiment-param", "name": "n-blocks"},
                        type="number",
                        value=2,
                    ),
                ),
            ],
        ),
    ],
    body=True,
    className="mb-3",
)

psi_params = dbc.Card(
    [
        html.H4("Psychometric Model", className="mb-4"),
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
                dbc.Label("Intercept", width=6),
                dbc.Col(
                    dbc.Input(
                        id={"type": "param", "id": 0},
                        type="number",
                        value=0.0,
                    ),
                    width=6,
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Label("Slope", width=6),
                dbc.Col(
                    dbc.Input(
                        id={"type": "param", "id": 1},
                        type="number",
                        value=1.0,
                        step=0.1,
                    ),
                    width=6,
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Label("Guess Rate ", width=6),
                dbc.Col(
                    dbc.Input(
                        id={"type": "param", "id": 2},
                        type="number",
                        value=0.0,
                        step=0.1,
                    ),
                    width=6,
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Label("Lapse Rate", width=6),
                dbc.Col(
                    dbc.Input(
                        id={"type": "param", "id": 3},
                        type="number",
                        value=0.0,
                        step=0.1,
                    ),
                    width=6,
                ),
            ],
        ),
    ],
    body=True,
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
