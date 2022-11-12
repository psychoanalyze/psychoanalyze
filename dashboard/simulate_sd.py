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
                                    "Fixed Pulse Width (μs)": [1, 2, 3, 4, 5],
                                    "Threshold Amplitude (μA)": [5, 4, 3, 2, 1],
                                    "Monkey": ["U"] * 2 + ["Y"] * 3,
                                    "Day": [1, 1, 2, 2, 2],
                                    "error_y": [0.5, 0.5, 0.5, 0.5, 0.5],
                                    "error_y_minus": [0.5, 0.5, 0.5, 0.5, 0.5],
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
                                    "Fixed Amplitude (μA)": [1, 2, 3, 4, 5],
                                    "Threshold Pulse Width (μs)": [5, 4, 3, 2, 1],
                                    "Monkey": ["U"] * 2 + ["Y"] * 3,
                                    "Day": [1, 1, 2, 2, 2],
                                    "error_y": [0.5, 0.5, 0.5, 0.5, 0.5],
                                    "error_y_minus": [0.5, 0.5, 0.5, 0.5, 0.5],
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
                                    "Pulse Width (μs)": [1, 2, 3, 4, 5],
                                    "Threshold Charge (nC)": [1, 2, 3, 4, 5],
                                    "Dimension": ["Amp"] * 2 + ["Width"] * 3,
                                    "Day": [1, 1, 2, 2, 2],
                                    "error_y": [0.5, 0.5, 0.5, 0.5, 0.5],
                                    "error_y_minus": [0.5, 0.5, 0.5, 0.5, 0.5],
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
                                    "Pulse Width (μs)": [1, 2, 3, 4, 5],
                                    "Threshold Charge (nC)": [1, 2, 3, 4, 5],
                                    "Dimension": ["Amp"] * 2 + ["Width"] * 3,
                                    "Day": [1, 1, 2, 2, 2],
                                    "error_y": [0.5, 0.5, 0.5, 0.5, 0.5],
                                    "error_y_minus": [0.5, 0.5, 0.5, 0.5, 0.5],
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
