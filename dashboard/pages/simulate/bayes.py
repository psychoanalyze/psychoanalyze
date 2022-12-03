from dash import html, dcc, dash_table, Output, Input, callback
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
from dashboard.layout.nav import simulate

import psychoanalyze as pa


dash.register_page(__name__)

index = pd.Index(np.arange(100.0, 600, 100), name="Amplitude")
x = np.arange(100.0, 600, 100)
y_observed = pa.points.psi(x, 300.0, 0.50, 0.1, 0.1)


layout = html.Div(
    [
        simulate,
        dbc.Container(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Threshold:"),
                                    dbc.Input(
                                        id="threshold",
                                        type="number",
                                        value=300,
                                        step=50,
                                    ),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Width:"),
                                    dbc.Input(
                                        id="width", type="number", value=0.5, step=0.1
                                    ),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Lapse Rate:"),
                                    dbc.Input(
                                        id="lambda", type="number", value=0.1, step=0.01
                                    ),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Guess Rate:"),
                                    dbc.Input(
                                        id="gamma", type="number", value=0.1, step=0.01
                                    ),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("n trials per level:"),
                                    dbc.Input(id="n", type="number", value=10),
                                ]
                            ),
                            dash_table.DataTable(id="points"),
                        ]
                    ),
                    dbc.Col(
                        dcc.Graph(id="block"),
                    ),
                ]
            ),
        ),
    ]
)


@callback(
    Output("block", "figure"),
    Output("points", "data"),
    Input("threshold", "value"),
    Input("width", "value"),
    Input("lambda", "value"),
    Input("gamma", "value"),
    Input("n", "value"),
)
def update_block(threshold, width, lambda_, gamma, n):
    x = np.arange(threshold - 200, threshold + 201, 100)
    y_observed = pa.points.psi(x, threshold, width, lambda_, gamma)
    block = pd.DataFrame(
        {
            "Hit Rate": y_observed,
            "n": [n] * 5,
        },
        index=pd.Index(x, name="Amplitude"),
    )
    posterior = pd.DataFrame(
        {
            "Hit Rate": [0.12, 0.19, 0.5, 0.81, 0.88],
            "error_y": [0.05] * 5,
            "error_y_minus": [0.05] * 5,
        },
        index=pd.Index(x, name="Amplitude"),
    )
    block = pa.blocks.add_posterior(block, posterior)
    block_table = block.pivot(index="Amplitude", columns="Type", values="Hit Rate")
    return (
        px.scatter(
            block.reset_index(),
            x="Amplitude",
            y="Hit Rate",
            error_y="error_y",
            error_y_minus="error_y_minus",
            symbol="Type",
            template=pa.plot.template,
        ),
        block_table.reset_index().to_dict("records"),
    )
