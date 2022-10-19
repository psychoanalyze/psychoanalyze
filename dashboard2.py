from dash import Dash, dcc, html, Output, Input, dash_table
import dash_bootstrap_components as dbc
import psychoanalyze as pa
import pandas as pd
import plotly.express as px


app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
app.layout = dbc.Container(
    [
        dcc.RadioItems(["U", "Y", "Z"], "Z", id="monkey"),
        dcc.Slider(
            step=None,
            marks={"": ""},
            id="day-select",
        ),
        html.P(id="day-display"),
        dash_table.DataTable(id="ref-stimulus-table", row_selectable="multi"),
        dcc.Graph(id="psycho"),
    ]
)


@app.callback(
    Output("day-select", "marks"),
    Output("day-select", "value"),
    Input("monkey", "value"),
)
def day_marks(monkey):
    sessions = pa.sessions.load()
    sessions = sessions.xs(monkey)
    print(sessions)
    trials = pa.trials.load()
    print(trials)
    n_trials = pa.sessions.n_trials(sessions, trials)
    print(n_trials)
    day_value = n_trials.idxmax()[0][1]
    day_marks = {
        float(sessions.loc[i, "Day"]): str(sessions.loc[i, "Day"])
        for i in sessions.index.values
    }
    if len(day_marks):
        return day_marks, day_value


@app.callback(Output("day-display", "children"), Input("day-select", "value"))
def display_day(day):
    return f"Day {day}"


@app.callback(
    Output("ref-stimulus-table", "data"),
    Input("monkey", "value"),
    Input("day-select", "value"),
)
def display_ref_stimulus_table(monkey, day):
    blocks = pa.blocks.load()
    blocks = blocks.xs(monkey, drop_level=False)
    blocks["Day"] = pa.blocks.days(blocks, pa.subjects.load())
    blocks = blocks[blocks["Day"] == day]
    return blocks.reset_index().to_dict("records")


@app.callback(
    Output("psycho", "figure"),
    Input("ref-stimulus-table", "derived_virtual_data"),
)
def display_selected_traces(blocks):
    if blocks is None:
        points = pd.DataFrame({"x": [], "Hit Rate": []})
    else:
        if len(blocks):
            blocks = pd.DataFrame(blocks)
            blocks["Date"] = pd.to_datetime(blocks["Date"])
            blocks = blocks.set_index(
                ["Monkey", "Date", "Amp2", "Width2", "Freq2", "Dur2"]
            )
            points = pa.points.load()
            points = blocks.join(points)
            points["Hit Rate"] = points["Hits"] / points["n"]
        else:
            points = pd.DataFrame({"x": [], "Hit Rate": []})
    return px.scatter(points, x="x", y="Hit Rate", template="plotly_white")


if __name__ == "__main__":
    app.run_server(debug=True)
