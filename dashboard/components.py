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
from dash import html

experiment_params = html.Div(
    [
        html.H4("Experimental Design"),
        dbc.InputGroup(
            [
                dbc.Input(id="n-trials-per-level", type="number", value=10),
                dbc.InputGroupText("trials per level"),
            ],
        ),
        dbc.InputGroup(
            [
                dbc.Input(id="n-levels", type="number", value=7),
                dbc.InputGroupText("n levels"),
            ],
            class_name="mb-4",
        ),
    ],
)
