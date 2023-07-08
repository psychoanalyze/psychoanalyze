"""Tests for psychoanalyze.points module."""

import numpy as np
import pandas as pd
import plotly.express as px
from scipy.special import expit

from psychoanalyze.data import points


def test_from_trials_sums_n_per_intensity_level() -> None:
    """Might be same as aggregate function."""
    trials = pd.DataFrame(
        {
            "Result": [0, 0],
        },
        index=pd.Index([0, 1], name="Intensity"),
    )
    _points = points.from_trials(trials)
    assert all(
        _points["n"]
        == pd.Series([1, 1], index=pd.Index([0, 1], name="Intensity"), name="n"),
    )


def test_amp_dimension() -> None:
    """Given points data, detect that it's amp-modulation data."""
    _points = pd.DataFrame(
        index=pd.MultiIndex.from_frame(
            pd.DataFrame({"Amp1": [1, 2], "Width1": [1, 1]}),
        ),
    )
    assert points.dimension(_points) == "Amp"


def test_width_dimension() -> None:
    """Given points data, detect that it's pw-modulation data."""
    _points = pd.DataFrame(
        index=pd.MultiIndex.from_frame(
            pd.DataFrame({"Amp1": [1, 1], "Width1": [1, 2]}),
        ),
    )
    assert points.dimension(_points) == "Width"


def test_both_dimensions() -> None:
    """Given points data, detect that it's amp-modulation data."""
    _points = pd.DataFrame(
        index=pd.MultiIndex.from_frame(
            pd.DataFrame({"Amp1": [1, 2], "Width1": [1, 2]}),
        ),
    )
    assert points.dimension(_points) == "Both"


def test_plot() -> None:
    """Test psi plot labels."""
    _points = pd.DataFrame(
        {"Intensity": [], "Hit Rate": []},
    )
    fig = points.plot(_points)
    assert fig.layout.yaxis.title.text == "Hit Rate"
    assert fig.layout.xaxis.title.text == "Intensity"


def test_generate() -> None:
    """Test generation of points data has right values and labels."""
    x = list(np.linspace(-3, 3, 7))
    n = [10] * 7
    p = expit(x)
    _points = points.generate(x, n, p)
    assert all(_points.index.to_numpy() == x)
    assert _points.name == "Hit Rate"
    assert _points.index.name == "Intensity"


def test_datatable() -> None:
    """Test format of datatable from points data."""
    data = pd.DataFrame(
        index=pd.MultiIndex.from_frame(
            pd.DataFrame({"Amp1": [0.1212345], "Hit Rate": [0.1234543], "n": [1]}),
        ),
    )
    datatable = points.datatable(data)
    amp_column = [column for column in datatable.columns if column["name"] == "Amp1"]
    assert amp_column[0]["format"].to_plotly_json()["specifier"] == ".2f"


def test_combine_plots() -> None:
    """Combines two plotly scatter plots into one figure."""
    data1 = pd.DataFrame({"A": [1]})
    data2 = pd.DataFrame({"B": [1]})
    plot1 = px.scatter(data1)
    plot2 = px.line(data2)
    fig = points.combine_plots(plot1, plot2)
    assert len(fig.data) == len(data1) + len(data2)


def test_no_dimension() -> None:
    """Given points data, detect that it's amp-modulation data."""
    session_cols = ["Monkey", "Date"]
    ref_stim_cols = ["Amp2", "Width2", "Freq2", "Dur2"]
    channel_config = ["Active Channels", "Return Channels"]
    test_stim_cols = ["Amp1", "Width1", "Freq1", "Dur1"]
    _points = pd.DataFrame(
        {"n": [], "Hits": []},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {
                    field: []
                    for field in session_cols
                    + ref_stim_cols
                    + channel_config
                    + test_stim_cols
                },
            ),
        ),
    )
    dimension = points.dimension(_points)
    assert dimension == "Neither"
