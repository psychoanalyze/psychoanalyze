import pytest

import psychoanalyze as pa


@pytest.fixture
def s_d_columns():
    return {"Monkey", "Day"}


def test_strengh_duration(s_d_columns):
    s_d = pa.strength_duration()
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
