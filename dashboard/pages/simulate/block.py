import dash

from dash import html, dcc, dash_table, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dashboard.layout.nav import simulate

import psychoanalyze as pa

dash.register_page(__name__)

moc_param_form = dbc.Card(
    [
        html.H4("MOC Params", className="card-title"),
        html.Div(
            [
                dbc.Label("# of total trials"),
                dbc.Input(id="n", type="number", value=200),
            ]
        ),
        html.Div(
            [
                dbc.Label("Minimum stimulus intensity"),
                dbc.Input(id="min-x", type="number", value=-3),
            ]
        ),
        html.Div(
            [
                dbc.Label("Maximum stmulus intensity"),
                dbc.Input(id="max-x", type="number", value=3),
            ]
        ),
        html.Div(
            [
                dbc.Label("# of stimulus levels"),
                dbc.Input(id="n-stim-levels", type="number", value=7),
            ]
        ),
    ]
)

layout = dbc.Container(
    [
        simulate,
        dbc.Row(
            [
                dbc.Col(moc_param_form, width=6),
                dbc.Col(
                    [
                        dcc.Graph(id="psychometric-upload"),
                    ],
                    width=6,
                ),
            ],
            align="center",
        ),
        dbc.Row([dbc.Col(dash_table.DataTable(id="points-upload"))]),
    ]
)


@dash.callback(
    Output("points-upload", "data"),
    Output("psychometric-upload", "figure"),
    Input("n", "value"),
)
def summarize_trials(n):
    p_x = pd.Series(
        [0.05, 0.10, 0.15, 0.5, 0.85, 0.90, 0.95],
        index=pd.Index([-3, -2, -1, 0, 1, 2, 3], name="Stimulus Magnitude"),
    )
    trials = pd.DataFrame.from_records(pa.trials.results(n, p_x))
    points = (
        trials.groupby("Stimulus Magnitude")["Result"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(columns={"sum": "Hits", "count": "n"})
    )
    points["Hit Rate"] = points["Hits"] / points["n"]
    trials["Result"] = trials["Result"].apply(lambda x: pa.trials.codes[x])
    return (
        points.to_dict("records"),
        pa.plot.combine_figs(
            px.scatter(
                points,
                x="Stimulus Magnitude",
                y="Hit Rate",
                size="n",
                template=pa.plot.template,
            ),
            pa.plot.psychometric(
                {
                    "Threshold": 0,
                    "width": 1,
                    "gamma": 0.1,
                    "lambda": 0.1,
                }
            ),
        ),
    )
