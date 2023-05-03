import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
import pandas as pd
import psychoanalyze as pa


dash.register_page(__name__, path="/simulate")

trials = pd.read_csv("data/test/trials.csv")
points = pd.read_csv("data/test/points.csv")
# points = points.reset_index().rename(columns={"Outcome": "Hit Rate"})
intensity_levels = [0, 1, 2]
intensity_index = pd.Index(intensity_levels, name="Intensity")
after_trial_1 = pd.Series([0, None, None], name="Hit Rate", index=intensity_index)
after_trial_2 = pd.Series([0, 1, None], name="Hit Rate", index=intensity_index)
after_trial_3 = pd.Series([0, 1, 1], name="Hit Rate", index=intensity_index)
after_trial_4 = pd.Series([0, 0.5, 1], name="Hit Rate", index=intensity_index)
df = pd.concat(
    [after_trial_1, after_trial_2, after_trial_3, after_trial_4],
    keys=[0, 1, 2, 3],
    names=["Trial", "Intensity"],
).reset_index()

layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.InputGroup(
                            [
                                dbc.Input(id="n-trials", type="number", value=3),
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
                        dcc.Graph(
                            id="psi-plot",
                            figure=pa.plot.psi_animation(df),
                        ),
                        html.Br(),
                        dash_table.DataTable(
                            data=points.to_dict("records"),
                            id="trials-table",
                            style_data={"color": "black"},
                            style_header={"color": "black"},
                        ),
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
                            Ψ(x)=.1+.8\\int_{-\\infty}^x\\exp(-t^2/2)\\,dt
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


# @callback(
#     [Output("psi-plot", "figure"), Output("trials-table", "data")],
#     Input("n-trials", "value"),
# )
# def update_figure(n_trials):
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
