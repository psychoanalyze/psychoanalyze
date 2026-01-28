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
from dash import dash_table, dcc

model_params = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Markdown("$x_0$", mathjax=True),
                    width=2,
                    style={"text-align": "center"},
                    align="center",
                ),
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                dbc.Checkbox(
                                    id={"type": "free", "name": "x_0"},
                                    value=True,
                                ),
                            ),
                            dbc.Input(
                                id={"type": "param", "name": "x_0"},
                                type="number",
                                value=0.0,
                            ),
                        ],
                        size="sm",
                        class_name="p-0",
                    ),
                    width=4,
                    style={"text-align": "center"},
                    align="center",
                ),
                dbc.Col(
                    dcc.Markdown("$k$", mathjax=True),
                    width=2,
                    align="center",
                    style={"text-align": "center"},
                ),
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                dbc.Checkbox(
                                    value=True,
                                    id={"type": "free", "name": "k"},
                                ),
                            ),
                            dbc.Input(
                                id={"type": "param", "name": "k"},
                                type="number",
                                value=1.0,
                                step=0.1,
                            ),
                        ],
                        size="sm",
                        class_name="p-0",
                    ),
                    width=4,
                    align="center",
                    style={"text-align": "center"},
                ),
            ],
            class_name="g-0 mb-0",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="preset",
                        placeholder="Presets",
                        options=[
                            {
                                "label": "Standard",
                                "value": "standard",
                            },
                            {
                                "label": "Non Standard",
                                "value": "non-standard",
                            },
                        ],
                    ),
                    width=7,
                    class_name="mt-2",
                ),
            ],
            justify="center",
        ),
    ],
    className="mb-2",
)

link_function = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="f",
                        options=[{"label": "Logistic", "value": "expit"}],
                        value="expit",
                        className="mb-1",
                    ),
                ),
                dbc.Col(
                    dbc.Button(
                        style={"border-radius": 3},
                        id="show-eqn",
                        class_name="btn btn-outline-info",
                        outline=True,
                    ),
                    width=6,
                ),
            ],
        ),
        dbc.Collapse(
            dcc.Markdown(
                """
                    $$
                    F(x) = \\frac{1}{1 + e^{-k(x-x_0)}}
                    $$""",
                mathjax=True,
            ),
            is_open=False,
            id="F-eqn",
        ),
    ],
    className="mb-2",
)

stimulus_params = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.FormText("min"),
                        dbc.Input(
                            id={"type": "x-param", "name": "min"},
                            type="number",
                            disabled=True,
                        ),
                    ],
                ),
                dbc.Col(
                    [
                        dbc.FormText("n levels"),
                        dbc.Input(
                            id={"type": "n-param", "name": "n-levels"},
                            type="number",
                            value=7,
                        ),
                    ],
                ),
                dbc.Col(
                    [
                        dbc.FormText("max"),
                        dbc.Input(
                            id={"type": "x-param", "name": "max"},
                            type="number",
                            disabled=True,
                        ),
                    ],
                ),
            ],
            className="mb-1 g-0",
        ),
    ],
    class_name="mb-3",
)


simulation_params = dbc.Col(
    [
        dbc.InputGroup(
            [
                dbc.Input(
                    id={"type": "n-param", "name": "n-trials"},
                    type="number",
                    value=100,
                ),
                dbc.InputGroupText("trials per block"),
            ],
        ),
        dbc.InputGroup(
            [
                dbc.Input(
                    id={"type": "n-param", "name": "n-blocks"},
                    type="number",
                    value=5,
                ),
                dbc.InputGroupText("blocks"),
            ],
        ),
    ],
    width="9",
)

points_table = dash_table.DataTable(
    id="points-table",
    columns=[
        {
            "name": "Block",
            "id": "Block",
            "type": "numeric",
        },
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
            "name": "n trials",
            "id": "n trials",
            "type": "numeric",
        },
        {
            "name": "p(x)",
            "id": "p(x)",
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
            "name": "Hit Rate",
            "id": "Hit Rate",
            "type": "numeric",
            "format": dash_table.Format.Format(
                precision=2,
                scheme=dash_table.Format.Scheme.fixed,
            ),
        },
    ],
    style_data={"color": "black"},
    style_header={"color": "black"},
    page_action="native",
)

blocks_table = dash_table.DataTable(
    id="blocks-table",
    row_selectable="multi",
    selected_rows=[0, 2],
    columns=[
        {
            "name": "Block",
            "id": "Block",
            "type": "numeric",
        },
        {
            "name": "intercept β₀",
            "id": "intercept",
            "type": "numeric",
            "format": dash_table.Format.Format(
                precision=2,
                scheme=dash_table.Format.Scheme.fixed,
            ),
        },
        {
            "name": "slope β₁",
            "id": "slope",
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
