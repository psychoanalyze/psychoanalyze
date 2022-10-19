from dash import Dash, dcc, html, Output, Input, dash_table
import dash_bootstrap_components as dbc
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
            id="day-select",
        ),
        html.P(id="day-display"),
        dash_table.DataTable(id="ref-stimulus-table"),
        dcc.Graph(id="psycho"),
    ]
)


@app.callback(Output("day-select", "marks"), Input("monkey", "value"))
def day_marks(monkey):
    sessions = pa.data.load()["Sessions"]
    sessions = sessions[sessions["Monkey"] == monkey]
    day_marks = {
        float(sessions.loc[i, "Days"]): sessions.loc[i, "Date"]
        for i in sessions.index.values
    }
    if len(day_marks):
        return day_marks


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
    blocks = blocks.xs(monkey)
    blocks["Day"] = pa.blocks.day(blocks, subjects)
    blocks = blocks[blocks["Day"] == day]
    return blocks.to_dict("records")


if __name__ == "__main__":
    app.run_server(debug=True)
