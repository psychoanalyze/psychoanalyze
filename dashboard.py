from dash import Dash, dcc, html, Output, Input
import dash_bootstrap_components as dbc
import psychoanalyze as pa
import pandas as pd

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])


subjects_input = dbc.Col(
    [
        dbc.Label("Number of Subjects:"),
        dbc.Input(id="subjects", value=1, type="number"),
    ]
)

n_sessions_input = dbc.Col(
    [
        dbc.Label("Number of Sessions:"),
        dbc.Input(id="sessions", value=1, type="number"),
    ]
)

app.layout = dbc.Container(
    [dbc.Row([subjects_input, n_sessions_input])]
    + [dbc.Label("Number of trials generated:"), html.P(id="n_trials")]
    + [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(id="time-thresholds"),
                        dbc.Table(id="thresh-data"),
                    ]
                ),
                dbc.Col(
                    [
                        dcc.Graph(id="curves"),
                        dbc.Table(id="curve-data"),
                    ]
                ),
            ]
        ),
    ]
)


@app.callback(
    [
        Output("n_trials", "children"),
        Output("thresh-data", "children"),
        Output("time-thresholds", "figure"),
        Output("curves", "figure"),
        Output("curve-data", "children"),
    ],
    [Input("subjects", "value"), Input("sessions", "value")],
)
def generate_data(n_subjects, n_sessions):
    subjects = pa.data.subjects(n_subjects=n_subjects)
    curves_data = pa.data.generate(subjects, n=n_sessions, y="Hit Rate").reset_index()
    data = pa.data.thresholds(curves_data).rename(columns={"Hit Rate": "Threshold"})
    table = dbc.Table.from_dataframe(data)
    curve_table = dbc.Table.from_dataframe(curves_data)
    return (
        sum(curves_data["n"]),
        table.children,
        pa.plot.thresholds(data),
        pa.plot.curves(curves_data),
        curve_table.children,
    )


if __name__ == "__main__":
    app.run_server(debug=True)
