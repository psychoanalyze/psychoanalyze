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


def test_plot():
    fig = strength_duration.plot(
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


def test_plot_with_data():
    """Test strenght-duration plot with data."""
    x_data = [1.0]
    y_data = [1.0]
    fig = strength_duration.plot(
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
