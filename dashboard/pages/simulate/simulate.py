import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
import random

import psychoanalyze as pa


dash.register_page(__name__, path="/simulate")


def thresholds(mean: float, sd: float, n: int) -> pd.DataFrame:
    return pd.DataFrame.from_records(
        [
            {
                "TrialID": i,
                "TrialType": random.choice(["Catch", "Test"]),
                "Intensity": random.choice([-3, -2, -1, 0, 1, 2, 3]),
            }
            for i in range(n)
        ]
    )


data = thresholds(mean=200, sd=10, n=1)

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.InputGroup(
                            [
                                dbc.Input(type="number", value=1),
                                dbc.InputGroupText("trials"),
                            ]
                        ),
                        html.H2("Simulation parameters"),
                        dcc.Markdown("Simulated threshold *l*"),
                        dbc.InputGroup(
                            [
                                dbc.Input(type="number", value=0),
                                dbc.InputGroupText("μA"),
                            ]
                        ),
                        dcc.Markdown("Simulated slope *m*"),
                        dbc.Input(type="number", value=1, step=0.01),
                        dcc.Markdown("Simulated guess rate *γ*"),
                        dbc.Input(type="number", value=0.1, step=0.01),
                        dcc.Markdown("Simulated lapse rate *λ*"),
                        dbc.Input(type="number", value=0.1, step=0.01),
                        html.Br(),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        dcc.Graph(figure=px.scatter(template=pa.plot.template)),
                        dash_table.DataTable(data.to_dict("records")),
                        dcc.Markdown(
                            """
                            $$
                            Ψ(x;l,m,γ,λ)=γ+(1-γ-λ)F(x;l,m)
                            $$
                            """,
                            mathjax=True,
                        ),
                        dcc.Markdown(
                            """
                            $$
                            Ψ(x)=.1+(1-.1-.1)F(x)
                            $$
                            """,
                            mathjax=True,
                        ),
                        # ( 1+\exp( \frac{x-μ}{σ\sqrt{2}} ) )
                        # \frac{ ( 1+\exp( \frac{x-μ}{σ\sqrt{2}} ) ) }{2}
                        dcc.Markdown(
                            """
                            $$
                            Ψ(x)=.1+.8\\frac{  1+\\exp( \\frac{x-0}{1\\sqrt{2}} )) }{2}
                            $$
                            """,
                            mathjax=True,
                        ),
                        dcc.Markdown(
                            """
                            $$
                            Ψ(x)=.5 + \\exp(\\frac{x}{\\sqrt{2}})/2
                            $$
                            """,
                            mathjax=True,
                        ),
                        dcc.Markdown(
                            """
                            $$
                            Ψ(x)=\\frac{1 + \\exp(\\frac{x}{\\sqrt{2}})}{2}
                            $$
                            """,
                            mathjax=True,
                        ),
                    ]
                ),
            ]
        ),
    ]
)


# @dash.callback(
#     Output()
# )
