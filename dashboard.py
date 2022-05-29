from dash import Dash, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import psychoanalyze as pa

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])

data = pd.DataFrame({"Threshold": [1, 2]}, index=pd.Index(["A", "B"], name="Subject"))

app.layout = dbc.Container(
    [
        dbc.Input(id="subjects", value=2, type="number"),
        dcc.Graph(id="time-thresholds", figure=pa.plot.thresholds(data)),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
