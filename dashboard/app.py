import dash_bootstrap_components as dbc
import numpy as np
from dash import Dash, Input, Output, callback
from scipy.special import expit

from dashboard.layout import layout
from psychoanalyze import plot, points

app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.BOOTSTRAP])

app.layout = layout

server = app.server


@callback(
    Output("plot", "figure"),
    Input("n-trials-per-level", "value"),
    Input("n-levels", "value"),
)
def update_data(n_levels: int):
    x = np.linspace(-4, 4, n_levels)
    df = points.generate(x=x, n=[10] * n_levels, p=expit(x))
    return plot.psi(df)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        debug=False,
    )
