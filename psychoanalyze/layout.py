import dash_bootstrap_components as dbc  # type: ignore
from dash import html, dcc  # type: ignore
import psychoanalyze as pa
import dash_daq as daq  # type: ignore
import plotly.express as px  # type: ignore
import pandas as pd

defaults = {
    "session": {"sessions": 1, "trials": 100, "subjects": 1},
    "param": {"thresh": 0, "scale": 1, "gamma": 0, "lambda": 0},
    "x_min": {"x_min": -3},
    "x_max": {"x_max": 3},
}


def label(type, param):
    labels = {
        "param": f"{param}",
        "session": f"{param}",
        "x_min": "Min: ",
        "x_max": "Max: ",
    }
    return labels[type]


def input_pair(type, param, default_value):
    _label = label(type, param)
    return dbc.InputGroup(
        [
            dbc.Label(_label),
            dbc.Input(id=param, value=default_value, type="number"),
        ]
    )


def input_group(type):
    return [input_pair(type, key, value) for key, value in defaults[type].items()]


session_inputs = input_group("session")
param_inputs = input_group("param")
x_min_input = input_group("x_min")
x_max_input = input_group("x_max")

threshold_column = dbc.Col(
    [
        dcc.Graph(id="time-thresholds"),
        dbc.Table(id="thresh-data"),
    ]
)


def points_column(data):
    return dbc.Col(
        [
            dcc.Graph(figure=pa.points.plot(data), id="psych-plot"),
        ],
    )


diff_thresh_column = dbc.Col(
    [
        dcc.Graph(id="difference-thresholds"),
        html.P(id="weber-fraction"),
    ],
)
controls = dbc.Col(
    [
        dbc.Card(
            dbc.CardBody(
                [html.H4("Entity Counts", className="card-title")] + session_inputs
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [html.H4("Simulated Params", className="card-title")] + param_inputs
            ),
        ),
        dbc.Card(
            dbc.CardBody(
                [html.H4("Visible Range", className="card-title")]
                + x_min_input
                + x_max_input
            ),
        ),
    ],
    width=2,
)


def simulation_tab(points):
    return dbc.Tab(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("n trials"),
                            dbc.Input(type="number", value=1, id="n-trials"),
                        ],
                        width=1,
                        align="center",
                    ),
                    dbc.Col(
                        [
                            points_column(points),
                        ],
                        width=6,
                        align="center",
                    ),
                    # dbc.Col(
                    #     [
                    #         dash_table.DataTable(
                    #             points.reset_index().to_dict("records"),
                    #             id="psych-table",
                    #         ),
                    #     ],
                    #     width=1,
                    #     align="center",
                    # ),
                ],
                justify="center",
            ),
            # dbc.Row(pa.plot.strength_duration()),
        ],
        label="Simulation",
    )


sd_plots = [
    dbc.Row(
        [
            dbc.Col(
                dcc.Graph(
                    # figure=pa.plot.strength_duration(
                    #     data=pa.strength_duration.from_blocks(
                    #         pa.blocks.load(), dim=dim
                    #     ),
                    #     dim=dim,
                    #     plot_type="inverse",
                    # )
                    figure=px.scatter()
                )
            )
            for dim in ["Amp", "Width"]
        ]
    )
    for view in ["inverse", "linear"]
]

sessions = pd.read_csv("data/trials.csv")[["Monkey", "Date"]].drop_duplicates()


def detection_tab(experiment_points, blocks):
    return dbc.Tab(
        dbc.Tabs(
            [
                dbc.Tab(
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Graph(figure=pa.plot.counts(sessions), id="counts")
                            ),
                            dbc.Col(
                                dcc.Graph(figure=pa.plot.counts(sessions, dim="Width"))
                            ),
                        ],
                    ),
                    label="Counts",
                ),
                dbc.Tab(sd_plots, label="Strength-Duration Plots", tab_id="sd"),
                dbc.Tab(
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Graph(
                                    # figure=pa.plot.ecdf(blocks),
                                    id="ecdf_g_l",
                                )
                            ),
                            # dbc.Col(
                            #     dcc.Graph(
                            #         figure=px.ecdf(blocks, x="width"),
                            #         id="ecdf_amp",
                            #     )
                            # ),
                            dbc.Col(
                                dcc.Graph(
                                    # figure=px.ecdf(blocks, x="Threshold"),
                                    id="ecdf_pw"
                                )
                            ),
                        ]
                    ),
                    label="eCDF",
                ),
                dbc.Tab(
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Graph(
                                    figure=pa.points.plot(experiment_points),
                                    id="points",
                                )
                            ),
                            dbc.Col(
                                [
                                    dbc.Button("Fit curves", id="fit"),
                                    pa.points.datatable(experiment_points),
                                ],
                                width=2,
                                align="center",
                            ),
                        ]
                    ),
                    label="Single Block",
                ),
            ],
            active_tab="sd",
        ),
        label="Detection",
    )


discrimination_tab = dbc.Tab(
    [
        dbc.Row(
            [
                dbc.Col(
                    daq.BooleanSwitch(
                        on=True,
                        label="Trendline",
                        labelPosition="top",
                        id="trendline",
                    ),
                ),
                dbc.Col(
                    dbc.RadioItems(
                        options=[
                            {"label": "Log Scale", "value": "Log Scale"},
                            {"label": "Linear Scale", "value": "Linear Scale"},
                        ],
                        value="Log Scale",
                        id="log-scale",
                    ),
                ),
                dbc.Col(
                    dbc.RadioItems(
                        options=[
                            {
                                "label": "Group by x values",
                                "value": "Group by x values",
                            },
                            {"label": "Show all blocks", "value": None},
                        ],
                        value=None,
                        id="group-x",
                    )
                ),
                dbc.Col(
                    dbc.RadioItems(
                        options=[
                            {"label": "Histogram", "value": "Histogram"},
                            {"label": "Off", "value": "Off"},
                        ],
                        value="Histogram",
                        id="marginal",
                    )
                ),
                dbc.Col(
                    dbc.RadioItems(
                        options=[
                            {"label": "error bars", "value": "error bars"},
                            {"label": "off", "value": "off"},
                        ],
                        value="error bars",
                        id="error",
                    )
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="weber"), width=6, id="weber-width"),
            ]
        ),
    ],
    label="Discrimination",
)


def experiment_tab(experiment_points, blocks):
    return dbc.Tab(
        dbc.Tabs(
            [
                detection_tab(experiment_points, blocks),
                discrimination_tab,
            ]
        ),
        label="Experiment",
    )
