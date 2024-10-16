# Copyright 2023 Tyler Schlichenmeyer

# This file is part of PsychoAnalyze.
# PsychoAnalyze is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# PsychoAnalyze is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# PsychoAnalyze. If not, see <https://www.gnu.org/licenses/>.

"""Tests for psychoanalyze.points module."""

import numpy as np
import pandas as pd
import plotly.express as px

from psychoanalyze.data import points as pa_points


def test_from_trials_sums_n_per_intensity_level():
    trials = pd.DataFrame(
        {
            "Result": [0, 0],
            "Intensity": [0.0, 1.0],
            "Block": [0, 0],
        },
    )
    points = pa_points.from_trials(trials)
    assert all(
        points["n trials"]
        == pd.Series(
            [1, 1],
            index=pd.Index([0.0, 1.0], name="Intensity"),
            name="n trials",
        ),
    )


def test_plot():
    points = pd.DataFrame(
        {"Hit Rate": [], "n": [], "Block": []},
        index=pd.Index([], name="Intensity"),
    )
    fig = pa_points.plot(points, y="Hit Rate")
    assert fig.layout.yaxis.title.text == "Hit Rate"
    assert fig.layout.xaxis.title.text == "Intensity"


def test_generate():
    x = list(np.linspace(-3, 3, 7))
    points = pa_points.generate(
        n_trials=70,
        options=x,
        params={
            "Threshold": 0.0,
            "Slope": 1.0,
            "Guess Rate": 0.0,
            "Lapse Rate": 0.0,
        },
    )
    assert set(points.index) == set(x)
    assert set(points.columns) >= {"Hits", "n", "Hit Rate"}
    assert points.index.name == "Intensity"


def test_datatable():
    data = pd.DataFrame(
        index=pd.MultiIndex.from_frame(
            pd.DataFrame({"Amp1": [0.1212345], "Hit Rate": [0.1234543], "n": [1]}),
        ),
    )
    datatable = pa_points.datatable(data)
    amp_column = [column for column in datatable.columns if column["name"] == "Amp1"]
    assert amp_column[0]["format"].to_plotly_json()["specifier"] == ".2f"


def test_combine_plots():
    data1 = pd.DataFrame({"A": [1]})
    data2 = pd.DataFrame({"B": [1]})
    plot1 = px.scatter(data1)
    plot2 = px.line(data2)
    fig = pa_points.combine_plots(plot1, plot2)
    assert len(fig.data) == len(data1) + len(data2)
