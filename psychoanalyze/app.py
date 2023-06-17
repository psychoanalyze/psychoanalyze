from dash import Dash
import dash_bootstrap_components as dbc
import psychoanalyze as pa

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.BOOTSTRAP],
    add_log_handler=True,
)
server = app.server

app.layout = pa.layout.layout

if __name__ == "__main__":
    app.run(
        host="localhost",
        debug=True,
    )
