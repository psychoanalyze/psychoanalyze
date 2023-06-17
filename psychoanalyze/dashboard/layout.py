import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table


experiment_params = html.Div(
    [
        html.H4("Experimental Design"),
        dbc.InputGroup(
            [
                dbc.Input(id="n-trials", type="number", value=50),
                dbc.InputGroupText("trials per block"),
            ]
        ),
        dbc.InputGroup(
            [
                dbc.Input(id="n-subjects", type="number", value=2),
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
                                    "name": "Subject",
                                    "id": "Subject",
                                },
                                {
                                    "name": "Block",
                                    "id": "Block",
                                },
                                {
                                    "name": "Slope",
                                    "id": "slope",
                                    "type": "numeric",
                                    "format": dash_table.Format.Format(
                                        precision=2,
                                        scheme=dash_table.Format.Scheme.fixed,
                                    ),
                                },
                                {
                                    "name": "Threshold",
                                    "id": "Threshold",
                                    "type": "numeric",
                                    "format": dash_table.Format.Format(
                                        precision=2,
                                        scheme=dash_table.Format.Scheme.fixed,
                                    ),
                                },
                            ],
                            row_selectable="multi",
                            style_data={"color": "black"},
                            style_header={"color": "black"},
                            page_size=15,
                        ),
                    ],
                    width=4,
                ),
            ]
        ),
    ]
)

layout = dbc.Container(
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
        dcc.Store(id="blocks-store"),
        dcc.Store(id="points-store"),
    ],
)
