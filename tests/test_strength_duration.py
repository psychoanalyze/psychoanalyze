import pandas as pd
import pytest

import psychoanalyze as pa


@pytest.fixture
def s_d_columns():
    return {"Monkey", "Day"}


def test_strength_duration(s_d_columns):
    df_index = pd.MultiIndex.from_frame(
        pd.DataFrame(
            {"Monkey": [], "Day": [], "Dimension": [], "Reference Magnitude": []}
        )
    )
    df = pd.DataFrame({"Threshold": []}, index=df_index)
    s_d = pa.strength_duration.data(df=df)
    assert set(s_d.columns) == s_d_columns


def test_strength_duration_amp(s_d_columns):
    s_d = pa.strength_duration.data(dim="amp")
    assert set(s_d.columns) <= s_d_columns | {
        "Threshold Amplitude (μA)",
        "Fixed Pulse Width (μs)",
    }


def test_strength_duration_pw(s_d_columns):
    s_d = pa.strength_duration.data(dim="pw")
    assert set(s_d.columns) <= s_d_columns | {
        "Fixed Amplitude (μA)",
        "Threshold Pulse Width (μs)",
    }


def test_get_x_label():
    # if dim == "Width":
    #     return "Fixed Amplitude (μA)"
    # if dim == "Amp":
    #     return "Fixed Pulse Width (μs)"
    # assert pa.strength_duration.xlabel("Width") == "Fixed Amplitude (μA)"
    # assert pa.strength_duration.xlabel("Amp") == "Fixed Pulse Width (μs)"
    pass
