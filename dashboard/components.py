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
                                dbc.Checkbox(id="x_0-free", value=True),
                            ),
                            dbc.Input(
                                id="x_0",
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
                                    id="k-free",
                                ),
                            ),
                            dbc.Input(
                                id="k",
                                type="number",
                                value=1.0,
                                step=0.5,
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
                    dcc.Markdown("$\\gamma$", mathjax=True),
                    width=2,
                    align="center",
                    style={"text-align": "center"},
                ),
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                dbc.Checkbox(id="gamma-free", value=True),
                            ),
                            dbc.Input(
                                id="gamma",
                                type="number",
                                value=0.0,
                            ),
                        ],
                        size="sm",
                        class_name="p-0",
                    ),
                    width=4,
                    align="center",
                    style={"text-align": "center"},
                ),
                dbc.Col(
                    dcc.Markdown("$\\lambda$", mathjax=True),
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
                                    id="lambda-free",
                                ),
                            ),
                            dbc.Input(
                                id="lambda",
                                type="number",
                                value=1.0,
                                step=0.5,
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
            class_name="g-0",
        ),
        dbc.FormText("Uncheck boxes to fix parameters."),
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
                        options=[{"label": "Logistic (expit)", "value": "expit"}],
                        value="expit",
                        className="mb-1",
                    ),
                ),
                dbc.Col(
                    dbc.Button(
                        "Show Eqn ▾ ",
                        style={"border-radius": 3},
                        id="show-eqn",
                        class_name="btn btn-outline-info",
                        outline=True,
                    ),
                    width="auto",
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
                            id="x-min",
                            type="number",
                            disabled=True,
                        ),
                    ],
                ),
                dbc.Col(
                    [
                        dbc.FormText("n levels"),
                        dbc.Input(
                            id="n-levels",
                            type="number",
                            value=7,
                        ),
                    ],
                ),
                dbc.Col(
                    [
                        dbc.FormText("max"),
                        dbc.Input(
                            id="x-max",
                            type="number",
                            disabled=True,
                        ),
                    ],
                ),
            ],
            className="mb-1 g-0",
        ),
        dbc.Checklist(
            options=[
                {
                    "label": "Select range from model",
                    "value": "fix-range",
                },
            ],
            id="fix-range",
            switch=True,
            value=["fix-range"],
        ),
    ],
    class_name="mb-3",
)


simulation_params = dbc.Row(
    [
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.Input(
                        id={"type": "experiment-param", "name": "n-trials"},
                        type="number",
                        value=70,
                    ),
                    dbc.InputGroupText("trials"),
                ],
            ),
        ),
        dbc.Col(
            dbc.Button(
                "Resimulate",
                id="resimulate",
                style={"border-radius": 3},
            ),
            width="auto",
        ),
    ],
    className="mb-3",
)


points_table = dash_table.DataTable(
    id="points-table",
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
