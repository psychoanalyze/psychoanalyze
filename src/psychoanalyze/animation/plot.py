"""Visualization functions for animated PyMC sampling.

This module provides plotting functions to visualize:
- Trace evolution over sampling draws
- Posterior distribution updates
- Psychometric curve fitting animation
- Parameter convergence
"""
from typing import Any

import altair as alt
import numpy as np
import plotly.graph_objects as go
import polars as pl
from plotly.subplots import make_subplots
from scipy.special import expit

from psychoanalyze.animation.sampler import AnimatedSampler, SamplerSnapshot


def plot_trace_evolution(
    sampler: AnimatedSampler,
    param_name: str = "threshold",
    chain: int = 0,
    up_to_draw: int | None = None,
) -> go.Figure:
    """Plot trace evolution for a parameter.
    
    Args:
        sampler: AnimatedSampler with completed sampling.
        param_name: Parameter name to plot.
        chain: Chain number to display.
        up_to_draw: Maximum draw to include. If None, plots all draws.
    
    Returns:
        Plotly figure showing trace evolution.
    """
    df = sampler.get_parameter_evolution(param_name, chain=chain)
    
    if up_to_draw is not None:
        df = df.filter(pl.col("draw") <= up_to_draw)
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["draw"].to_list(),
            y=df["value"].to_list(),
            mode="lines",
            name=param_name,
            line={"color": "steelblue", "width": 1},
        ),
    )
    
    fig.update_layout(
        title=f"Trace: {param_name} (Chain {chain})",
        xaxis_title="Draw",
        yaxis_title=param_name,
        template="plotly_white",
        hovermode="x unified",
    )
    
    return fig


def plot_posterior_evolution(
    sampler: AnimatedSampler,
    param_name: str = "threshold",
    chain: int = 0,
    up_to_draw: int | None = None,
    n_bins: int = 30,
) -> go.Figure:
    """Plot histogram of posterior samples up to a specific draw.
    
    Args:
        sampler: AnimatedSampler with completed sampling.
        param_name: Parameter name to plot.
        chain: Chain number.
        up_to_draw: Maximum draw to include. If None, uses all draws.
        n_bins: Number of histogram bins.
    
    Returns:
        Plotly figure showing posterior distribution.
    """
    df = sampler.get_parameter_evolution(param_name, chain=chain)
    
    if up_to_draw is not None:
        df = df.filter(pl.col("draw") <= up_to_draw)
    
    values = df["value"].to_numpy()
    
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=values,
            nbinsx=n_bins,
            name=param_name,
            marker={"color": "steelblue", "line": {"color": "white", "width": 1}},
        ),
    )
    
    # Add vertical line at mean
    mean_val = float(np.mean(values))
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: {mean_val:.3f}",
    )
    
    fig.update_layout(
        title=f"Posterior: {param_name} (Draw {up_to_draw or len(df)} / Chain {chain})",
        xaxis_title=param_name,
        yaxis_title="Count",
        template="plotly_white",
        showlegend=False,
    )
    
    return fig


