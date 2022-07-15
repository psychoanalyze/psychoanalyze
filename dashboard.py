import os
from dash import Dash, dcc, Output, Input  # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
import psychoanalyze as pa
import pandas as pd
import plotly.express as px  # type: ignore
from psychoanalyze.layout import controls, curves_column, diff_thresh_column

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
server = app.server

if os.path.isfile("data/blocks.csv"):
    blocks = pd.read_csv("data/blocks.csv")
else:
    if os.path.isfile("data/trials.csv"):
        trials = pd.read_csv("data/trials.csv")
        points = pa.points.from_trials(trials)
        blocks = pa.blocks.from_points(points)
    else:
        blocks = pd.DataFrame({"Dimension": []})

detection_data = pa.detection.load(blocks)[
    ["Monkey", "Threshold", "width", "lambda", "gamma"]
]
main_params = detection_data[["Monkey", "Dimension", "Threshold", "width"]].melt(
    id_vars=["Monkey"], var_name="param"
)
main_params_amp = main_params[main_params["Dimension"] == "Amp"].drop(
    columns=["Dimension"]
)
main_params_width = main_params[main_params["Dimension"] == "Width"].drop(
    columns=["Dimension"]
)
nuisance_params = detection_data[["Monkey", "gamma", "lambda"]].melt(
    id_vars=["Monkey"], var_name="param"
)
weber_data = pd.read_csv("data/weber_curves.csv")

app.layout = dbc.Container(
    dbc.Tabs(
        [
            dbc.Tab(
                dbc.Tabs(
                    [
                        dbc.Tab(
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Graph(
                                            figure=px.ecdf(
                                                main_params,
                                                color="Monkey",
                                                line_dash="param",
                                                template="plotly_white",
                                            )
                                        ),
                                    ),
                                    dbc.Col(
                                        dcc.Graph(
                                            figure=px.ecdf(
                                                nuisance_params,
                                                line_dash="param",
                                                color="Monkey",
                                                template="plotly_white",
                                            )
                                        )
                                    ),
                                ]
                            ),
                            label="Detection",
                        ),
                        dbc.Tab(
                            dcc.Graph(figure=pa.weber.plot(weber_data)),
                            label="Discrimination",
                        ),
                    ]
                ),
                label="Experiment",
            ),
            dbc.Tab(
                [
                    controls,
                    dbc.Row([curves_column, diff_thresh_column]),
                ],
                label="Simulation",
            ),
        ]
    )
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
    curves_data = pa.blocks.generate(n_trials_per_level)

    # define the range of the function
    x = pa.blocks.xrange_index(x_min, x_max)

    # fit curves with Stan
    curves_data.index = x
    fit = pa.points.fit(curves_data)
    df = pa.data.reshape_fit_results(fit, x, y)
    param_names = ["mu", "sigma", "sigma_err", "gamma", "lambda"]
    param_fits = {name: [pa.blocks.get_fit_param(fit, name)] for name in param_names}
    # plot fig
    curves_plot_data = {"y": y, "curves_df": df}
    fig = pa.plot.curves(curves_plot_data)
    diff_thresh_fig = pa.plot.difference_thresholds()
    # fetch regression data
    results = px.get_trendline_results(diff_thresh_fig)
    params = results.loc[0, "px_fit_results"].params
    weber_fraction = params[1]

    # render fit params table
    params_table = dbc.Table.from_dataframe(pd.DataFrame(param_fits))

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
