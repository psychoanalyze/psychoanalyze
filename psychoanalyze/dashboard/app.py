from dash import Dash
import dash_bootstrap_components as dbc
from .layout import layout

app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.BOOTSTRAP])

app.layout = layout

server = app.server
