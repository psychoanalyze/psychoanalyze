import plotly.express as px
import pandas as pd


def thresholds(df):
    df["err+"] = df["95%"] - df["50%"]
    df["err-"] = df["50%"] - df["5%"]
    df = df.drop(columns=["95%", "5%"])
    return px.scatter(
        df,
        x="Day",
        y="50%",
        error_y="err+",
        error_y_minus="err-",
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


def linear_curves(points: pd.DataFrame):
    df = points
    df["err+"] = df["95%"] - df["50%"]
    df["err-"] = df["50%"] - df["5%"]
    df = df.drop(columns=["95%", "5%"]).reset_index()
    return px.scatter(
        df,
        x="x",
        y="50%",
        error_y="err+",
        error_y_minus="err-",
        color="Subject",
        symbol="Day",
        template="plotly_white",
    )


def logistic(data):
    df = data.reset_index()
    return px.line(
        df, x="x", y="Hit Rate", color=df.get("Type"), template="plotly_white"
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
