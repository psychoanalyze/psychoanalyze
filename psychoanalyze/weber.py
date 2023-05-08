import plotly.express as px
import psychoanalyze as pa
import pandas as pd


def plot(
    data,
    trendline="ols",
    group_x=None,
    log_scale=True,
    marginal=None,
    error_y=None,
    stable_sessions=None,
):
    if stable_sessions == "stable":
        data = data[data["Date"].between("6/19/2017", "8/16/2017")]
    if group_x:
        data = pa.weber.aggregate(data)
    _log_scale = True if log_scale == "Log Scale" else None
    _marginal = "histogram" if marginal == "Histogram" else None
    _trendline = "ols" if trendline else None
    return px.scatter(
        data.reset_index(),
        x="Reference Charge (nC)",
        y="Difference Threshold (nC)",
        error_y="err+" if error_y == "error bars" else None,
        error_y_minus="err-" if error_y == "error bars" else None,
        color="Monkey",
        color_discrete_map=pa.plot.colormap,
        symbol="Dimension",
        trendline=_trendline,
        template="plotly_white",
        log_x=_log_scale,
        trendline_options={"log_x": _log_scale},
        marginal_x=_marginal,
        hover_data=["Date"],
    )


def aggregate(data):
    return (
        data.groupby(["Monkey", "Dimension", "Reference Charge (nC)"])[
            "Difference Threshold (nC)"
        ]
        .agg(["mean", "count", "std"])
        .rename(columns={"mean": "Difference Threshold (nC)"})
    )


def load(path):
    df = pd.read_csv(path, parse_dates=["Date"])
    df["err+"] = (df["location_CI_5"] * df["Fixed_Param_Value"] / 1000) - df[
        "Threshold_Charge_nC"
    ]
    df["err-"] = (
        df["Threshold_Charge_nC"]
        - (df["location_CI_95"]) * df["Fixed_Param_Value"] / 1000
    )
    return df
