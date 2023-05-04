import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, Output, Input, callback
import plotly.express as px
import pandas as pd
import random
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
            ]
        ),
        dbc.Row(
            [
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
                        sort_by=[{"column_id": "Trial", "direction": "desc"}],
                    ),
                ),
                dbc.Col(
                    dash_table.DataTable(
                        id="points-table",
                        style_data={"color": "black"},
                        style_header={"color": "black"},
                    )
                ),
            ]
        ),
    ]
)


@callback(
    [
        Output("psi-plot", "figure"),
        Output("points-table", "data"),
        Output("trials-table", "data"),
    ],
    Input("n-trials", "value"),
)
def update_figure(n_trials):
    p_x = {-1: 0.25, 0: 0.5, 1: 0.75}
    intensities = [random.choice([-1, 0, 1]) for _ in range(n_trials)]
    results = [random.random() <= p_x[intensity] for intensity in intensities]
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
