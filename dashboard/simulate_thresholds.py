from dash import Dash, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import random

import psychoanalyze as pa


app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])


def monkey_thresholds(mean: float, sd: float, n: int, monkey: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Day": [random.uniform(0, 1000) for _ in range(n)],
            "Threshold": [random.gauss(mean, sd) for _ in range(n)],
            "Monkey": [monkey] * n,
        }
    )


app.layout = dbc.Container(
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
            color="Monkey",
            template=pa.plot.template,
        )
    )
)

if __name__ == "__main__":
    app.run_server(debug=True, port=8053)
