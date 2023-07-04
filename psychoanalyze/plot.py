"""Helper functions for common plot formats in psychophysics."""
import pandas as pd
import plotly.express as px
from pandera.typing import DataFrame
from plotly import graph_objects as go

from psychoanalyze import data
from psychoanalyze.data import dimension_filter
from psychoanalyze.schemas import PsiAnimation

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


def thresholds(blocks: pd.DataFrame) -> go.Figure:
    """Plot longitudinal threshold data."""
    return px.scatter(
        data.transform_errors(blocks),
        x="Block",
        y="50%",
        error_y="err+",
        error_y_minus="err-",
        color="Subject",
        color_discrete_map=colormap,
        template=template,
    )


def curves(curve_data: dict[str, pd.DataFrame]) -> go.Figure:
    """Maybe duplicate of thresholds."""
    curves = curve_data["curves_df"]
    y = curve_data["y"]
    return px.scatter(
        curves.reset_index(),
        x="x",
        y=y,
        error_y="err+",
        error_y_minus="err-",
        color=curves.get("Subject"),  # or df["Type"],
        color_discrete_map=colormap,
        symbol=curves.get("Block"),
        template=template,
    )


def logistic(points: pd.DataFrame) -> go.Figure:
    """Plot a logistic curve."""
    return px.line(
        points.reset_index(),
        x="x",
        y="Hit Rate",
        color=points.get("Type"),
        template="plotly_white",
    )


def bayes(simulated: pd.DataFrame, estimated: pd.Series) -> go.Figure:
    """Plot Psychometric curve to emphasize Bayesian posteriors."""
    combined = pd.concat(
        [simulated.reset_index(), estimated.reset_index()],
        keys=["Simulated", "Estimated"],
        names=["Type"],
    )
    return px.scatter(
        combined.reset_index(),
        x="x",
        y="Hit Rate",
        color="Type",
        template="plotly_white",
    )


def hits_animation(cumulative_draws: pd.DataFrame) -> go.Figure:
    """Plot raw hit count as animation."""
    return px.bar(
        cumulative_draws.reset_index(),
        x="x",
        y="Hits",
        animation_group="x",
        animation_frame="n",
        range_y=(0, max(cumulative_draws["Hits"])),
    )


def psi(points: pd.Series) -> go.Figure:
    """Plot a psychometric function."""
    return px.scatter(
        points.reset_index(),
        x="Intensity",
        y="Hit Rate",
        template="plotly_white",
    )


def psi_animation(df: DataFrame[PsiAnimation]) -> go.Figure:
    """Plot animation for psychometric plot as n trials grows."""
    return px.line(
        df,
        x="Intensity",
        y="Hit Rate",
        animation_group="Intensity",
        animation_frame="Trial",
        template=template,
    )


def posterior_animation(cumulative_draws: pd.DataFrame) -> go.Figure:
    """Plot animation of posterior data as n grows."""
    _cumulative_draws = data.transform_errors(cumulative_draws).reset_index()
    return px.scatter(
        _cumulative_draws,
        x="x",
        y="Hit Rate",
        error_y="err+",
        error_y_minus="err-",
        animation_group="x",
        animation_frame="n",
        color=_cumulative_draws.get("Subject"),
        symbol=_cumulative_draws.get("Block"),
        template=template,
    )


def difference_thresholds() -> go.Figure:
    """Plot difference thresholds. Might be duplicate of weber."""
    return px.scatter(
        pd.DataFrame(
            {
                "Reference Charge (nC)": [10.0, 20.0, 30.0],
                "Difference Threshold Charge (nC)": [0.1, 0.2, 0.3],
                "Monkey": ["U", "U", "U"],
                "Dimension": ["PW", "PW", "PW"],
                "n": [10, 7, 9],
            },
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
        "y": "Threshold Amplitude (μA)",
    },
    "Width": {
        "x": "Fixed Amplitude (μA)",
        "y": "Threshold Pulse Width (μs)",
    },
}


def get_labels_given_dim(labels: dict[str, dict[str, str]], dim: str) -> dict[str, str]:
    """Get appropriate axis labels for different choices of modulated dimension."""
    return {"x": labels[dim]["x"], "y": labels[dim]["y"]}


def strength_duration(
    blocks: pd.DataFrame,
    dim: str,
    x_data: list[float],
    y_data: list[float],
) -> go.Figure:
    """Plot strength-duration curve given detection data."""
    labels_given_dim = get_labels_given_dim(labels=labels, dim=dim)
    x = labels_given_dim["x"]
    y = labels_given_dim["y"]
    if blocks is not None:
        sd_df = dimension_filter(blocks, dim=dim)
    else:
        sd_df = pd.DataFrame({x: x_data, y: y_data})
    return px.scatter(
        sd_df,
        x=x,
        y=y,
        template=template,
    )


def counts(sessions: pd.DataFrame, dim: str) -> go.Figure:
    """Plot how many sessions are in the dataset."""
    if dim is not None:
        sessions["Dimension"] = "Amp"
        sessions = sessions[sessions["Dimension"] == dim]
    return px.histogram(
        sessions,
        x="Monkey",
        color="Monkey",
        template=template,
    ).update_layout(yaxis_title_text="# of Sessions")


def ecdf(blocks: pd.DataFrame, param: str) -> go.Figure:
    """Plot empirical cumulative distrubtion function (eCDF) of fitted params."""
    return px.ecdf(
        blocks.reset_index(),
        x=param,
        color=blocks.get("Monkey"),
    ).update_layout(xaxis_title=param)


def combine_figs(fig1: go.Figure, fig2: go.Figure) -> go.Figure:
    """Combine two plotly scatter plots."""
    return go.Figure(
        data=fig1.data + fig2.data,
        layout_xaxis_title_text="Stimulus Magnitude",
        layout_yaxis_title_text="Hit Rate",
        layout_template=template,
    )
