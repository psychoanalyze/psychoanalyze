from typing import List
from dash import Dash, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

import psychoanalyze as pa


def sd_data_inverse(
    x: List[float], xlabel: str, y: List[float], ylabel: str
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            xlabel: x,
            ylabel: y,
            "Monkey": ["U"] * 2 + ["Y"] * 3,
            "Day": [1, 1, 2, 2, 2],
            "error_y": [50] * 5,
            "error_y_minus": [50] * 5,
        }
    )


def sd_data_linear(
    x: List[float], xlabel: str, y: List[float], ylabel: str
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            xlabel: x,
            ylabel: y,
            "Monkey": ["U"] * 2 + ["Y"] * 3,
            "Day": [1, 1, 2, 2, 2],
            "Dimension": ["Amp"] * 2 + ["Width"] * 3,
            "error_y": [50] * 5,
            "error_y_minus": [50] * 5,
        }
    )


app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        figure=px.line(
                            sd_data_inverse(
                                x=list(range(100, 600, 100)),
                                xlabel="Fixed Pulse Width (μs)",
                                y=list(range(1000, 0, -200)),
                                ylabel="Threshold Amplitude (μA)",
                            ),
                            x="Fixed Pulse Width (μs)",
                            y="Threshold Amplitude (μA)",
                            error_y="error_y",
                            error_y_minus="error_y_minus",
                            color="Monkey",
                            symbol="Day",
                            template=pa.plot.template,
                        ),
                    )
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=px.line(
                            sd_data_inverse(
                                x=list(range(100, 1100, 200)),
                                xlabel="Fixed Amplitude (μA)",
                                y=list(range(600, 100, -100)),
                                ylabel="Threshold Pulse Width (μs)",
                            ),
                            x="Fixed Amplitude (μA)",
                            y="Threshold Pulse Width (μs)",
                            error_y="error_y",
                            error_y_minus="error_y_minus",
                            color="Monkey",
                            symbol="Day",
                            template=pa.plot.template,
                        )
                    ),
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        figure=px.line(
                            sd_data_linear(
                                x=list(range(100, 600, 100)),
                                xlabel="Pulse Width (μs)",
                                y=list(range(100, 600, 100)),
                                ylabel="Threshold Charge (nC)",
                            ),
                            x="Pulse Width (μs)",
                            y="Threshold Charge (nC)",
                            error_y="error_y",
                            error_y_minus="error_y_minus",
                            line_dash="Dimension",
                            symbol="Day",
                            template=pa.plot.template,
                        )
                    ),
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=px.line(
                            sd_data_linear(
                                x=list(range(100, 600, 100)),
                                xlabel="Pulse Width (μs)",
                                y=list(range(100, 600, 100)),
                                ylabel="Threshold Charge (nC)",
                            ),
                            x="Pulse Width (μs)",
                            y="Threshold Charge (nC)",
                            error_y="error_y",
                            error_y_minus="error_y_minus",
                            line_dash="Dimension",
                            symbol="Day",
                            template=pa.plot.template,
                        )
                    ),
                ),
            ]
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True, port=8054)
