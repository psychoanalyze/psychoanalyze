from dash import Dash, dcc, Output, Input
import dash_bootstrap_components as dbc
import psychoanalyze as pa

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])


subjects_input = dbc.Col(
    [
        dbc.Label("Number of subjects:"),
        dbc.Input(id="subjects", value=2, type="number"),
    ]
)

n_sessions_input = dbc.Col(
    [
        dbc.Label("Number of sessions:"),
        dbc.Input(id="sessions", value=10, type="number"),
    ]
)

n_trials_input = dbc.Col(
    [
        dbc.Label("Number of trials per session:"),
        dbc.Input(id="trials", value=100, type="number"),
    ]
)

true_thresh_input = dbc.Col(
    [
        dbc.Label("True threshold value:"),
        dbc.Input(id="location", value=0, type="number"),
    ]
)

threshold_column = dbc.Col(
    [
        dcc.Graph(id="time-thresholds"),
        dbc.Table(id="thresh-data"),
    ]
)

curves_column = dbc.Col(
    [
        dcc.Graph(id="curves"),
        dcc.Graph(id="logistic", figure=pa.plot.logistic(pa.data.logistic())),
        dbc.Table(id="curve-data"),
    ]
)

app.layout = dbc.Container(
    [
        dbc.Row([subjects_input, n_sessions_input, n_trials_input, true_thresh_input]),
        dbc.Row([threshold_column, curves_column]),
    ]
)


@app.callback(
    [
        Output("thresh-data", "children"),
        Output("time-thresholds", "figure"),
        Output("curves", "figure"),
        Output("curve-data", "children"),
    ],
    [Input("subjects", "value"), Input("sessions", "value"), Input("trials", "value")],
)
def generate_data(n_subjects, n_sessions, n_trials):
    subjects = pa.data.subjects(n_subjects=n_subjects)
    curves_data = pa.data.generate(
        subjects,
        n_sessions=n_sessions,
        y="Hit Rate",
        n_trials_per_stim_level=n_trials,
    ).reset_index()
    data = pa.data.thresholds(curves_data).rename(columns={"Hit Rate": "Threshold"})
    table = dbc.Table.from_dataframe(data)
    curve_table = dbc.Table.from_dataframe(curves_data)
    return (
        table.children,
        pa.plot.thresholds(data),
        pa.plot.curves(curves_data),
        curve_table.children,
    )


if __name__ == "__main__":
    app.run_server(debug=True)
