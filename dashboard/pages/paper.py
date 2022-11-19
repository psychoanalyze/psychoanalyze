import dash
from dash import dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

import psychoanalyze as pa


dash.register_page(__name__)

blocks = pd.read_csv("data/blocks.csv")
mask = blocks[["Amp2", "Width2", "Freq2", "Dur2"]].any(axis=1)
blocks.loc[mask, "Experiment Type"] = "Discrimination"
blocks.loc[~mask, "Experiment Type"] = "Detection"

summary = blocks[["Monkey", "Experiment Type"]]

layout = dbc.Container(
    dcc.Graph(
        figure=px.sunburst(
            summary,
            path=["Monkey", "Experiment Type"],
            template=pa.plot.template,
        )
    )
)
