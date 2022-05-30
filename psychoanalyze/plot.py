import plotly.express as px
import pandas as pd


def thresholds(data):
    return px.scatter(
        data,
        x="Day",
        y="mu",
        color="Subject",
        template="plotly_white",
    )


def curves(points):
    return px.scatter(
        points.reset_index(),
        x="x",
        y="Hit Rate",
        color="Subject",
        symbol="Day",
        template="plotly_white",
    )


def logistic(data):
    return px.line(
        data.reset_index(), x="x", y="Hit Rate", color="Type", template="plotly_white"
    )


def bayes(simulated, estimated):
    estimated = estimated.to_frame().rename(columns={"50%": "Hit Rate"})
    df = pd.concat(
        [simulated.reset_index(), estimated.reset_index()],
        keys=["Simulated", "Estimated"],
        names=["Type"],
    )
    return px.scatter(
        df.reset_index(), x="x", y="Hit Rate", color="Type", template="plotly_white"
    )
