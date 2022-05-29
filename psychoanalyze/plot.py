import plotly.express as px
import pandas as pd


def thresholds(data):
    return px.scatter(
        data.reset_index(),
        x="Day",
        y="Threshold",
        color="Subject",
        template="plotly_white",
    )


def curve(points):
    return px.scatter(points, y="Hit Rate", template="plotly_white")


def curves(points):
    return px.scatter(
        points.reset_index(),
        x="x",
        y="Hit Rate",
        color="Subject",
        template="plotly_white",
    )
