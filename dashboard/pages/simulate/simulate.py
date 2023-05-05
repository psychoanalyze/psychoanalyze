import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, callback
import plotly.express as px
import pandas as pd
from sklearn.linear_model import LogisticRegression
import numpy as np
import psychoanalyze as pa

dash.register_page(__name__, path="/simulate")


component_column = dbc.Col(
    [
        dbc.InputGroup(
            [
                dbc.Input(id="n-trials", type="number", value=100),
                dbc.InputGroupText("trials/block"),
            ]
        ),
        dbc.InputGroup(
            [
                dbc.Input(id="n-blocks", type="number", value=2),
                dbc.InputGroupText("blocks"),
            ]
        ),
        html.H3("Intensity Levels"),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Min"),
                dbc.Input(id="min-intensity", type="number", value=-4),
                dbc.Input(id="max-intensity", type="number", value=4),
                dbc.InputGroupText("Max"),
            ]
        ),
        html.H3("Model Parameters"),
        html.H4("Logistic Regression"),
        dbc.InputGroup(
            [
                dbc.InputGroupText("k"),
                dbc.Input(id="model-k", type="number", value=1, step=0.1),
            ]
        ),
    ],
    width=3,
)

layout = html.Div(
    [
        dbc.Row(
            [
                component_column,
                dbc.Col(
                    [
                        dcc.Graph(id="intensity-histo"),
                        dcc.Graph(id="psi-plot"),
                        dcc.Graph(id="blocks-plot"),
                    ]
                ),
            ]
        ),
    ]
)


@callback(
    [
        Output("intensity-histo", "figure"),
        Output("psi-plot", "figure"),
        Output("blocks-plot", "figure"),
    ],
    [
        Input("n-trials", "value"),
        Input("min-intensity", "value"),
        Input("max-intensity", "value"),
        Input("model-k", "value"),
        Input("n-blocks", "value"),
    ],
)
def update_figure(n_trials, min_intensity, max_intensity, k, n_blocks):
    intensity_choices = np.array(list(range(min_intensity, max_intensity + 1)))

    hit_rates = pd.Series(
        pa.blocks.model_hit_rates(intensity_choices, k),
        name="Hit Rate",
        index=pd.Index(intensity_choices, name="Intensity"),
    )
    trials1 = pa.blocks.moc_sample(intensity_choices, n_trials, k)
    fits1 = LogisticRegression(fit_intercept=False).fit(
        trials1[["Intensity"]], trials1["Result"]
    )
    observed_points1 = pa.points.from_trials(trials1)[["Hit Rate", "n"]]
    predictions1 = pd.DataFrame(
        {
            "Hit Rate": fits1.predict_proba(
                pd.DataFrame({"Intensity": intensity_choices})
            )[:, 1],
        },
        index=pd.Index(intensity_choices, name="Intensity"),
    )
    trials2 = pa.blocks.moc_sample(intensity_choices, n_trials, k)
    fits2 = LogisticRegression(fit_intercept=False).fit(
        trials2[["Intensity"]], trials2["Result"]
    )
    observed_points2 = pa.points.from_trials(trials2)[["Hit Rate", "n"]]
    predictions2 = pd.DataFrame(
        {
            "Hit Rate": fits2.predict_proba(
                pd.DataFrame({"Intensity": intensity_choices})
            )[:, 1],
        },
        index=pd.Index(intensity_choices, name="Intensity"),
    )
    trials = pd.concat([trials1, trials2], keys=["1", "2"], names=["Block"])
    observed = pd.concat(
        [observed_points1, observed_points2], keys=["1", "2"], names=["Block"]
    )
    predictions = pd.concat(
        [predictions1, predictions2], keys=["1", "2"], names=["Block"]
    )
    hit_rates = hit_rates.reset_index()
    hit_rates["Block"] = "Prior"
    hit_rates = hit_rates.set_index(["Block", "Intensity"])
    points = pd.concat(
        [
            observed,
            predictions,
            hit_rates,
        ],
        keys=["Observed", "Posterior Prediction", "Prediction"],
        names=["Source"],
    )
    return (
        px.histogram(
            trials.reset_index(),
            x="Intensity",
            color="Block",
            barmode="group",
            template=pa.plot.template,
        ),
        px.scatter(
            points.reset_index(),
            x="Intensity",
            y="Hit Rate",
            color="Block",
            symbol="Source",
            template=pa.plot.template,
        ),
        px.scatter(
            {"k": [fits1.coef_[0][0], fits2.coef_[0][0]]}, template=pa.plot.template
        ),
    )
