# Copyright 2023 Tyler Schlichenmeyer

# This file is part of PsychoAnalyze.
# PsychoAnalyze is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# PsychoAnalyze is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with Foobar.
# If not, see <https://www.gnu.org/licenses/>.

"""Visualize psychophysical data and metrics."""
import pandas as pd
import plotly.express as px
from plotly import graph_objects as go

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
