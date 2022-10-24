from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc


layout = dbc.Container(
    [
        html.H1("PsychoAnalyze"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.RadioItems(
                            options=[
                                {"label": monkey, "value": monkey}
                                for monkey in ["U", "Y", "Z"]
                            ],
                            value="Z",
                            inline=True,
                            id="monkey-select",
                        ),
                        dbc.RadioItems(
                            options=[
                                {"label": dim, "value": dim} for dim in ["Amp", "PW"]
                            ],
                            value="Amp",
                            inline=True,
                            id="dim-select",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.P(id="day-display"),
                        dcc.Slider(
                            step=None,
                            marks={"": ""},
                            id="day-select",
                        ),
                    ],
                    width=8,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button(
                            "Fit Curve",
                            id="fit-button",
                            n_clicks=0,
                        ),
                        html.Table(
                            children=[
                                html.Tr(
                                    [
                                        html.Th(param)
                                        for param in [
                                            "param",
                                            "MAP fit",
                                            "err+",
                                            "err-",
                                        ]
                                    ]
                                )
                            ]
                            + [
                                html.Tr(
                                    [
                                        html.Td(param),
                                        html.Td(id=f"{param}-value"),
                                        html.Td(id=f"{param}-err+"),
                                        html.Td(id=f"{param}-err-"),
                                    ]
                                )
                                for param in [
                                    "Threshold",
                                    "width",
                                    "gamma",
                                    "lambda",
                                ]
                            ],
                            id="fit-table",
                        ),
                    ],
                    align="center",
                ),
                dbc.Col(
                    dash_table.DataTable(
                        id="ref-stimulus-table",
                        row_selectable="single",
                        selected_rows=[0],
                    ),
                ),
                dbc.Col(dcc.Graph(id="psychometric-fig")),
            ],
            justify="center",
        ),
    ]
)
