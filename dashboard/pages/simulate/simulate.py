import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, callback
import plotly.express as px
import pandas as pd
import psychoanalyze as pa

dash.register_page(__name__, path="/simulate")


component_column = dbc.Col(
    [
        html.H3("Counts"),
        dbc.InputGroup(
            [
                dbc.Input(id="n-trials", type="number", value=100),
                dbc.InputGroupText("trials/block"),
            ]
        ),
        dbc.InputGroup(
            [
                dbc.Input(id="n-blocks", type="number", value=10),
                dbc.InputGroupText("blocks/subject"),
            ]
        ),
        dbc.InputGroup(
            [
                dbc.Input(id="n-subjects", type="number", value=2),
                dbc.InputGroupText("subject"),
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
        dbc.InputGroup(
            [
                dbc.InputGroupText("x_0"),
                dbc.Input(id="x_0", type="number", value=0, step=0.1),
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
        Output("psi-plot", "figure"),
        Output("blocks-plot", "figure"),
    ],
    [
        Input("n-trials", "value"),
        Input("min-intensity", "value"),
        Input("max-intensity", "value"),
        Input("model-k", "value"),
        Input("n-blocks", "value"),
        Input("n-subjects", "value"),
    ],
)
def update_figure(n_trials, min_intensity, max_intensity, k, n_blocks, n_subjects):
    intensity_choices = pd.Index(
        range(min_intensity, max_intensity + 1), name="Intensity"
    )

    hit_rates = pa.blocks.model_hit_rates(intensity_choices, k)

    subject_fits = []
    for _ in range(n_subjects):
        trials = [
            pa.trials.moc_sample(intensity_choices, n_trials, k)
            for _ in range(n_blocks)
        ]
        observed_points = [pa.points.from_trials(trial_block) for trial_block in trials]
        fits = [pa.blocks.get_fit(trial_block) for trial_block in trials]
        subject_fits.append(fits)
        predictions = [
            pa.blocks.make_predictions(block_fit, intensity_choices)
            for block_fit in fits
        ]

        trials = pd.concat(trials, keys=range(n_blocks), names=["Block"])

        observed = pd.concat(observed_points, keys=range(n_blocks), names=["Block"])

        predictions = pd.concat(predictions, keys=range(n_blocks), names=["Block"])

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
        px.scatter(
            points.reset_index(),
            x="Intensity",
            y="Hit Rate",
            symbol="Source",
            template=pa.plot.template,
        ),
        px.ecdf(
            pd.concat(
                {
                    i: pd.Series([fit.coef_[0][0] for fit in subject_fits[i]], name="k")
                    for i in range(n_subjects)
                },
                names=["Subject"],
            ).reset_index(),
            x="k",
            color="Subject",
            template=pa.plot.template,
        ),
    )
