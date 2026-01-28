
"""Global plot settings and generic plot utilities."""

import plotly.graph_objects as go

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
