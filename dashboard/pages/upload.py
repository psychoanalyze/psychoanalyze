import dash
from dash import html, dcc, Output, Input, State, dash_table
import dash_bootstrap_components as dbc
import base64
import pandas as pd
import io
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
        trials = pd.Series(
            data[data.columns[-1]],
            index=pd.MultiIndex.from_frame(data[data.columns[0:-1]]),
        )
        blocks = pa.blocks.from_trials(trials)
        subjects = pa.blocks.monkey_counts(blocks)
        output_data = subjects.to_frame().reset_index()
        return [dash_table.DataTable(output_data.to_dict("records"))]
