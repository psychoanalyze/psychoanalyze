import plotly.express as px
import pandas as pd
import psychoanalyze as pa
from plotly import graph_objects as go
from psychoanalyze.schemas import PsiAnimation
from pandera.typing import DataFrame

axis_settings = {
    "ticks": "outside",
    "showgrid": False,
    "showline": True,
    "zeroline": False,
    "title": {"font": {"size": 12, "family": "Arial"}},
}

template = go.layout.Template(
    layout=go.Layout(
        template="plotly_white",
        xaxis=axis_settings,
        yaxis=axis_settings,
        colorway=["#e41a1c", "#377eb8", "#4daf4a"],
        title={"font": {"size": 16, "family": "Arial"}},
        legend={"yanchor": "top", "y": 1, "xanchor": "left", "x": 0.98},
    ),
)

colormap = {"U": "#e41a1c", "Y": "#377eb8", "Z": "#4daf4a"}


def thresholds(df):
    df = pa.data.transform_errors(df)
    return px.scatter(
        df,
        x="Block",
        y="50%",
        error_y="err+",
        error_y_minus="err-",
        color="Subject",
        color_discrete_map=colormap,
        template=template,
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
        color_discrete_map=colormap,
        symbol=df.get("Block"),
        template=template,
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


def psi_animation(df: DataFrame[PsiAnimation]):
    return px.line(
        df,
        x="Intensity",
        y="Hit Rate",
        # error_y="err+",
        # error_y_minus="err-",
        # color=df.get("Subject") or df.get("Type"),
        # symbol=df.get("Block"),
        animation_group="Intensity",
        animation_frame="Trial",
        template=template,
    )


def posterior_animation(cumulative_draws: pd.DataFrame):
    df = cumulative_draws
    df = pa.data.transform_errors(df).reset_index()
    return px.scatter(
        df,
        x="x",
        y="Hit Rate",
        error_y="err+",
        error_y_minus="err-",
        animation_group="x",
        animation_frame="n",
        color=df.get("Subject"),
        symbol=df.get("Block"),
        template=template,
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
        color_discrete_map=colormap,
        symbol="Dimension",
        size="n",
        trendline="ols",
        template=template,
    )


labels = {
    "Amp": {
        "x": "Fixed Pulse Width (μs)",
        "y": {
            "inverse": "Threshold Amplitude (μA)",
            "linear": "Threshold Charge (nC)",
        },
    },
    "Width": {
        "x": "Fixed Amplitude (μA)",
        "y": {
            "inverse": "Threshold Pulse Width (μs)",
            "linear": "Threshold Charge (nC)",
        },
    },
}


def get_labels_given_dim(labels, dim, plot_type):
    return {"x": labels[dim]["x"], "y": labels[dim]["y"][plot_type]}


def strength_duration(
    data=None, dim=None, plot_type=None, x_data=[], y_data=[], points=None
):
    labels_given_dim = get_labels_given_dim(labels=labels, dim=dim, plot_type=plot_type)
    x = labels_given_dim["x"]
    y = labels_given_dim["y"]
    if data is not None:
        sd_df = pa.data.filter(data, dim=dim)
    else:
        sd_df = pd.DataFrame({x: x_data, y: y_data})
    return px.scatter(
        sd_df,
        x=x,
        y=y,
        template=template,
    )


def counts(sessions, dim=None):
    if dim is not None:
        sessions["Dimension"] = "Amp"
        sessions = sessions[sessions["Dimension"] == dim]
    return px.histogram(
        sessions,
        x="Monkey",
        color="Monkey",
        template=template,
    ).update_layout(yaxis_title_text="# of Sessions")


def ecdf(blocks, param):
    return px.ecdf(
        blocks.reset_index(), x=param, color=blocks.get("Monkey")
    ).update_layout(xaxis_title=param)


def psychometric(fit, x_range=(-3, 3)):
    s = pa.psi(fit["Threshold"], fit["width"], fit["lambda"], fit["gamma"], x_range)
    return px.line(s, template=pa.plot.template)


def combine_figs(fig1: go.Figure, fig2: go.Figure) -> go.Figure:
    return go.Figure(
        data=fig1.data + fig2.data,
        layout_xaxis_title_text="Stimulus Magnitude",
        layout_yaxis_title_text="Hit Rate",
        layout_template=pa.plot.template,
    )
