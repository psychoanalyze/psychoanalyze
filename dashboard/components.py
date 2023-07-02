import dash_bootstrap_components as dbc
from dash import html

experiment_params = html.Div(
    [
        html.H4("Experimental Design"),
        dbc.InputGroup(
            [
                dbc.Input(id="n-trials", type="number", value=50),
                dbc.InputGroupText("trials per block"),
            ]
        ),
        dbc.InputGroup(
            [
                dbc.Input(id="n-subjects", type="number", value=2),
                dbc.InputGroupText("subjects"),
            ],
            class_name="mb-4",
        ),
    ]
)
