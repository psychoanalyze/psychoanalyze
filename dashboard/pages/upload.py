import dash
from dash import html, dcc, Output, Input
import dash_bootstrap_components as dbc
import base64
import pandas as pd
import io


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
)
def show_contents(contents):
    if contents is not None:
        _, contents = contents.split(",")
        blocks = pd.read_csv(io.StringIO(base64.b64decode(contents).decode("utf-8")))
        # blocks = trials[
        #     [
        #         "Monkey",
        #         "Date",
        #         "Amp2",
        #         "Width2",
        #         "Freq2",
        #         "Dur2",
        #         "Active Channels",
        #         "Return Channels",
        #     ]
        # ].drop_duplicates()
        subjects = blocks["Monkey"].value_counts().to_frame()
        return dash.dash_table.DataTable(subjects.to_dict("records"))
        # return html.Div(dcc.Graph(figure=px.bar(subjects)))
