from dash import Dash, html, dcc, Input, Output, dash_table
from dash.dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc
import psychoanalyze as pa
import pandas as pd
import plotly.express as px
from plotly import graph_objects as go
from werkzeug.middleware.profiler import ProfilerMiddleware
import os
import numpy as np

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.BOOTSTRAP],
)

server = app.server

experiment_params = html.Div(
    [
        html.H4("Experimental Design"),
        dbc.InputGroup(
            [
                dbc.Input(id="n-trials", type="number", value=100),
                dbc.InputGroupText("trials per block"),
            ]
        ),
        dbc.InputGroup(
            [
                dbc.Input(id="n-subjects", type="number", value=1),
                dbc.InputGroupText("subjects"),
            ],
            class_name="mb-4",
        ),
    ]
)


psi_params = html.Div(
    [
        html.H4("Psychometric Function"),
        dcc.Dropdown(
            id="f",
            options=[{"label": "Logistic (expit)", "value": "expit"}],
            value="expit",
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("intercept"),
                dbc.Input(id="x_0", type="number", value=50.0, step=0.1),
            ],
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("slope"),
                dbc.Input(id="model-k", type="number", value=1, step=0.1),
            ]
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("guess rate"),
                dbc.Input(id="gamma", type="number", value=0.0, step=0.1),
            ],
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("lapse rate"),
                dbc.Input(id="lambda", type="number", value=0.0, step=0.1),
            ],
            class_name="mb-3",
        ),
    ]
)

component_column = dbc.Col(
    [
        html.H3("Simulation Parameters"),
        experiment_params,
        psi_params,
    ],
    width=3,
)

upload_component = dcc.Upload(
    """Upload your own data -
                        drag and drop or click to open file browser
                        """,
    id="upload-data",
    style={
        "width": "100%",
        "height": "60px",
        "lineHeight": "60px",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "textAlign": "center",
    },
    multiple=True,
)

dataset_component = dcc.Dropdown(
    options=[
        {
            "label": html.Span(
                ["Schlichenmeyer et al. 2022"], style={"color": "black"}
            ),
            "value": "schlich2022",
        }
    ],
    placeholder="Select an open dataset...",
    id="dataset",
)

empirical_data_components = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(upload_component),
                dbc.Col(dataset_component),
            ]
        ),
    ]
)

psi_tab = dbc.Tab(
    tab_id="psi-tab",
    label="Psychometric Function",
    activeTabClassName="fw-bold fst-italic",
)

ecdf_tab = dbc.Tab(
    label="eCDF",
    tab_id="ecdf-tab",
)

time_series_tab = dbc.Tab(
    tab_id="time-series-tab",
    label="Time Series",
    activeTabClassName="fw-bold fst-italic",
)

sd_tab = dbc.Tab(
    label="Strength-Duration",
    tab_id="sd-tab",
)

plot_tabs = dbc.Col(
    [
        empirical_data_components,
        dbc.Row(
            dbc.Tabs(
                [
                    psi_tab,
                    ecdf_tab,
                    time_series_tab,
                    sd_tab,
                ],
                active_tab="psi-tab",
                id="plot-tabs",
            ),
            class_name="my-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(id="plot"),
                    ],
                    width=7,
                ),
                dbc.Col(
                    [
                        dash_table.DataTable(
                            id="table",
                            columns=[
                                {
                                    "name": "Day",
                                    "id": "Day",
                                },
                                {
                                    "name": "Slope",
                                    "id": "slope",
                                    "type": "numeric",
                                    "format": Format(precision=2, scheme=Scheme.fixed),
                                },
                                {
                                    "name": "Threshold",
                                    "id": "Threshold",
                                    "type": "numeric",
                                    "format": Format(precision=2, scheme=Scheme.fixed),
                                },
                            ],
                            style_data={"color": "black"},
                            style_header={"color": "black"},
                        ),
                    ],
                    width=4,
                ),
            ]
        ),
    ]
)

