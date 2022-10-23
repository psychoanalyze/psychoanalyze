from dash import Dash, dcc, html, Output, Input, State, dash_table
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
                    [
                        dbc.RadioItems(
                            options=[
                                {"label": monkey, "value": monkey}
                                for monkey in ["U", "Y", "Z"]
                            ],
                            value="Z",
                            inline=True,
                            id="monkey-select",
                        ),
                        dbc.RadioItems(
                            options=[
                                {"label": dim, "value": dim} for dim in ["Amp", "PW"]
                            ],
                            value="Amp",
                            inline=True,
                            id="dim-select",
                        ),
                    ]
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
                    [
                        dbc.Button(
                            "Fit Curve",
                            id="fit-button",
                            n_clicks=0,
                        ),
                        html.P(id="threshold"),
                    ],
                    align="center",
                    width=2,
                ),
                dbc.Col(dcc.Graph(id="psychometric-fig"), width=8),
            ],
            justify="center",
        ),
    ]
)


@app.callback(
    Output("day-select", "marks"),
    Output("day-select", "value"),
    Input("monkey-select", "value"),
)
def day_marks(monkey):
    sessions = pa.sessions.load(monkey=monkey)
    session_max_n_index = sessions["n Trials"].idxmax()
    day_value = sessions.loc[session_max_n_index, "Day"]
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
    Input("monkey-select", "value"),
    Input("day-select", "value"),
)
def display_ref_stimulus_table(monkey, day):
    blocks = pa.blocks.load(monkey=monkey, day=day)
    return (
        blocks.reset_index()
        .drop(columns=["Monkey", "Date", "Dimension", "n Levels", "Day"])
        .to_dict("records")
    )


@app.callback(
    Output("psychometric-fig", "figure"),
    Input("monkey-select", "value"),
    Input("day-select", "value"),
    Input("ref-stimulus-table", "selected_rows"),
    Input("fit-button", "n_clicks"),
)
def display_selected_traces(monkey, day, row_numbers, n_clicks):
    if row_numbers is None:
        points = pd.DataFrame({"x": [], "Hit Rate": []})
    else:
        if len(row_numbers):
            blocks = pa.blocks.load(monkey=monkey, day=day)
            blocks = blocks.iloc[row_numbers]
            points = pa.points.load()
            points = blocks.join(points)
            if n_clicks:
                return pa.points.plot(points, trendline="ols")
        else:
            points = pd.DataFrame({"x": [], "Hit Rate": []})
    base_plot = pa.points.plot(points)
    return base_plot


if __name__ == "__main__":
    app.run_server(debug=True)
