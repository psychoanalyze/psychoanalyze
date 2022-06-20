from dash import Dash, dcc, Output, Input, html
import dash_bootstrap_components as dbc
import psychoanalyze as pa
import pandas as pd
import plotly.express as px
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
        dbc.Table(id="fit-params"),
        dbc.Table(id="curve-data"),
    ]
)

diff_thresh_column = dbc.Col(
    [
        dcc.Graph(id="difference-thresholds"),
        html.P(id="weber-fraction"),
    ]
)

app.layout = dbc.Container(
    [
        dbc.Row(session_inputs + param_inputs),
        dbc.Row(x_min_input + x_max_input),
        dbc.Row([curves_column, diff_thresh_column]),
    ]
)


@app.callback(
    [
        Output("curves", "figure"),
        Output("curve-data", "children"),
        Output("weber-fraction", "children"),
        Output("difference-thresholds", "figure"),
        Output("fit-params", "children"),
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
    curves_data.index = x
    fit = pa.curve.fit(curves_data)
    df = pa.data.reshape_fit_results(fit, x, y)
    mu = pa.curve.get_fit_param(fit, "mu")
    sigma = pa.curve.get_fit_param(fit, "sigma")
    sigma_err = pa.curve.get_fit_param(fit, "sigma_err")
    gamma = pa.curve.get_fit_param(fit, "gamma")
    lambda_ = pa.curve.get_fit_param(fit, "lambda")

    # plot fig
    curves_plot_data = {"y": y, "curves_df": df}
    fig = pa.plot.curves(curves_plot_data)
    diff_thresh_fig = pa.plot.difference_thresholds()
    # fetch regression data
    results = px.get_trendline_results(diff_thresh_fig)
    params = results.loc[0, "px_fit_results"].params
    weber_fraction = params[1]

    # render fit params table
    params_table = dbc.Table.from_dataframe(
        pd.DataFrame(
            {
                "mu": [mu],
                "sigma": [sigma],
                "sigma_err": sigma_err,
                "gamma": gamma,
                "lambda": lambda_,
            }
        )
    )

    # render points table
    curve_table = dbc.Table.from_dataframe(curves_plot_data["curves_df"])
    return (
        fig,
        curve_table.children,
        f"Weber Fraction: {weber_fraction}",
        diff_thresh_fig,
        params_table.children,
    )


if __name__ == "__main__":
    app.run_server(debug=True)
