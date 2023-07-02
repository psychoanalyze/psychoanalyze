import dash_bootstrap_components as dbc
from dash import html

experiment_params = html.Div(
    [
        html.H4("Experimental Design"),
        dbc.InputGroup(
            [
                dbc.Input(id="n-trials-per-level", type="number", value=10),
                dbc.InputGroupText("trials per level"),
            ]
        ),
        dbc.InputGroup(
            [
                dbc.Input(id="n-levels", type="number", value=7),
                dbc.InputGroupText("n levels"),
            ],
            class_name="mb-4",
        ),
    ]
)