def plot_psychometric_curve_evolution(
    sampler: AnimatedSampler,
    trials: pl.DataFrame,
    up_to_draw: int | None = None,
    chain: int = 0,
    n_curves: int = 50,
) -> go.Figure:
    """Plot psychometric curve with uncertainty from samples.
    
    Shows how the fitted curve evolves as more posterior samples are collected.
    
    Args:
        sampler: AnimatedSampler with completed sampling.
        trials: Original trial data for scatter plot.
        up_to_draw: Maximum draw to include.
        chain: Chain number.
        n_curves: Number of sample curves to plot.
    
    Returns:
        Plotly figure with psychometric curves.
    """
    # Get trace data up to the specified draw
    traces = sampler.get_trace_data(up_to_draw)
    
    # Extract samples for the specified chain
    intercepts = traces["intercept"][chain, :]
    slopes = traces["slope"][chain, :]
    
    # Sample subset of curves for plotting
    n_samples = len(intercepts)
    if n_samples > n_curves:
        indices = np.linspace(0, n_samples - 1, n_curves, dtype=int)
        intercepts = intercepts[indices]
        slopes = slopes[indices]
    
    # Generate x range
    x_min = float(trials["Intensity"].min())
    x_max = float(trials["Intensity"].max())
    x_range = x_max - x_min
    x = np.linspace(x_min - 0.2 * x_range, x_max + 0.2 * x_range, 100)
    
    fig = go.Figure()
    
    # Plot sample curves
    for intercept, slope in zip(intercepts, slopes):
        y = expit(intercept + slope * x)
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                line={"color": "steelblue", "width": 0.5},
                opacity=0.1,
                showlegend=False,
                hoverinfo="skip",
            ),
        )
    
    # Plot mean curve
    mean_intercept = float(np.mean(intercepts))
    mean_slope = float(np.mean(slopes))
    y_mean = expit(mean_intercept + mean_slope * x)
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y_mean,
            mode="lines",
            line={"color": "red", "width": 2},
            name="Mean Curve",
        ),
    )
    
    # Add trial data points
    points_df = (
        trials.group_by("Intensity")
        .agg([pl.col("Result").sum().alias("Hits"), pl.len().alias("n")])
        .with_columns((pl.col("Hits") / pl.col("n")).alias("Hit Rate"))
    )
    
    fig.add_trace(
        go.Scatter(
            x=points_df["Intensity"].to_list(),
            y=points_df["Hit Rate"].to_list(),
            mode="markers",
            marker={"size": points_df["n"].to_list(), "color": "black", "sizemode": "area", "sizeref": 0.5},
            name="Data",
        ),
    )
    
    fig.update_layout(
        title=f"Psychometric Curve Evolution (Draw {up_to_draw or n_samples} / Chain {chain})",
        xaxis_title="Intensity",
        yaxis_title="Hit Rate",
        template="plotly_white",
        hovermode="x unified",
    )
    
    return fig


def plot_multi_chain_traces(
    sampler: AnimatedSampler,
    param_name: str = "threshold",
    up_to_draw: int | None = None,
) -> go.Figure:
    """Plot traces for all chains to visualize convergence.
    
    Args:
        sampler: AnimatedSampler with completed sampling.
        param_name: Parameter name to plot.
        up_to_draw: Maximum draw to include.
    
    Returns:
        Plotly figure with multiple chain traces.
    """
    fig = go.Figure()
    
    colors = ["steelblue", "orange", "green", "red"]
    
    for chain in range(sampler.chains):
        df = sampler.get_parameter_evolution(param_name, chain=chain)
        
        if up_to_draw is not None:
            df = df.filter(pl.col("draw") <= up_to_draw)
        
        fig.add_trace(
            go.Scatter(
                x=df["draw"].to_list(),
                y=df["value"].to_list(),
                mode="lines",
                name=f"Chain {chain}",
                line={"color": colors[chain % len(colors)], "width": 1},
            ),
        )
    
    fig.update_layout(
        title=f"Multi-Chain Traces: {param_name}",
        xaxis_title="Draw",
        yaxis_title=param_name,
        template="plotly_white",
        hovermode="x unified",
    )
    
    return fig


