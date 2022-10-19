from dash import Dash, dcc, html, Output, Input, dash_table
import dash_bootstrap_components as dbc
import psychoanalyze as pa
import pandas as pd
import plotly.express as px


app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
app.layout = dbc.Container(
    [
        html.H1("PsychoAnalyze"),
        dbc.Row(
            [
                dbc.Col(
                    dbc.RadioItems(
                        options=[
                            {"label": monkey, "value": monkey}
                            for monkey in ["U", "Y", "Z"]
                        ],
                        value="Z",
                        inline=True,
                        id="monkey",
                    )
                ),
                dbc.Col(
                    [
                        html.P(id="day-display"),
                        dcc.Slider(
                            step=None,
                            marks={"": ""},
                            id="day-select",
                        ),
                    ],
                    width=8,
                ),
            ]
        ),
        dash_table.DataTable(
            id="ref-stimulus-table", row_selectable="single", selected_rows=[0]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button("Fit Curve"),
                    align="center",
                    width=2,
                    n_clicks=0,
                    id="fit button",
                ),
                dbc.Col(dcc.Graph(id="psycho"), width=8),
            ],
            justify="center",
        ),
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
    trials = pa.trials.load()
    n_trials = pa.sessions.n_trials(sessions, trials)
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
    blocks = blocks[blocks["n Levels"] > 1]
    return (
        blocks.reset_index()
        .drop(columns=["Monkey", "Date", "Dimension", "n Levels", "Day"])
        .to_dict("records")
    )


@app.callback(
    Output("psycho", "figure"),
    Input("monkey", "value"),
    Input("day-select", "value"),
    Input("ref-stimulus-table", "selected_rows"),
)
def display_selected_traces(monkey, day, row_numbers):
    if row_numbers is None:
        points = pd.DataFrame({"x": [], "Hit Rate": []})
    else:
        if len(row_numbers):
            blocks = pa.blocks.load()
            blocks = blocks.xs(monkey, drop_level=False)
            blocks["Day"] = pa.blocks.days(blocks, pa.subjects.load())
            blocks = blocks[blocks["n Levels"] > 1]
            blocks = blocks[blocks["Day"] == day].iloc[row_numbers]
            points = pa.points.load()
            points = blocks.join(points)
            points["Hit Rate"] = points["Hits"] / points["n"]
        else:
            points = pd.DataFrame({"x": [], "Hit Rate": []})
    return px.scatter(points, x="x", y="Hit Rate", template=pa.plot.template)


if __name__ == "__main__":
    app.run_server(debug=True)
