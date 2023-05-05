import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, Output, Input, callback
import plotly.express as px
import pandas as pd
import random
from sklearn.linear_model import LogisticRegression
import numpy as np
import psychoanalyze as pa

dash.register_page(__name__, path="/simulate")


layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.InputGroup(
                            [
                                dbc.Input(id="n-trials", type="number", value=100),
                                dbc.InputGroupText("trials/block"),
                            ]
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(id="n-blocks", type="number", value=1),
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
                                dbc.Input(
                                    id="model-k", type="number", value=1, step=0.1
                                ),
                                dbc.InputGroupText(id="fit-output"),
                            ]
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        dcc.Graph(id="psi-plot"),
                        dash_table.DataTable(
                            id="points-table",
                            style_data={"color": "black"},
                            style_header={"color": "black"},
                        ),
                        dash_table.DataTable(
                            id="blocks-table",
                            style_data={"color": "black"},
                            style_header={"color": "black"},
                        ),
                    ]
                ),
            ]
        ),
    ]
)


@callback(
    [
        Output("psi-plot", "figure"),
        Output("points-table", "data"),
        Output("fit-output", "children"),
    ],
    [
        Input("n-trials", "value"),
        Input("min-intensity", "value"),
        Input("max-intensity", "value"),
        Input("model-k", "value"),
    ],
)
def update_figure(n_trials, min_intensity, max_intensity, k):
    intensity_choices = np.array(list(range(min_intensity, max_intensity + 1)))
    model_hit_rates = 1 / (1 + np.exp(-k * intensity_choices))
    intensities = [random.choice(intensity_choices) for _ in range(n_trials)]
    results = [
        random.random() <= 1 / (1 + np.exp(-k * intensity)) for intensity in intensities
    ]
    trials = pd.DataFrame(
        {
            "Intensity": intensities,
            "Result": results,
        }
    )
    fits = LogisticRegression(fit_intercept=False).fit(
        trials[["Intensity"]], trials["Result"]
    )
    predictions = fits.predict_proba(pd.DataFrame({"Intensity": intensity_choices}))[
        :, 1
    ]
    points = pd.concat(
        [
            pa.points.from_trials(trials)[["Hit Rate", "n"]],
            pd.DataFrame(
                {
                    "Hit Rate": model_hit_rates,
                    "n": 1,
                },
                index=pd.Index(intensity_choices, name="Intensity"),
            ),
            pd.DataFrame(
                {
                    "Hit Rate": predictions,
                    "n": 1,
                },
                index=pd.Index(intensity_choices, name="Intensity"),
            ),
        ],
        keys=["Observed", "Prior Prediction", "Posterior Prediction"],
        names=["Source"],
    )
    observed_points = points.loc["Observed"]
    return (
        px.scatter(
            points.reset_index(),
            x="Intensity",
            y="Hit Rate",
            size="n",
            color="Source",
            template=pa.plot.template,
        ),
        observed_points.reset_index().to_dict("records"),
        str(fits.coef_[0][0]),
    )