def plot_sampling_dashboard(
    sampler: AnimatedSampler,
    trials: pl.DataFrame,
    up_to_draw: int | None = None,
    chain: int = 0,
) -> go.Figure:
    """Create a comprehensive dashboard with multiple views.
    
    Args:
        sampler: AnimatedSampler with completed sampling.
        trials: Original trial data.
        up_to_draw: Maximum draw to include.
        chain: Chain number.
    
    Returns:
        Plotly figure with subplots.
    """
    # Create subplots
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Threshold Trace",
            "Slope Trace",
            "Threshold Posterior",
            "Psychometric Curve",
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "histogram"}, {"type": "scatter"}],
        ],
    )
    
    # Get parameter evolution
    threshold_df = sampler.get_parameter_evolution("threshold", chain=chain)
    slope_df = sampler.get_parameter_evolution("slope", chain=chain)
    
    if up_to_draw is not None:
        threshold_df = threshold_df.filter(pl.col("draw") <= up_to_draw)
        slope_df = slope_df.filter(pl.col("draw") <= up_to_draw)
    
    # Threshold trace
    fig.add_trace(
        go.Scatter(
            x=threshold_df["draw"].to_list(),
            y=threshold_df["value"].to_list(),
            mode="lines",
            name="Threshold",
            line={"color": "steelblue"},
        ),
        row=1,
        col=1,
    )
    
    # Slope trace
    fig.add_trace(
        go.Scatter(
            x=slope_df["draw"].to_list(),
            y=slope_df["value"].to_list(),
            mode="lines",
            name="Slope",
            line={"color": "orange"},
        ),
        row=1,
        col=2,
    )
    
    # Threshold posterior
    fig.add_trace(
        go.Histogram(
            x=threshold_df["value"].to_numpy(),
            name="Threshold Dist",
            marker={"color": "steelblue"},
            showlegend=False,
        ),
        row=2,
        col=1,
    )
    
    # Psychometric curve with data
    traces = sampler.get_trace_data(up_to_draw)
    intercepts = traces["intercept"][chain, :]
    slopes = traces["slope"][chain, :]
    
    mean_intercept = float(np.mean(intercepts))
    mean_slope = float(np.mean(slopes))
    
    x_min = float(trials["Intensity"].min())
    x_max = float(trials["Intensity"].max())
    x_range = x_max - x_min
    x = np.linspace(x_min - 0.2 * x_range, x_max + 0.2 * x_range, 100)
    y = expit(mean_intercept + mean_slope * x)
    
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            name="Fitted Curve",
            line={"color": "red"},
        ),
        row=2,
        col=2,
    )
    
    # Add data points
    points_df = (
        trials.group_by("Intensity")
        .agg([pl.col("Result").sum().alias("Hits"), pl.len().alias("n")])
        .with_columns((pl.col("Hits") / pl.col("n")).alias("Hit Rate"))
    )
    
    fig.add_trace(
        go.Scatter(
            x=points_df["Intensity"].to_list(),
            y=points_df["Hit Rate"].to_list(),
            mode="markers",
            name="Data",
            marker={"color": "black"},
        ),
        row=2,
        col=2,
    )
    
    fig.update_xaxes(title_text="Draw", row=1, col=1)
    fig.update_xaxes(title_text="Draw", row=1, col=2)
    fig.update_xaxes(title_text="Threshold", row=2, col=1)
    fig.update_xaxes(title_text="Intensity", row=2, col=2)
    
    fig.update_yaxes(title_text="Threshold", row=1, col=1)
    fig.update_yaxes(title_text="Slope", row=1, col=2)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    fig.update_yaxes(title_text="Hit Rate", row=2, col=2)
    
    fig.update_layout(
        height=800,
        showlegend=False,
        template="plotly_white",
        title_text=f"Sampling Dashboard (Draw {up_to_draw or len(threshold_df)} / Chain {chain})",
    )
    
    return fig


def create_altair_trace_animation(
    sampler: AnimatedSampler,
    param_name: str = "threshold",
    chain: int = 0,
) -> alt.Chart:
    """Create an Altair chart with animation capabilities.
    
    Args:
        sampler: AnimatedSampler with completed sampling.
        param_name: Parameter name to plot.
        chain: Chain number.
    
    Returns:
        Altair chart with slider for animation.
    """
    df = sampler.get_parameter_evolution(param_name, chain=chain)
    df_pd = df.to_pandas()
    
    # Create base chart
    base = alt.Chart(df_pd).encode(
        x=alt.X("draw:Q", title="Draw"),
        y=alt.Y("value:Q", title=param_name),
    )
    
    # Line chart
    line = base.mark_line(color="steelblue")
    
    # Points chart
    points = base.mark_point(size=50, color="red", filled=True)
    
    # Add selection for interactivity
    slider = alt.binding_range(min=0, max=len(df), step=1, name="Draw: ")
    select_draw = alt.selection_point(
        name="draw_selection",
        fields=["draw"],
        bind=slider,
        value=len(df),
    )
    
    # Filter data based on slider
    filtered = points.add_params(select_draw).transform_filter(
        alt.datum.draw <= select_draw.draw,
    )
    
    chart = (line + filtered).properties(
        width=600,
        height=300,
        title=f"Trace Animation: {param_name} (Chain {chain})",
    )
    
    return chart
