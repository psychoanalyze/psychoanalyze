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

"""Tests for psychoanalyze.plot module."""
import pandas as pd
import plotly.express as px

from psychoanalyze import data, plot


def test_thresholds() -> None:
    """Tests threshold plot."""
    data = pd.DataFrame(
        {
            "Subject": ["A", "B"],
            "5%": [1, 2],
            "50%": [1, 2],
            "95%": [1, 2],
            "Block": [1, 2],
        },
    )
    fig = plot.thresholds(data)
    subjects = {trace["legendgroup"] for trace in fig.data}
    assert subjects == {"A", "B"}
    assert fig.layout.xaxis.title.text == "Block"
    assert fig.layout.yaxis.title.text == "50%"


def test_standard_logistic() -> None:
    """Tests plotting the standard logistic function."""
    s = data.logistic()
    logistic = s.to_frame()
    logistic["Type"] = "Generated"
    fig = plot.logistic(logistic)
    assert fig.layout.xaxis.title.text == "x"
    assert fig.layout.yaxis.title.text == "Hit Rate"


def test_combine_logistics() -> None:
    """Tests multiple logistic curves."""
    s1 = data.logistic(threshold=0)
    s2 = data.logistic(threshold=1)
    s = [s1, s2]
    combined = pd.concat(s, keys=["0", "1"], names=["Type"])
    assert len(plot.logistic(combined.reset_index()).data) == len(s)


def test_bayes() -> None:
    """Test plotting bayesian representation of psi data."""
    simulated = pd.DataFrame(
        {
            "x": [-4, -2, 0, 2, 4],
            "Hit Rate": [0.01, 0.19, 0.55, 0.81, 0.99],
        },
    )
    index = pd.Index([-4, -2, 0, 2, 4], name="Hit Rate")
    estimated = pd.Series([0.011, 0.2, 0.56, 0.80, 0.98], index=index)
    fig = plot.bayes(simulated, estimated)
    assert fig.layout.xaxis.title.text == "x"
    assert fig.layout.yaxis.title.text == "Hit Rate"


def test_curves() -> None:
    """Tests plotting curves."""
    curves_data = {
        "curves_df": pd.DataFrame(
            {"p": [], "err+": [], "err-": []},
            index=pd.Index([], name="x"),
        ),
    }
    assert plot.curves(curves_data)


def test_strength_duration() -> None:
    """Tests strength-duration plot."""
    fig = plot.strength_duration(
        dim="Amp",
        blocks=pd.DataFrame(
            {
                "Dimension": [],
                "Fixed Amplitude (μA)": [],
                "Threshold Pulse Width (μs)": [],
                "Fixed Pulse Width (μs)": [],
                "Threshold Amplitude (μA)": [],
            },
        ),
        x_data=[],
        y_data=[],
    )
    assert fig.layout.xaxis.title.text == "Fixed Pulse Width (μs)"
    assert fig.layout.yaxis.title.text == "Threshold Amplitude (μA)"


def test_strength_duration_with_data() -> None:
    """Test strenght-duration plot with data."""
    x_data = [1.0]
    y_data = [1.0]
    fig = plot.strength_duration(
        dim="Width",
        blocks=pd.DataFrame(
            {
                "Dimension": [],
                "Fixed Amplitude (μA)": [],
                "Threshold Pulse Width (μs)": [],
            },
        ),
        x_data=x_data,
        y_data=y_data,
    )
    assert len(fig.data) == 1


def test_plot_counts() -> None:
    """Test plot for session counts."""
    sessions = pd.DataFrame(
        {"Monkey": ["U", "U"], "Block": [1, 2], "Dimension": ["Amp", "Amp"]},
    )
    fig = plot.counts(sessions, dim="Width")
    assert fig.layout.yaxis.title.text == "# of Sessions"


def test_plot_counts_dim_facet() -> None:
    """Test facet plot for block counts."""
    sessions = pd.DataFrame(
        {"Monkey": ["U", "U"], "Block": [1, 2], "Dimension": ["Amp", "Width"]},
    )
    figs = plot.counts(sessions, dim="Amp")
    assert len(figs.data)


def test_ecdf_location_no_data() -> None:
    """Test ecdf location for no data."""
    blocks = pd.DataFrame({"location": []})
    ecdf_fig = plot.ecdf(blocks, "location")
    assert ecdf_fig.layout.xaxis.title.text == "location"


def test_ecdf_width_no_data() -> None:
    """Test ecdf with no data."""
    blocks = pd.DataFrame({"width": []})
    ecdf_fig = plot.ecdf(blocks, "width")
    assert ecdf_fig.layout.xaxis.title.text == "width"


def test_combine_line_and_scatter() -> None:
    """Test combining line and scatter Plotly plots."""
    data1 = pd.DataFrame(
        {"Stimulus Magnitude": [0], "Hit Rate": [0.5]},
    )
    data2 = pd.DataFrame({"Stimulus Magnitude": [0], "Hit Rate": [0.5]})
    fig1 = px.scatter(
        data1,
        x="Stimulus Magnitude",
        y="Hit Rate",
    )
    fig2 = px.line(
        data2,
        x="Stimulus Magnitude",
        y="Hit Rate",
    )
    fig = plot.combine_figs(fig1, fig2)
    assert fig.layout.xaxis.title.text == "Stimulus Magnitude"
    assert fig.layout.yaxis.title.text == "Hit Rate"
    assert len(fig.data) == len(data1) + len(data2)


def test_psi() -> None:
    """Test psychometric function plot."""
    assert plot.psi(
        pd.Series([], name="Hit Rate", index=pd.Index([], name="Intensity")),
    )
