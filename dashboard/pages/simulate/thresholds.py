from dash import dcc
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import random

import psychoanalyze as pa
from dashboard.layout.nav import simulate


dash.register_page(__name__)


def monkey_thresholds(mean: float, sd: float, n: int, monkey: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Day": [random.uniform(0, 1000) for _ in range(n)],
            "Threshold": [random.gauss(mean, sd) for _ in range(n)],
            "err_y_plus": [random.gauss(sd, sd / 2) for _ in range(n)],
            "err_y_minus": [random.gauss(sd, sd / 2) for _ in range(n)],
            "Monkey": [monkey] * n,
            "Channel": [random.choice([1, 2, 3, 4]) for _ in range(n)],
        }
    )


layout = dbc.Container(
    [
        simulate,
        dcc.Graph(
            figure=px.scatter(
                pd.concat(
                    [
                        monkey_thresholds(100, 5, 50, "U"),
                        monkey_thresholds(200, 10, 75, "Y"),
                    ]
                ),
                x="Day",
                y="Threshold",
                error_y="err_y_plus",
                error_y_minus="err_y_minus",
                color="Monkey",
                symbol="Channel",
                template=pa.plot.template,
            )
        ),
    ]
)
