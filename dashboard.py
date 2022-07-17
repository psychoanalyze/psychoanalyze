from tkinter import E
from dash import Dash, dcc, dash_table, Input, Output, State  # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
import psychoanalyze as pa
import pandas as pd
from psychoanalyze.layout import points_column
from scipy.special import expit

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
server = app.server

data_dir = "data"


def data_path(entity):
    return f"data/{entity}.csv"


experiment_points = pa.points.load()
experiment_trials = experiment_points[
    experiment_points.index.get_level_values("Monkey") == "Z"
]

# weber_data = pd.read_csv("data/weber_curves.csv")
x = list(range(-3, 4))
p = expit(x)

trials = pa.trials.generate(1)
points = pa.points.from_trials(trials)
points["Hit Rate"] = points["Hits"] / points["n"]
# points = pa.points.generate(x=x, n=[10] * 7, p=p)
points_list = points.reset_index().to_dict("records")

simulation_tab = dbc.Tab(
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
                        dash_table.DataTable(points_list, id="psych-table"),
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

experiment_tab = dbc.Tab(
    dbc.Tabs(
        [
            dbc.Tab(
                dcc.Graph(figure=pa.points.plot(experiment_points)), label="Detection"
            ),
            dbc.Tab(
                label="Discrimination",
            ),
        ]
    ),
    label="Experiment",
)

app.layout = dbc.Container(
    [
        dbc.Tabs(
            [
                experiment_tab,
                simulation_tab,
            ]
        ),
        dcc.Store(data=trials.to_json(orient="split"), id="trials"),
    ]
)


@app.callback(
    Output("trials", "data"), Input("n-trials", "value"), State("trials", "data")
)
def add_or_remove_trials(n_trials, trials):
    trials = pd.read_json(trials, orient="split")
    trials.index.name = "x"
    if n_trials > len(trials):
        print(len(trials))
        print(n_trials)
        n_new_trials = n_trials - len(trials)
        trials = pd.concat([trials, pa.trials.generate(n_new_trials)])
    return trials.to_json(orient="split")


@app.callback(
    [Output("psych-plot", "figure"), Output("psych-table", "data")],
    Input("trials", "data"),
)
def plot_from_data(trials):
    trials_df = pd.read_json(trials, orient="split")
    trials_df.index.name = "x"
    points = pa.points.from_trials(trials_df)
    points["Hit Rate"] = points["Hits"] / points["n"]
    points_list = points.reset_index().to_dict("records")
    return pa.points.plot(points), points_list


if __name__ == "__main__":
    app.run_server(debug=True)
