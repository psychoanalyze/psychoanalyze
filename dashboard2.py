from dash import Dash, dcc, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import psychoanalyze as pa


app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
app.layout = dbc.Container(
    dcc.RadioItems(["U", "Y", "Z"], "Z", id="monkey"), dcc.Slider(id="day")
)


@app.callback(Output("day", "marks"), Input("monkey", "value"))
def day_marks(monkey):
    return pa.sessions.day_marks(monkey)


if __name__ == "__main__":
    app.run_server(debug=True)
