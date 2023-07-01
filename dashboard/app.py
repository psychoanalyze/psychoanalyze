import dash_bootstrap_components as dbc
from dash import Dash

from dashboard.layout import layout

app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.BOOTSTRAP])

app.layout = layout

server = app.server

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        debug=False,
    )
