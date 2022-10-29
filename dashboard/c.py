from dash import Dash, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

import psychoanalyze as pa

blocks = pd.read_csv("data/blocks.csv")
blocks["Experiment Type"] = pa.blocks.experiment_type(blocks)

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
app.layout = dbc.Container(
    dcc.Graph(figure=px.bar(blocks, x="Experiment Type", color="Monkey"))
)


if __name__ == "__main__":
    app.run_server(debug=True)
