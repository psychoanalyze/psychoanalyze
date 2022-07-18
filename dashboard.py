from cmath import exp
from tkinter import E
from dash import Dash, dcc, Input, Output, State  # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
import psychoanalyze as pa
import pandas as pd
from psychoanalyze.layout import simulation_tab, experiment_tab
from scipy.special import expit

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
server = app.server

experiment_points = pa.points.load()
experiment_points = experiment_points[
    experiment_points.index.get_level_values("Monkey") == "Z"
]
experiment_points = experiment_points[
    experiment_points.index.get_level_values("Date") == "2017-01-10"
]

x = list(range(-3, 4))
p = expit(x)

trials = pa.trials.generate(100)
points = pa.points.from_trials(trials)


app.layout = dbc.Container(
    [
        dbc.Tabs(
            [
                experiment_tab(experiment_points),
                simulation_tab(points),
            ]
        ),
        dcc.Store(data=trials.to_json(orient="split"), id="trials"),
    ]
)


# @app.callback(Output(""))

# @app.callback(
#     Output("trials", "data"), Input("n-trials", "value"), State("trials", "data")
# )
# def add_or_remove_trials(n_trials, trials):
#     trials = pd.read_json(trials, orient="split")
#     trials.index.name = "x"
#     if n_trials > len(trials):
#         n_new_trials = n_trials - len(trials)
#         trials = pd.concat([trials, pa.trials.generate(n_new_trials)])
#     return trials.to_json(orient="split")


# @app.callback(
#     [Output("psych-plot", "figure"), Output("psych-table", "data")],
#     Input("trials", "data"),
# )
# def plot_from_data(trials):
#     trials_df = pd.read_json(trials, orient="split")
#     trials_df.index.name = "x"
#     points = pa.points.from_trials(trials_df)
#     points["Hit Rate"] = points["Hits"] / points["n"]
#     points_list = points.reset_index().to_dict("records")
#     return pa.points.plot(points), points_list


if __name__ == "__main__":
    app.run_server(debug=True)
