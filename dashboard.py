from dash import Dash, dcc, Output, Input
import dash_bootstrap_components as dbc
import psychoanalyze as pa
import pandas as pd

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])


subjects_input = dbc.Col(
    [
        dbc.Label("Number of subjects:"),
        dbc.Input(id="subjects", value=1, type="number"),
    ]
)

n_sessions_input = dbc.Col(
    [
        dbc.Label("Number of sessions:"),
        dbc.Input(id="sessions", value=1, type="number"),
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
        dbc.Input(id="true-thresh", value=0, type="number"),
    ]
)

true_scale_input = dbc.Col(
    [
        dbc.Label("True scale parameter value:"),
        dbc.Input(id="true-scale", value=1, type="number"),
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
        dbc.Label("Fitted threshold value: "),
        dbc.Label(id="fit-value"),
        dcc.Graph(id="sigmoid"),
        dbc.Table(id="curve-data"),
    ]
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                subjects_input,
                n_sessions_input,
                n_trials_input,
                true_thresh_input,
                true_scale_input,
            ]
        ),
        dbc.Row([threshold_column, curves_column]),
    ]
)


@app.callback(
    [
        Output("thresh-data", "children"),
        Output("time-thresholds", "figure"),
        Output("curves", "figure"),
        Output("curve-data", "children"),
        Output("fit-value", "children"),
    ],
    [
        Input("subjects", "value"),
        Input("sessions", "value"),
        Input("trials", "value"),
        Input("true-thresh", "value"),
        Input("true-scale", "value"),
    ],
)
def generate_data(n_subjects, n_sessions, n_trials, thresh, scale):
    subjects = pa.data.subjects(n_subjects=n_subjects)
    curves_data = pa.data.generate(
        subjects,
        n_sessions=n_sessions,
        y="Hit Rate",
        n_trials_per_stim_level=n_trials,
        X=list(range(-4, 5)),
        threshold=thresh,
        scale=scale,
    ).reset_index()
    data = pa.data.thresholds(curves_data).rename(columns={"Hit Rate": "Threshold"})
    table = dbc.Table.from_dataframe(data)
    curve_table = dbc.Table.from_dataframe(curves_data)
    fit_value = pa.data.fit_curve(curves_data)
    return (
        table.children,
        pa.plot.thresholds(data),
        pa.plot.curves(curves_data),
        curve_table.children,
        fit_value,
    )


@app.callback(
    Output("sigmoid", "figure"),
    Input("true-thresh", "value"),
    Input("true-scale", "value"),
)
def generate_sigmoid(thresh, scale):
    s1 = pa.data.logistic(thresh, scale)
    df1 = s1.to_frame()
    df1["Type"] = "Generated"
    s2 = pa.data.logistic(thresh + 0.5, scale)
    df2 = s2.to_frame()
    df2["Type"] = "Fitted"
    df = pd.concat([df1, df2])
    return pa.plot.logistic(df)


if __name__ == "__main__":
    app.run_server(debug=True)
