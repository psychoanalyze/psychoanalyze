import plotly.express as px
import pandas as pd
import psychoanalyze as pa


def thresholds(df):
    df = pa.data.transform_errors(df)
    return px.scatter(
        df,
        x="Day",
        y="50%",
        error_y="err+",
        error_y_minus="err-",
        color="Subject",
        template="plotly_white",
    )


def curves(curve_data):
    df = curve_data["curves_df"]
    y = curve_data["y"]
    if "5%" in df.columns:
        df = pa.data.transform_errors(df)
    df = df.reset_index()
    return px.scatter(
        df,
        x="x",
        y=y,
        error_y="err+",
        error_y_minus="err-",
        color=df.get("Subject"),  # or df["Type"],
        symbol=df.get("Day"),
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


def hits_animation(cumulative_draws: pd.DataFrame):
    df = cumulative_draws
    return px.bar(
        df.reset_index(),
        x="x",
        y="Hits",
        animation_group="x",
        animation_frame="n",
        range_y=(0, max(df["Hits"])),
    )


def hit_rate_animation(cumulative_draws: pd.DataFrame):
    df = cumulative_draws.reset_index()
    return px.scatter(
        df,
        x="x",
        y="Hit Rate",
        error_y="err+",
        error_y_minus="err-",
        color=df.get("Subject") or df.get("Type"),
        symbol=df.get("Day"),
        animation_group="x",
        animation_frame="n",
        template="plotly_white",
    )


def posterior_animation(cumulative_draws: pd.DataFrame):
    df = cumulative_draws
    df = pa.data.transform_errors(df, "50%").reset_index()
    return px.scatter(
        df,
        x="x",
        y="Hit Rate",
        error_y="err+",
        error_y_minus="err-",
        animation_group="x",
        animation_frame="n",
        color=df.get("Subject"),
        symbol=df.get("Day"),
        template="plotly_white",
    )


def difference_thresholds():
    return px.scatter(
        pd.DataFrame(
            {
                "Reference Charge (nC)": [10.0, 20.0, 30.0],
                "Difference Threshold Charge (nC)": [0.1, 0.2, 0.3],
                "Monkey": ["U", "U", "U"],
                "Dimension": ["PW", "PW", "PW"],
                "n": [10, 7, 9],
            }
        ),
        x="Reference Charge (nC)",
        y="Difference Threshold Charge (nC)",
        color="Monkey",
        symbol="Dimension",
        size="n",
        trendline="ols",
        template="plotly_white",
    )
