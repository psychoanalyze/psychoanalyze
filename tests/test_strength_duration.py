import pandas as pd
import pytest

import psychoanalyze as pa


@pytest.fixture
def s_d_columns():
    return {"Monkey", "Day", "Dimension"}


def test_strength_duration(s_d_columns):
    df_index = pd.MultiIndex.from_frame(
        pd.DataFrame({"Monkey": [], "Day": [], "Dimension": [], "Fixed Magnitude": []})
    )
    df = pd.DataFrame({"Threshold": []}, index=df_index)
    s_d = pa.strength_duration.data(df=df)
    assert set(s_d.columns) == {"Threshold"}


def test_strength_duration_amp(s_d_columns):
    df = pd.DataFrame({"Threshold": [], "Fixed Magnitude": [], "Dimension": []})
    s_d = pa.strength_duration.data(df=df, dim="amp")
    assert set(s_d.columns) <= s_d_columns | {
        "Threshold Amplitude (μA)",
        "Fixed Pulse Width (μs)",
    }


def test_strength_duration_pw(s_d_columns):
    df = pd.DataFrame({"Threshold": [], "Fixed Magnitude": [], "Dimension": []})
    s_d = pa.strength_duration.data(
        df=df,
        dim="pw",
    )
    assert set(s_d.columns) <= s_d_columns | {
        "Fixed Amplitude (μA)",
        "Threshold Pulse Width (μs)",
    }


def test_strength_duration_plot():
    fig = pa.strength_duration.plot(plot_type="inverse", dim="Amp")
    assert fig.layout.xaxis.title.text == "Fixed Pulse Width (μs)"
    assert fig.layout.yaxis.title.text == "Threshold Amplitude (μA)"
