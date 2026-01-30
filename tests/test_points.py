
"""Tests for psychoanalyze.points module."""

import numpy as np
import plotly.express as px
import polars as pl

from psychoanalyze.data import points as pa_points


def test_from_trials_sums_n_per_intensity_level():
    trials = pl.DataFrame(
        {
            "Result": [0, 0],
            "Intensity": [0.0, 1.0],
            "Block": [0, 0],
        },
    )
    points = pa_points.from_trials(trials)
    n_trials_values = points.sort("Intensity")["n trials"].to_list()
    assert n_trials_values == [1, 1]


def test_plot():
    points = pl.DataFrame(
        {"Intensity": [], "Hit Rate": [], "n": [], "Block": []},
    ).cast(
        {
            "Intensity": pl.Float64,
            "Hit Rate": pl.Float64,
            "n": pl.Int64,
            "Block": pl.Int64,
        }
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
    assert set(points["Intensity"].to_list()) == set(x)
    assert set(points.columns) >= {"Hits", "n", "Hit Rate", "Intensity"}


def test_datatable():
    data = pl.DataFrame(
        {"Amp1": [0.1212345], "Hit Rate": [0.1234543], "n": [1]},
    )
    datatable = pa_points.datatable(data)
    amp_column = [column for column in datatable.columns if column["name"] == "Amp1"]
    assert amp_column[0]["format"].to_plotly_json()["specifier"] == ".2f"


def test_combine_plots():
    data1 = pl.DataFrame({"A": [1]})
    data2 = pl.DataFrame({"B": [1]})
    plot1 = px.scatter(data1.to_pandas())
    plot2 = px.line(data2.to_pandas())
    fig = pa_points.combine_plots(plot1, plot2)
    assert len(fig.data) == len(data1) + len(data2)
