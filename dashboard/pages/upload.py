import dash
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import base64
import pandas as pd
import io

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
    print(filename)
    if contents is not None:
        _, contents = contents.split(",")
        data = pd.read_csv(io.StringIO(base64.b64decode(contents).decode("utf-8")))
        if "trials" in filename:
            data = data.set_index(
                [
                    "Monkey",
                    "Date",
                    "Amp2",
                    "Width2",
                    "Freq2",
                    "Dur2",
                    "Active Channels",
                    "Return Channels",
                    "Amp1",
                    "Width1",
                    "Freq1",
                    "Dur1",
                    "Trial ID",
                ]
            )
            blocks = pa.blocks.from_trials(data)
        elif filename == "blocks.csv":
            blocks = data
        subjects = blocks.index.get_level_values("Monkey").value_counts().to_frame()
        return dash.dash_table.DataTable(subjects.to_dict("records"))
