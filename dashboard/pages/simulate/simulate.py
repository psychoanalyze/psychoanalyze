import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, callback
import plotly.express as px
import pandas as pd
import psychoanalyze as pa
import duckdb

dash.register_page(__name__, path="/simulate")

duckdb.sql("CREATE TEMP TABLE LastTrials (Intensity INTEGER, Result INTEGER)")

component_column = dbc.Col(
    [
        html.H3("Generate n"),
        dbc.InputGroup(
            [
                dbc.Input(id="n-trials", type="number", value=100),
                dbc.InputGroupText("trials per block"),
            ]
        ),
        dbc.InputGroup(
            [
                dbc.Input(id="n-blocks", type="number", value=10),
                dbc.InputGroupText("blocks per subject"),
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
        html.H4("Modulated Dimension"),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Min"),
                dbc.Input(id="min-intensity", type="number", value=-4),
                dbc.Input(id="max-intensity", type="number", value=4),
                dbc.InputGroupText("Max"),
            ],
            class_name="mb-3",
        ),
        html.H4("Fixed Dimension"),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Fixed"),
                dbc.Input(id="fixed-intensity", type="number", value=0),
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
    ],
    width=3,
)

plot_tabs = dbc.Col(
    dbc.Tabs(
        [
            dbc.Tab(
                dcc.Graph(id="psi-plot"),
                label="Psychometric Function",
                activeTabClassName="fw-bold fst-italic",
            ),
            dbc.Tab(
                dbc.Row(
                    [
                        dbc.Col(dcc.Graph(id="blocks-plot"), width=6),
                        dbc.Col(dcc.Graph(id="ecdf-plot"), width=6),
                    ]
                ),
                label="eCDF",
                tab_id="ecdf-tab",
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
            dbc.Tab(
                dcc.Graph(
                    figure=px.scatter(
                        pd.DataFrame(
                            {
                                "Fixed Intensity": [],
                                "Threshold (modulated dimension)": [],
                            }
                        ),
                        x="Fixed Intensity",
                        y="Threshold (modulated dimension)",
                        template=pa.plot.template,
                    ),
                    id="sd-plot",
                ),
                label="Strength-Duration",
                tab_id="sd-tab",
            ),
        ],
        active_tab="sd-tab",
    )
)

layout = html.Div(
    [
        dbc.Row(
            [
                component_column,
                plot_tabs,
            ]
        ),
    ]
)


@callback(
    [
        Output("psi-plot", "figure"),
        Output("blocks-plot", "figure"),
        Output("ecdf-plot", "figure"),
        Output("longitudinal-plot", "figure"),
        Output("sd-plot", "figure"),
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
        trials = pa.trials.moc_sample(intensity_choices, n_trials, k, x_0, n_blocks)
        duckdb.sql("INSERT INTO LastTrials SELECT Intensity, Result FROM trials")
        observed = pa.points.from_trials(trials)
        fits = pa.blocks.get_fits(trials)
        predictions = pa.subjects.make_predictions(fits, intensity_choices)
        fit_params = pa.subjects.fit_params(fits)

        subject_fits.append(fit_params)
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
    params = pd.concat(
        {i: subject_fits[i] for i in range(n_subjects)},
        names=["Subject"],
    )
    params = params.reset_index().rename(columns={"intercept": "Threshold"})
    params["Day"] = params["Block"]
    params["Fixed Intensity"] = 0
    return (
        px.box(
            all_points.reset_index(),
            x="Intensity",
            y="Hit Rate",
            color="Subject",
            template=pa.plot.template,
        ),
        px.ecdf(
            params.reset_index(),
            x="slope",
            color="Subject",
            template=pa.plot.template,
        ),
        px.ecdf(
            params,
            x="Threshold",
            color="Subject",
            template=pa.plot.template,
        ),
        px.scatter(
            params,
            x="Day",
            y="Threshold",
            symbol="Subject",
            template=pa.plot.template,
        ),
        px.box(
            params.rename(columns={"Threshold": "Threshold (modulated dimension)"}),
            x="Fixed Intensity",
            y="Threshold (modulated dimension)",
            template=pa.plot.template,
        ),
    )
