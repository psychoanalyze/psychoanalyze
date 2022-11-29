import dash
from dash import html, dcc, Output, Input, State, dash_table
import dash_bootstrap_components as dbc
import base64
import pandas as pd
import io
import plotly.express as px

import psychoanalyze as pa


dash.register_page(__name__, path="/upload")

layout = dbc.Container(
    [
        html.H2("Upload your own data:"),
        dcc.Upload(
            ["Drag and Drop or ", html.A("Select a File")],
            id="upload-data",
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
            },
            multiple=True,
        ),
        html.H2("Or,"),
        html.P("Process this randomly generated dataset:"),
        dbc.Button("Process", id="process-upload"),
        html.H4("trials.csv"),
        dash_table.DataTable(
            data=[
                {"Trial ID": 1, "Result": "Miss"},
                {"Trial ID": 2, "Result": "Hit"},
            ],
            id="sample-trials",
        ),
        html.Div(id="output-data-upload"),
        html.P(id="trial-summary"),
    ]
)


@dash.callback(
    Output("output-data-upload", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def show_contents(contents, filename):
    if contents:
        contents = contents[0]
        filename = filename[0]
        _, contents = contents.split(",")
        data = pd.read_csv(io.StringIO(base64.b64decode(contents).decode("utf-8")))
        if "trials" in filename:
            data = data.set_index(
                pa.sessions.index_levels
                + pa.blocks.index_levels
                + pa.points.index_levels
                + [
                    "Trial ID",
                ]
            )
            blocks = pa.blocks.from_trials(data)
        elif filename == "blocks.csv":
            blocks = data
        subjects = pa.blocks.monkey_counts(blocks)
        output_data = subjects.to_frame().reset_index()
        return [
            dash_table.DataTable(output_data.to_dict("records")),
            dcc.Graph(figure=px.bar(output_data, x="Monkey", y="Total Blocks")),
        ]


@dash.callback(
    Output("trial-summary", "children"),
    Input("process-upload", "n_clicks"),
    State("sample-trials", "data"),
)
def summarize_trials(n_clicks, data):
    if n_clicks:
        n = sum([pa.trials.codes[trial["Result"]] for trial in data])
        return f"n trials: {n}, hit rate: {n/len(data)}"
