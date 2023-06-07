from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import psychoanalyze as pa
import pandas as pd
import plotly.express as px


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
                dbc.Input(id="n-subjects", type="number", value=3),
                dbc.InputGroupText("subjects"),
            ],
            class_name="mb-4",
        ),
    ]
)

stimulus_params = html.Div(
    [
        html.H4("Stimulus"),
        html.H5("Modulated Dimension"),
        dcc.Dropdown(options={"amp": "Amplitude"}, value="amp"),
        dbc.InputGroup(
            [
                dbc.InputGroupText("n levels"),
                dbc.Input(id="n-levels", type="number", value=7),
            ],
            class_name="mb-3",
        ),
        html.H5("Fixed Dimension"),
        dcc.Dropdown(options={"pw": "Pulse Width"}, value="pw"),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Min"),
                dbc.Input(id="fixed-min", type="number", value=0),
                dbc.Input(id="fixed-max", type="number", value=1),
                dbc.InputGroupText("Max"),
            ],
            class_name="mb-3",
        ),
    ]
)

psi_params = html.Div(
    [
        html.H4("Psychometric Function"),
        html.H5("Logistic Regression"),
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
        dbc.Button("Re-run Simulation", color="primary", className="mb-3"),
        html.H3("Simulation Parameters"),
        experiment_params,
        stimulus_params,
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
            "label": "Schlichenmeyer et al. 2022",
            "value": "schlich2022",
        },
    ],
    placeholder="Select an open dataset...",
    value="schlich2022",
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
    [
        dcc.Graph(id="psi-plot", className="mb-5"),
        dcc.Markdown(
            "$\hat{p}(x) = \\frac{1}{1 + \exp(-kx - x_0)}$",
            mathjax=True,
        ),
    ],
    tab_id="psi-tab",
    label="Psychometric Function",
    activeTabClassName="fw-bold fst-italic",
)

ecdf_tab = dbc.Tab(
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id="ecdf-thresh"), width=6),
            dbc.Col(dcc.Graph(id="ecdf-slope"), width=6),
        ]
    ),
    label="eCDF",
    tab_id="ecdf-tab",
)

time_series_tab = dbc.Tab(
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
    label="Time Series",
    activeTabClassName="fw-bold fst-italic",
)

sd_tab = dbc.Tab(
    [
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
    ],
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
            ),
            class_name="my-4",
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
                            href="https://psychoanalyze.github.io",
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
    [
        Output("psi-plot", "figure"),
        Output("ecdf-thresh", "figure"),
        Output("ecdf-slope", "figure"),
        Output("longitudinal-plot", "figure"),
        Output("sd-plot", "figure"),
    ],
    [
        Input("n-trials", "value"),
        Input("n-levels", "value"),
        Input("model-k", "value"),
        Input("x_0", "value"),
        Input("gamma", "value"),
        Input("lambda", "value"),
        Input("n-subjects", "value"),
        Input("fixed-min", "value"),
        Input("fixed-max", "value"),
        Input("dataset", "value"),
    ],
)
def update_figure(
    n_trials,
    n_levels,
    k,
    x_0,
    gamma,
    lambda_,
    n_subjects,
    fixed_min,
    fixed_max,
    dataset,
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
        fixed_range = {"max": fixed_max, "min": fixed_min}
        fixed_n = 2

        trials = pa.subjects.generate_trials(
            n_trials,
            model_params,
            n_levels,
            fixed_range,
            fixed_n,
            n_days,
            n_subjects,
        )
        points = pa.points.from_trials(trials)

        fits = (
            trials.reset_index(level="Intensity")
            .groupby(["Subject", "Day", "Fixed Intensity"])
            .apply(pa.blocks.get_fit)
        )

        params = fits.apply(pa.blocks.fit_params)
        params = params.reset_index().rename(columns={"intercept": "Threshold"})
        return (
            px.box(
                points.reset_index(),
                x="Intensity",
                y="Hit Rate",
                color="Subject",
                template=pa.plot.template,
            ),
            px.ecdf(
                params,
                x="Threshold",
                color="Subject",
                template=pa.plot.template,
            ),
            px.ecdf(
                params.reset_index(),
                x="slope",
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
                color="Subject",
                template=pa.plot.template,
            ),
        )


if __name__ == "__main__":
    app.run_server(host="localhost", debug=True, dev_tools_hot_reload=False)
