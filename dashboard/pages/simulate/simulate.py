import dash
import dash_bootstrap_components as dbc
from dash import dcc
import plotly.express as px
import random
import pandas as pd

import psychoanalyze as pa


dash.register_page(__name__, path="/simulate")


def monkey_thresholds(mean: float, sd: float, n: int, monkey: str) -> pd.DataFrame:
    return pd.DataFrame.from_records(
        [
            {
                "Day": random.uniform(0, 1000),
                "Threshold": random.gauss(mean, sd),
                "err_y_plus": random.gauss(sd, sd / 2),
                "err_y_minus": random.gauss(sd, sd / 2),
                "Monkey": monkey,
                "Channel": random.choice([1, 2, 3, 4]),
            }
            for _ in range(n)
        ]
    )


data = pd.concat(
    [
        monkey_thresholds(mean=100, sd=5, n=50, monkey="U"),
        monkey_thresholds(mean=200, sd=10, n=75, monkey="Y"),
    ]
)


layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.InputGroup(
                            [
                                dbc.Input(type="number", value=3),
                                dbc.InputGroupText("subjects"),
                            ]
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(type="number", value=100),
                                dbc.InputGroupText("blocks per subject"),
                            ]
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(type="number", value=1000),
                                dbc.InputGroupText("trials per block"),
                            ]
                        ),
                        dbc.Label("True Threshold"),
                        dbc.InputGroup(
                            [
                                dbc.Input(type="number", value=200),
                                dbc.InputGroupText("μA"),
                            ]
                        ),
                        dbc.Label("True Slope"),
                        dbc.Input(type="number", value=0.5, step=0.01),
                        dbc.Label("True Guess Rate"),
                        dbc.Input(type="number", value=0.1, step=0.01),
                        dbc.Label("True Lapse Rate"),
                        dbc.Input(type="number", value=0.1, step=0.01),
                    ],
                    width=3,
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=px.scatter(
                            data,
                            x="Day",
                            y="Threshold",
                            error_y="err_y_plus",
                            error_y_minus="err_y_minus",
                            color="Monkey",
                            symbol="Channel",
                            template=pa.plot.template,
                            # animation_frame="Day",
                        )
                    )
                ),
            ]
        ),
    ]
)
