import dash
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import base64
import pandas as pd
import io
import plotly.express as px

import psychoanalyze as pa


dash.register_page(__name__, path="/upload")

layout = dbc.Container(
    [
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
        html.Div(id="output-data-upload"),
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
            dash.dash_table.DataTable(output_data.to_dict("records")),
            dcc.Graph(figure=px.bar(output_data, x="Monkey", y="Total Blocks")),
        ]
