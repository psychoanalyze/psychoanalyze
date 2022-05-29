from dash import Dash, dcc
import dash_bootstrap_components as dbc
import psychoanalyze as pa

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])

app.layout = dbc.Container(
    [
        dbc.Input(id="subjects", placeholder="# of subjects", type="number"),
        dcc.Graph(id="time-thresholds", figure=pa.thresholds()),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
