import pandas as pd
import pytest

from psychoanalyze import plot, strength_duration


@pytest.fixture
def s_d_columns():
    return {"Monkey", "Block", "Dimension"}


def test_strength_duration(s_d_columns):
    df_index = pd.MultiIndex.from_frame(
        pd.DataFrame(
            {"Monkey": [], "Block": [], "Dimension": [], "Fixed Magnitude": []}
        )
    )
    blocks = pd.DataFrame({"Threshold": [], "Fixed Magnitude": []}, index=df_index)
    s_d = strength_duration.from_blocks(blocks=blocks, dim="Amp")
    assert set(s_d.columns) == {
        "Fixed Pulse Width (μs)",
        "Threshold Amplitude (μA)",
    }


@pytest.fixture
def s_d_empty_df():
    return pd.DataFrame({"Threshold": [], "Fixed Magnitude": [], "Dimension": []})


def test_strength_duration_amp(s_d_columns, s_d_empty_df):
    blocks = s_d_empty_df
    s_d = strength_duration.from_blocks(blocks=blocks, dim="Amp")
    assert set(s_d.columns) <= s_d_columns | {
        "Threshold Amplitude (μA)",
        "Fixed Pulse Width (μs)",
    }


def test_strength_duration_pw(s_d_columns, s_d_empty_df):
    s_d = strength_duration.from_blocks(
        blocks=s_d_empty_df,
        dim="Width",
    )
    assert set(s_d.columns) <= s_d_columns | {
        "Fixed Amplitude (μA)",
        "Threshold Pulse Width (μs)",
    }


def test_strength_duration_plot():
    fig = strength_duration.plot(plot_type="inverse", dim="Amp")
    assert fig.layout.xaxis.title.text == "Fixed Pulse Width (μs)"
    assert fig.layout.yaxis.title.text == "Threshold Amplitude (μA)"


def test_strength_duration_points_arg():
    points = pd.DataFrame(
        {"Threshold": []},
        pd.MultiIndex.from_frame(
            pd.DataFrame(
                {
                    "Monkey": [],
                    "Block": [],
                }
            )
        ),
    )
    fig = plot.strength_duration(points=points, dim="Amp", plot_type="inverse")
    assert len(fig.data) == 1
