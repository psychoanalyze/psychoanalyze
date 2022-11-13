import dash
import dash_bootstrap_components as dbc


dash.register_page(__name__, path="/upload")

layout = dbc.Container(
    [
        dash.dcc.Upload(
            ["Drag and Drop or ", dash.html.A("Select a File")],
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
    ]
)
