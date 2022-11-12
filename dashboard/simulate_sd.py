from dash import Dash, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

import psychoanalyze as pa


app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        figure=px.line(
                            pd.DataFrame(
                                {
                                    "Fixed Pulse Width (μs)": list(
                                        range(100, 600, 100)
                                    ),
                                    "Threshold Amplitude (μA)": list(
                                        range(1000, 0, -200)
                                    ),
                                    "Monkey": ["U"] * 2 + ["Y"] * 3,
                                    "Day": [1, 1, 2, 2, 2],
                                    "error_y": [50] * 5,
                                    "error_y_minus": [50] * 5,
                                }
                            ),
                            x="Fixed Pulse Width (μs)",
                            y="Threshold Amplitude (μA)",
                            error_y="error_y",
                            error_y_minus="error_y_minus",
                            color="Monkey",
                            symbol="Day",
                            template=pa.plot.template,
                        )
                    ),
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=px.line(
                            pd.DataFrame(
                                {
                                    "Fixed Amplitude (μA)": list(range(100, 1100, 200)),
                                    "Threshold Pulse Width (μs)": list(
                                        range(600, 100, -100)
                                    ),
                                    "Monkey": ["U"] * 2 + ["Y"] * 3,
                                    "Day": [1, 1, 2, 2, 2],
                                    "error_y": [50] * 5,
                                    "error_y_minus": [50] * 5,
                                }
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
                            pd.DataFrame(
                                {
                                    "Pulse Width (μs)": list(range(50, 500, 100)),
                                    "Threshold Charge (nC)": list(range(50, 500, 100)),
                                    "Dimension": ["Amp"] * 2 + ["Width"] * 3,
                                    "Day": [1, 1, 2, 2, 2],
                                    "error_y": [50] * 5,
                                    "error_y_minus": [50] * 5,
                                }
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
                            pd.DataFrame(
                                {
                                    "Pulse Width (μs)": list(range(50, 500, 100)),
                                    "Threshold Charge (nC)": list(range(5, 50, 10)),
                                    "Dimension": ["Amp"] * 2 + ["Width"] * 3,
                                    "Day": [1, 1, 2, 2, 2],
                                    "error_y": [5] * 5,
                                    "error_y_minus": [5] * 5,
                                }
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
