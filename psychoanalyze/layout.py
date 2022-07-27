import dash_bootstrap_components as dbc  # type: ignore
from dash import html, dcc, dash_table  # type: ignore
import psychoanalyze as pa

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
                    dbc.Col(
                        [
                            dash_table.DataTable(
                                points.reset_index().to_dict("records"),
                                id="psych-table",
                            ),
                        ],
                        width=1,
                        align="center",
                    ),
                ],
                justify="center",
            )
        ],
        label="Simulation",
    )


def detection_tab(experiment_points):
    return dbc.Tab(
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
        label="Detection",
    )


discrimination_tab = dbc.Tab(
    [
        dcc.RadioItems(options=["ols", None], value="ols", id="trendline"),
        dcc.RadioItems(
            options=["Log Scale", "Linear Scale"], value="Log Scale", id="log-scale"
        ),
        dcc.RadioItems(options=["Group by x values", "show all blocks"], id="group-x"),
        dcc.RadioItems(options=["Histogram", "off"], value="Histogram", id="marginal"),
        dcc.RadioItems(options=["stable", "all"], value="all", id="stable"),
        dcc.RadioItems(
            options=["error bars", "off"],
            value="error bars",
            id="error",
        ),
        html.P("Plot width:"),
        dcc.Input(value=6, id="weber-width-input"),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="weber"), width=6, id="weber-width"),
                dbc.Col(dcc.Graph(id="weber-time")),
            ]
        ),
    ],
    label="Discrimination",
)


def experiment_tab(experiment_points):
    return dbc.Tab(
        dbc.Tabs(
            [
                discrimination_tab,
                detection_tab(experiment_points),
            ]
        ),
        label="Experiment",
    )
