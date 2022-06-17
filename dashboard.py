from dash import Dash, dcc, Output, Input
import dash_bootstrap_components as dbc
import psychoanalyze as pa
import pandas as pd
from psychoanalyze.layout import input_group
import plotly.express as px

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
        dcc.Graph(figure=pa.plot.difference_thresholds()),
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
def generate_data(n_trials_per_level, x_min, x_max, y):
    # generate curves with n trials per level
    curves_data = pa.curve.generate(n_trials_per_level)

    # define the range of the function
    x = pa.curve.xrange_index(x_min, x_max)

    # fit curves with Stan
    curves_data_w_posterior = pa.curve.prep_psych_curve(
        curves_data=curves_data, x=x, y=y
    )

    # plot fig
    curves_plot_data = {"y": y, "curves_df": curves_data_w_posterior}
    fig = pa.plot.curves(curves_plot_data)

    # render table
    curve_table = dbc.Table.from_dataframe(pd.DataFrame())
    return (
        fig,
        curve_table.children,
    )


if __name__ == "__main__":
    app.run_server(debug=True)
