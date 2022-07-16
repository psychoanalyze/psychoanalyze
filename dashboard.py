from dash import Dash, dcc, dash_table, Input, Output, State  # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
import psychoanalyze as pa
import pandas as pd
from psychoanalyze.layout import points_column, diff_thresh_column
from scipy.special import expit
import json

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
server = app.server

block_index_levels = pa.sessions.dims + pa.blocks.dims
point_index_levels = block_index_levels + pa.points.dims

data_dir = "data"


def data_path(entity):
    return f"data/{entity}.csv"


weber_data = pd.read_csv("data/weber_curves.csv")
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
            dbc.Tab(label="Detection"),
            dbc.Tab(
                dcc.Graph(figure=pa.weber.plot(weber_data)), label="Discrimination"
            ),
        ]
    ),
    label="Experiment",
)

app.layout = dbc.Container(
    [
        dbc.Tabs(
            [
                simulation_tab,
                experiment_tab,
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
        trials = pd.concat([trials, pa.trials.generate(1)])
        print(trials)
    elif n_trials < len(trials):
        trials = trials[:-1]
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
