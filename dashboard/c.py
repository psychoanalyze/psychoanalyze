from dash import Dash, dcc  # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
import plotly.express as px  # type: ignore
import pandas as pd

import psychoanalyze as pa

blocks = pd.read_csv("data/blocks.csv")
blocks["Experiment Type"] = pa.blocks.experiment_type(blocks)

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
app.layout = dbc.Container(
    dcc.Graph(
        figure=px.bar(
            blocks, x="Experiment Type", color="Monkey", template=pa.plot.template
        )
    )
)


if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
