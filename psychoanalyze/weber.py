import plotly.express as px
import pandas as pd


def plot(data):
    return px.scatter(
        data.reset_index(),
        x="Reference Charge (nC)",
        y="Difference Threshold (nC)",
        color="Monkey",
        symbol="Dimension",
        error_y="err_y",
    )


def aggregate(data):
    return data.groupby("Reference Charge (nC)").mean().reset_index()
