
"""Tests for psychoanalyze.strength_duration module."""

import polars as pl
import pytest

from psychoanalyze.analysis import strength_duration


@pytest.fixture
def s_d_columns() -> set:
    """Columns needed for a strength-duration dataframe."""
    return {"Monkey", "Block", "Dimension"}


def test_strength_duration() -> None:
    """Test strength_duration construction."""
    blocks = pl.DataFrame(
        {
            "Monkey": [],
            "Block": [],
            "Dimension": [],
            "Fixed Magnitude": [],
            "Threshold": [],
        },
    ).cast(
        {
            "Threshold": pl.Float64,
            "Fixed Magnitude": pl.Float64,
        },
    )
    s_d = strength_duration.from_blocks(blocks=blocks, dim="Amp")
    assert set(s_d.columns) == {
        "Fixed Pulse Width (μs)",
        "Threshold Amplitude (μA)",
    }


@pytest.fixture
def s_d_empty_df() -> pl.DataFrame:
    """Empty strength-duration dataframe."""
    return pl.DataFrame(
        {"Threshold": [], "Fixed Magnitude": [], "Dimension": []},
    ).cast({"Threshold": pl.Float64, "Fixed Magnitude": pl.Float64})


def test_strength_duration_amp(s_d_columns: set, s_d_empty_df: pl.DataFrame) -> None:
    """Tests Strength-duration data for amplitude-modulated data."""
    blocks = s_d_empty_df
    s_d = strength_duration.from_blocks(blocks=blocks, dim="Amp")
    assert set(s_d.columns) <= s_d_columns | {
        "Threshold Amplitude (μA)",
        "Fixed Pulse Width (μs)",
    }


def test_strength_duration_pw(s_d_columns: set, s_d_empty_df: pl.DataFrame) -> None:
    """Test strength-duration calcs for pulse-width-modulated data."""
    s_d = strength_duration.from_blocks(
        blocks=s_d_empty_df,
        dim="Width",
    )
    assert set(s_d.columns) <= s_d_columns | {
        "Fixed Amplitude (μA)",
        "Threshold Pulse Width (μs)",
    }


def test_plot():
    fig = strength_duration.plot(
        dim="Amp",
        blocks=pl.DataFrame(
            {
                "Dimension": [],
                "Fixed Amplitude (μA)": [],
                "Threshold Pulse Width (μs)": [],
                "Fixed Pulse Width (μs)": [],
                "Threshold Amplitude (μA)": [],
            },
        ).cast(
            {
                "Fixed Amplitude (μA)": pl.Float64,
                "Threshold Pulse Width (μs)": pl.Float64,
                "Fixed Pulse Width (μs)": pl.Float64,
                "Threshold Amplitude (μA)": pl.Float64,
            },
        ),
        x_data=[],
        y_data=[],
    )
    assert fig.layout.xaxis.title.text == "Fixed Pulse Width (μs)"
    assert fig.layout.yaxis.title.text == "Threshold Amplitude (μA)"


def test_plot_with_data():
    """Test strenght-duration plot with data."""
    x_data = [1.0]
    y_data = [1.0]
    fig = strength_duration.plot(
        dim="Width",
        blocks=pl.DataFrame(
            {
                "Dimension": [],
                "Fixed Amplitude (μA)": [],
                "Threshold Pulse Width (μs)": [],
            },
        ).cast(
            {
                "Fixed Amplitude (μA)": pl.Float64,
                "Threshold Pulse Width (μs)": pl.Float64,
            },
        ),
        x_data=x_data,
        y_data=y_data,
    )
    assert len(fig.data) == 1