app.layout = dbc.Container(
    [
        dbc.NavbarSimple(
            [
                dbc.NavItem(
                    [
                        dbc.NavLink(
                            "GitHub",
                            href="https://github.com/psychoanalyze/psychoanalyze",
                        ),
                        html.I(className="bi bi-github"),
                    ],
                    className="d-flex align-items-center mx-2",
                ),
                dbc.NavItem(
                    [
                        dbc.NavLink(
                            "Docs",
                            href="https://docs.psychoanalyze.io",
                        ),
                        html.I(className="bi bi-book"),
                    ],
                    className="d-flex align-items-center mx-2",
                ),
            ],
            brand=dbc.Col(
                [
                    dbc.Row(html.H1("PsychoAnalyze")),
                    dbc.Row(
                        html.P(
                            "Interactive data simulation & analysis for psychophysics."
                        )
                    ),
                ],
            ),
            brand_href="/",
            class_name="mb-3",
        ),
        dbc.Row(
            [
                component_column,
                plot_tabs,
            ]
        ),
    ]
)


@app.callback(
    [Output("plot", "figure"), Output("table", "data")],
    [
        Input("n-trials", "value"),
        Input("model-k", "value"),
        Input("x_0", "value"),
        Input("gamma", "value"),
        Input("lambda", "value"),
        Input("n-subjects", "value"),
        Input("dataset", "value"),
        Input("plot-tabs", "active_tab"),
    ],
)
def update_figure(
    n_trials,
    k,
    x_0,
    gamma,
    lambda_,
    n_subjects,
    dataset,
    active_tab,
):
    if dataset == "schlich2022":
        points = pd.read_csv("data/normalized/points.csv")
        blocks = pd.read_csv("data/fit.csv")
        return (
            [
                px.box(
                    points,
                    x="Charge",
                    y="Hit Rate",
                    # color="Subject",
                    template=pa.plot.template,
                )
            ]
            + [px.ecdf(blocks, x="Threshold", template=pa.plot.template)] * 2
            + [px.scatter()] * 2
        )
    else:
        n_days = 5
        model_params = {"x_0": x_0, "k": k, "gamma": gamma, "lambda": lambda_}

        trials = pa.subjects.generate_trials(
            n_trials,
            model_params,
            n_days,
            n_subjects,
        )
        points = pa.points.from_trials(trials)
        intensities = points.reset_index()["Intensity"]
        x = list(np.linspace(intensities.min(), intensities.max()))
        y = [pa.trials.psi(gamma, lambda_, k, intensity, x_0) for intensity in x]

        fits = (
            trials.reset_index(level="Intensity")
            .groupby(["Subject", "Day"])
            .apply(pa.blocks.get_fit)
        )

        params = fits.apply(pa.blocks.fit_params)
        params = params.reset_index().rename(columns={"intercept": "Threshold"})
        if active_tab == "psi-tab":
            return (
                px.box(
                    points.reset_index(),
                    x="Intensity",
                    y="Hit Rate",
                    color="Subject",
                    template=pa.plot.template,
                ).add_trace(go.Scatter(x=x, y=y, mode="lines", name="model")),
                params.to_dict("records"),
            )
        elif active_tab == "ecdf-tab":
            return (
                px.ecdf(
                    params,
                    x="Threshold",
                    color="Subject",
                    template=pa.plot.template,
                ),
                params.to_dict("records"),
            )
        elif active_tab == "time-series-tab":
            return (
                px.scatter(
                    params,
                    x="Day",
                    y="Threshold",
                    symbol="Subject",
                    template=pa.plot.template,
                ),
                params.to_dict("records"),
            )
        elif active_tab == "sd-tab":
            return (
                px.box(
                    params.rename(
                        columns={"Threshold": "Threshold (modulated dimension)"}
                    ),
                    x="Fixed Intensity",
                    y="Threshold (modulated dimension)",
                    color="Subject",
                    template=pa.plot.template,
                ),
                params.to_dict("records"),
            )
            # px.ecdf(
            #     params.reset_index(),
            #     x="slope",
            #     color="Subject",
            #     template=pa.plot.template,
            # ),


PROF_DIR = ".profiler"
if __name__ == "__main__":
    if os.getenv("PROFILER", None):
        app.server.config["PROFILE"] = True
        app.server.wsgi_app = ProfilerMiddleware(
            app.server.wsgi_app,
            sort_by=("cumtime", "tottime"),
            restrictions=[160],
            stream=None,
            profile_dir=PROF_DIR,
        )
    app.run_server(host="localhost", debug=True, use_reloader=False)
