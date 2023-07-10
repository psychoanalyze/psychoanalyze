"""Components for Dash dashboard.

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
                dbc.Label("n trials", html_for="n-trials", width=6),
                dbc.Col(
                    dbc.Input(id="n-trials", type="number", value=70),
                    width=6,
                ),
            ],
            className="mb-1",
        ),
        dbc.Row(
            [
                dbc.Label("n levels", html_for="n-levels", width=6),
                dbc.Col(
                    dbc.Input(id="n-levels", type="number", value=7),
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
        dcc.Markdown("""$f(x) = \\frac{1}{1 + e^{-k(x-x_0)}}$""", mathjax=True),
        dbc.Row(
            [
                dbc.Label("Intercept", html_for="x_0", width=6),
                dbc.Col(
                    dbc.Input(id="x_0", type="number", value=0.0),
                    width=6,
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Label("Slope", html_for="model-k", width=6),
                dbc.Col(
                    dbc.Input(id="model-k", type="number", value=1.0, step=0.1),
                    width=6,
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Label("Guess Rate ", html_for="guess-rate", width=6),
                dbc.Col(
                    dbc.Input(id="guess-rate", type="number", value=0.0, step=0.1),
                    width=6,
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Label("Lapse Rate", html_for="lapse-rate", width=6),
                dbc.Col(
                    dbc.Input(id="lapse-rate", type="number", value=0.0, step=0.1),
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
