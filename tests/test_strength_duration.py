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
    s_d = pa.strength_duration(df=df)
    assert set(s_d.columns) == s_d_columns


def test_strength_duration_amp(s_d_columns):
    s_d = pa.strength_duration(dim="amp")
    assert set(s_d.columns) <= s_d_columns | {
        "Threshold Amplitude (μA)",
        "Fixed Pulse Width (μs)",
    }


def test_strength_duration_pw(s_d_columns):
    s_d = pa.strength_duration(dim="pw")
    assert set(s_d.columns) <= s_d_columns | {
        "Fixed Amplitude (μA)",
        "Threshold Pulse Width (μs)",
    }
