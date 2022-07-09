import dash_bootstrap_components as dbc  # type: ignore


defaults = {
    "session": {"sessions": 1, "trials": 100, "subjects": 1},
    "param": {"thresh": 0, "scale": 1, "gamma": 0, "lambda": 0},
    "x_min": {"x_min": -3},
    "x_max": {"x_max": 3},
}


def label(type, param):
    labels = {
        "param": f"Simulated {param} value: ",
        "session": f"Number of {param}: ",
        "x_min": "Minimum x value: ",
        "x_max": "Maximum x value: ",
    }
    return labels[type]


def input_pair(type, param, default_value):
    _label = label(type, param)
    return dbc.Col(
        [
            dbc.Label(_label),
            dbc.Input(id=param, value=default_value, type="number"),
        ]
    )


def input_group(type):
    return [input_pair(type, key, value) for key, value in defaults[type].items()]
