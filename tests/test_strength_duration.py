"""Tests for psychoanalyze.strength_duration module."""
import pandas as pd
import pytest

from psychoanalyze.analysis import strength_duration


@pytest.fixture()
def s_d_columns() -> set:
    """Columns needed for a strength-duration dataframe."""
    return {"Monkey", "Block", "Dimension"}


def test_strength_duration() -> None:
    """Test strength_duration construction."""
    df_index = pd.MultiIndex.from_frame(
        pd.DataFrame(
            {"Monkey": [], "Block": [], "Dimension": [], "Fixed Magnitude": []},
        ),
    )
    blocks = pd.DataFrame({"Threshold": [], "Fixed Magnitude": []}, index=df_index)
    s_d = strength_duration.from_blocks(blocks=blocks, dim="Amp")
    assert set(s_d.columns) == {
        "Fixed Pulse Width (μs)",
        "Threshold Amplitude (μA)",
    }


@pytest.fixture()
def s_d_empty_df() -> pd.DataFrame:
    """Empty strength-duration dataframe."""
    return pd.DataFrame({"Threshold": [], "Fixed Magnitude": [], "Dimension": []})


def test_strength_duration_amp(s_d_columns: set, s_d_empty_df: pd.DataFrame) -> None:
    """Tests Strength-duration data for amplitude-modulated data."""
    blocks = s_d_empty_df
    s_d = strength_duration.from_blocks(blocks=blocks, dim="Amp")
    assert set(s_d.columns) <= s_d_columns | {
        "Threshold Amplitude (μA)",
        "Fixed Pulse Width (μs)",
    }


def test_strength_duration_pw(s_d_columns: set, s_d_empty_df: pd.DataFrame) -> None:
    """Test strength-duration calcs for pulse-width-modulated data."""
    s_d = strength_duration.from_blocks(
        blocks=s_d_empty_df,
        dim="Width",
    )
    assert set(s_d.columns) <= s_d_columns | {
        "Fixed Amplitude (μA)",
        "Threshold Pulse Width (μs)",
    }
