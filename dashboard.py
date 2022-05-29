from dash import Dash, dcc, Output, Input
import dash_bootstrap_components as dbc
import psychoanalyze as pa

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])

subjects_input = [
    dbc.Label("Number of Subjects:"),
    dbc.Input(id="subjects", value=2, type="number"),
]

n_sessions_input = [
    dbc.Label("Number of Sessions:"),
    dbc.Input(id="sessions", value=10, type="number"),
]

app.layout = dbc.Container(
    subjects_input
    + n_sessions_input
    + [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(id="time-thresholds"),
                        dbc.Table(id="data"),
                    ]
                ),
                dbc.Col(dcc.Graph(id="curves")),
            ]
        ),
    ]
)


@app.callback(
    [
        Output("data", "children"),
        Output("time-thresholds", "figure"),
        Output("curves", "figure"),
    ],
    [Input("subjects", "value"), Input("sessions", "value")],
)
def generate_data(n_subjects, n_sessions):
    subjects = pa.data.subjects(n_subjects=n_subjects)
    curves_data = pa.data.generate(subjects, n=n_sessions, y="Hit Rate").reset_index()
    data = pa.data.thresholds(curves_data).rename(columns={"Hit Rate": "Threshold"})
    table = dbc.Table.from_dataframe(data)
    return (table.children, pa.plot.thresholds(data), pa.plot.curves(curves_data))


if __name__ == "__main__":
    app.run_server(debug=True)
