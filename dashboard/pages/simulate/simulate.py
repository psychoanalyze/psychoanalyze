import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, Output, Input, callback
import plotly.express as px
import pandas as pd
import random
from scipy.special import expit
import psychoanalyze as pa

dash.register_page(__name__, path="/simulate")


layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.InputGroup(
                            [
                                dbc.Input(id="n-trials", type="number", value=100),
                                dbc.InputGroupText("trials"),
                            ]
                        )
                    ],
                    width=3,
                ),
                dbc.Col(
                    dcc.Graph(id="psi-plot"),
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dash_table.DataTable(
                        id="trials-table",
                        style_data={"color": "black"},
                        style_header={"color": "black"},
                        page_size=10,
                    ),
                ),
                dbc.Col(
                    dash_table.DataTable(
                        id="points-table",
                        style_data={"color": "black"},
                        style_header={"color": "black"},
                        page_size=10,
                    )
                ),
            ]
        ),
    ]
)


@callback(
    [
        Output("psi-plot", "figure"),
        Output("trials-table", "data"),
        Output("points-table", "data"),
    ],
    Input("n-trials", "value"),
)
def update_figure(n_trials):
    intensity_choices = list(range(-2,3))
    intensities = [random.choice(intensity_choices) for _ in range(n_trials)]
    results = [random.random() <= expit(intensity) for intensity in intensities]
    trials = pd.DataFrame(
        {
            "Intensity": intensities,
            "Result": results,
        }
    )
    points = pa.points.from_trials(trials)
    return (
        px.scatter(
            points.reset_index(),
            x="Intensity",
            y="Hit Rate",
            size="n",
            template=pa.plot.template,
        ),
        trials.reset_index().to_dict("records"),
        points.reset_index().to_dict("records"),
    )
