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
from dash import dcc, html

experiment_params = html.Div(
    [
        html.H4("Experimental Design"),
        dbc.Row(
            [
                dbc.Label("trials per level", html_for="n-trials-per-level", width=6),
                dbc.Col(
                    dbc.Input(id="n-trials-per-level", type="number", value=10),
                    width=6,
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Label("n levels", html_for="n-levels", width=6),
                dbc.Col(
                    dbc.Input(id="n-levels", type="number", value=7),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
    ],
)

psi_params = html.Div(
    [
        html.H4("Psychometric Function"),
        dcc.Dropdown(
            id="f",
            options=[{"label": "Logistic (expit)", "value": "expit"}],
            value="expit",
            className="mb-3",
        ),
        dcc.Markdown("""$f(x) = \\frac{1}{1 + exp(-k(x-x_0))}$""", mathjax=True),
        dbc.Row(
            [
                dbc.Label("Intercept", html_for="x_0", width=6),
                dbc.Col(
                    dbc.Input(id="x_0", type="number", value=50.0, step=0.1),
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
                dbc.Label("Guess Rate ", html_for="gamma", width=6),
                dbc.Col(
                    dbc.Input(id="gamma", type="number", value=0.0, step=0.1),
                    width=6,
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Label("Lapse Rate", html_for="lambda", width=6),
                dbc.Col(
                    dbc.Input(id="lambda", type="number", value=0.0, step=0.1),
                    width=6,
                ),
            ],
        ),
    ],
)
