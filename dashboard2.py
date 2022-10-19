from dash import Dash, dcc, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import psychoanalyze as pa


app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
app.layout = dbc.Container(
    [
        dcc.RadioItems(["U", "Y", "Z"], "Z", id="monkey"),
        dcc.Slider(
            step=None,
            marks={
                1: "A",
            },
            id="day",
        ),
        dcc.Graph(id="psycho"),
    ]
)


@app.callback(Output("day", "marks"), Input("monkey", "value"))
def day_marks(monkey):
    subjects = pa.subjects.load()
    sessions = pa.sessions.load()
    sessions["Days"] = pa.sessions.days(sessions, subjects)
    sessions = sessions[sessions["Monkey"] == monkey]
    day_marks = {
        float(sessions.loc[i, "Days"]): str(sessions.loc[i, "Date"].date())
        for i in sessions.index
    }
    if len(day_marks):
        return day_marks


if __name__ == "__main__":
    app.run_server(debug=True)
