from dash import Dash, html
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])

app.layout = dbc.Container(html.H1("Psychoanalyze"))

if __name__ == "__main__":
    app.run_server(debug=True)
