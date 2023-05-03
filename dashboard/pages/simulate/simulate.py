import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, Output, Input, callback
import plotly.express as px
import pandas as pd
from random import random

dash.register_page(__name__, path="/simulate")


layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.InputGroup(
                            [
                                dbc.Input(id="n-trials", type="number", value=10),
                                dbc.InputGroupText("trials"),
                            ]
                        )
                        # html.H2("Simulation parameters"),
                        # dcc.Markdown("Simulated threshold *l*"),
                        # dbc.InputGroup(
                        #     [
                        #         dbc.Input(type="number", value=0),
                        #         dbc.InputGroupText("μA"),
                        #     ]
                        # ),
                        # dcc.Markdown("Simulated slope *m*"),
                        # dbc.Input(type="number", value=1, step=0.01),
                        # dcc.Markdown("Simulated guess rate *γ*"),
                        # dbc.Input(type="number", value=0.1, step=0.01),
                        # dcc.Markdown("Simulated lapse rate *λ*"),
                        # dbc.Input(type="number", value=0.1, step=0.01),
                        # html.Br(),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        # dcc.Graph(
                        #     id="psi-plot",
                        #     # figure=pa.plot.psi_animation(df),
                        #     figure=px.scatter(s),
                        # ),
                        html.Br(),
                        dash_table.DataTable(
                            id="points-table",
                            style_data={"color": "black"},
                            style_header={"color": "black"},
                            page_size=10,
                            sort_by=[{"column_id": "Trial", "direction": "desc"}],
                        ),
                        # dcc.Markdown(
                        #     """
                        #     $$
                        #     Ψ(x;l,m,γ,λ)=γ+(1-γ-λ)F(x;l,m)
                        #     $$
                        #     """,
                        #     mathjax=True,
                        # ),
                        # dcc.Markdown(
                        #     """
                        #     $$
                        #     Ψ(x)=.1+(1-.1-.1)F(x)
                        #     $$
                        #     """,
                        #     mathjax=True,
                        # ),
                        # ( 1+\exp( \frac{x-μ}{σ\sqrt{2}} ) )
                        # \frac{ ( 1+\exp( \frac{x-μ}{σ\sqrt{2}} ) ) }{2}
                        # dcc.Markdown(
                        #     """
                        #     $$
                        #     Ψ(x)=.1+.8\\int_{-\\infty}^x\\exp(-t^2/2)\\,dt
                        #     $$
                        #     """,
                        #     mathjax=True,
                        # ),
                        # dcc.Markdown(
                        #     """
                        #     $$
                        #     Ψ(x)=.5 + \\exp(\\frac{x}{\\sqrt{2}})/2
                        #     $$
                        #     """,
                        #     mathjax=True,
                        # ),
                        # dcc.Markdown(
                        #     """
                        #     $$
                        #     Ψ(x)=\\frac{1 + \\exp(\\frac{x}{\\sqrt{2}})}{2}
                        #     $$
                        #     """,
                        #     mathjax=True,
                        # ),
                    ]
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id="psi-plot"),
                ),
                dbc.Col(dcc.Graph(id="trial-convergence")),
            ]
        ),
    ]
)


@callback(
    # Output("psi-plot", "figure"),
    [
        Output("points-table", "data"),
        Output("psi-plot", "figure"),
        Output("trial-convergence", "figure"),
    ],
    Input("n-trials", "value"),
)
def update_figure(n_trials):
    results = [random() <= 0.5 for _ in range(n_trials)]
    results1 = [random() <= 0.75 for _ in range(n_trials)]
    results2 = [random() <= 0.25 for _ in range(n_trials)]
    points_history = (
        [
            {
                "Trial": i,
                "Result": results[i],
                "Intensity": 0,
                "Hits": sum(results[: i + 1]),
                "Hit Rate": sum(results[: i + 1]) / (i + 1),
                "n": i + 1,
            }
            for i in range(n_trials)
        ]
        + [
            {
                "Trial": i,
                "Result": results1[i],
                "Intensity": 1,
                "Hits": sum(results1[: i + 1]),
                "Hit Rate": sum(results1[: i + 1]) / (i + 1),
                "n": i + 1,
            }
            for i in range(n_trials)
        ]
        + [
            {
                "Trial": i,
                "Result": results2[i],
                "Intensity": -1,
                "Hits": sum(results2[: i + 1]),
                "Hit Rate": sum(results2[: i + 1]) / (i + 1),
                "n": i + 1,
            }
            for i in range(n_trials)
        ]
    )

    return (
        points_history,
        px.line(
            pd.DataFrame.from_records(points_history),
            x="Trial",
            y="Hit Rate",
            color="Intensity",
        ),
        px.scatter(
            pd.DataFrame.from_records(points_history),
            x="Intensity",
            y="Hit Rate",
            animation_group="Intensity",
            animation_frame="Trial",
        ),
    )


#     _trials = trials.iloc[:n_trials]
#     points = _trials.groupby("Intensity")[["Outcome"]].sum() / len(_trials)
#     points = points.reset_index().rename(columns={"Outcome": "Hit Rate"})
#     return (
#         px.line(
#             points.reset_index(),
#             x="Intensity",
#             y="Hit Rate",
#             # color="Source",
#             markers=True,
#             template=pa.plot.template,
#         ),
#         points.to_dict("records"),
#     )
