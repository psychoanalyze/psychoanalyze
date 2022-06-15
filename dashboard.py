from dash import Dash, dcc, Output, Input
import dash_bootstrap_components as dbc
import psychoanalyze as pa
import pandas as pd
from psychoanalyze.layout import input_group

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])


session_inputs = input_group("session")
param_inputs = input_group("param")
x_min_input = input_group("x_min")
x_max_input = input_group("x_max")

threshold_column = dbc.Col(
    [
        dcc.Graph(id="time-thresholds"),
        dbc.Table(id="thresh-data"),
    ]
)

curves_column = dbc.Col(
    [
        dcc.RadioItems(
            [
                {"label": "sigmoid", "value": "p"},
                {"label": "linear", "value": "alpha"},
            ],
            "p",
            id="y",
        ),
        dcc.Graph(id="curves"),
        dbc.Table(id="curve-data"),
    ]
)

app.layout = dbc.Container(
    [
        dbc.Row(session_inputs + param_inputs),
        dbc.Row(x_min_input + x_max_input),
        dbc.Row([curves_column]),
    ]
)


@app.callback(
    [
        Output("curves", "figure"),
        Output("curve-data", "children"),
    ],
    [
        Input("trials", "value"),
        Input("x_min", "value"),
        Input("x_max", "value"),
        Input("y", "value"),
    ],
)
def generate_data(n_trials, x_min, x_max, y):
    curves_data = pa.curve.generate(n_trials)
    x = pa.curve.xrange_index(x_max, x_min)
    curves_data_w_posterior = pa.curve.prep_psych_curve(
        curves_data=curves_data, x_min=x_min, x_max=x_max, x=x, y=y
    )
    fig = pa.plot.curves(curves_data_w_posterior, y)
    curve_table = dbc.Table.from_dataframe(curves_data_w_posterior.reset_index())
    return (
        fig,
        curve_table.children,
    )


if __name__ == "__main__":
    app.run_server(debug=True)
