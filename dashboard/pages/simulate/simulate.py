import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, State, callback
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
            ],
            class_name="mb-4",
        ),
        html.H3("Intensity Levels"),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Min"),
                dbc.Input(id="min-intensity", type="number", value=-4),
                dbc.Input(id="max-intensity", type="number", value=4),
                dbc.InputGroupText("Max"),
            ],
            class_name="mb-4",
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
                dbc.Input(id="x_0", type="number", value=0.0, step=0.1),
            ],
            class_name="mb-3",
        ),
        dbc.Button("Show/Hide ECDF Plots", className="mb-3", id="ecdf-button"),
    ],
    width=3,
)

layout = html.Div(
    [
        dbc.Row(
            [
                component_column,
                dbc.Col(
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                dcc.Graph(id="psi-plot"),
                                label="Psychometric Function",
                                activeTabClassName="fw-bold fst-italic",
                            ),
                            dbc.Tab(
                                dcc.Graph(
                                    figure=px.scatter(
                                        pd.DataFrame({"Day": [], "Threshold": []}),
                                        x="Day",
                                        y="Threshold",
                                        template=pa.plot.template,
                                    ),
                                    id="longitudinal-plot",
                                ),
                                tab_id="longitudinal-tab",
                                label="Longitudinal Plot",
                                activeTabClassName="fw-bold fst-italic",
                            ),
                        ],
                        active_tab="longitudinal-tab",
                    )
                ),
            ]
        ),
        dbc.Collapse(
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="blocks-plot")),
                    dbc.Col(dcc.Graph(id="ecdf-plot")),
                ]
            ),
            id="collapse",
        ),
    ]
)


@callback(
    [
        Output("psi-plot", "figure"),
        Output("blocks-plot", "figure"),
        Output("ecdf-plot", "figure"),
        Output("longitudinal-plot", "figure"),
    ],
    [
        Input("n-trials", "value"),
        Input("min-intensity", "value"),
        Input("max-intensity", "value"),
        Input("model-k", "value"),
        Input("x_0", "value"),
        Input("n-blocks", "value"),
        Input("n-subjects", "value"),
    ],
)
def update_figure(n_trials, min_intensity, max_intensity, k, x_0, n_blocks, n_subjects):
    intensity_choices = pd.Index(
        range(min_intensity, max_intensity + 1), name="Intensity"
    )

    hit_rates = pa.blocks.model_hit_rates(intensity_choices, k, x_0)

    subject_fits = []
    subject_points = []
    for _ in range(n_subjects):
        trials = [
            pa.trials.moc_sample(intensity_choices, n_trials, k, x_0)
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
        subject_points.append(points)
    all_points = pd.concat(
        {i: subject_points[i] for i in range(n_subjects)},
        names=["Subject"],
    ).reset_index()
    slopes = pd.concat(
        {
            i: pd.Series([fit.coef_[0][0] for fit in subject_fits[i]], name="k")
            for i in range(n_subjects)
        },
        names=["Subject"],
    )
    thresholds = pd.concat(
        {
            i: pd.Series([fit.intercept_[0] for fit in subject_fits[i]], name="x_0")
            for i in range(n_subjects)
        },
        names=["Subject"],
    )
    return (
        px.box(
            all_points.reset_index(),
            x="Intensity",
            y="Hit Rate",
            color="Subject",
            template=pa.plot.template,
        ),
        px.ecdf(
            slopes.reset_index(),
            x="k",
            color="Subject",
            template=pa.plot.template,
        ),
        px.ecdf(
            thresholds.reset_index(),
            x="x_0",
            color="Subject",
            template=pa.plot.template,
        ),
        px.scatter(
            thresholds.reset_index().rename(
                columns={"x_0": "Thresholds", "level_1": "Day"}
            ),
            x="Day",
            y="Thresholds",
            symbol="Subject",
            template=pa.plot.template,
        ),
    )


@callback(
    Output("collapse", "is_open"),
    [Input("ecdf-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_ecdf(n, is_open):
    if n:
        return not is_open
    return is_open
