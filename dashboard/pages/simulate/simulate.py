import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, callback
import plotly.express as px
import pandas as pd
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
    intensity_choices = pd.Index(
        range(min_intensity, max_intensity + 1), name="Intensity"
    )

    hit_rates = pa.blocks.model_hit_rates(intensity_choices, k)

    trials1 = pa.blocks.moc_sample(intensity_choices, n_trials, k)
    observed_points1 = pa.points.from_trials(trials1)
    fits1 = pa.blocks.get_fit(trials1)
    predictions1 = pa.blocks.make_predictions(fits1, intensity_choices)

    trials2 = pa.blocks.moc_sample(intensity_choices, n_trials, k)
    observed_points2 = pa.points.from_trials(trials2)
    fits2 = pa.blocks.get_fit(trials2)
    predictions2 = pa.blocks.make_predictions(fits2, intensity_choices)

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
