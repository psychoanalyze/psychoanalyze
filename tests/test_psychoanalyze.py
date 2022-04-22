from psychoanalyze import __version__
import psychoanalyze as pa
import pandas as pd
import datatest as dt
import pytest


@pytest.fixture
def fake_df():
    return pd.DataFrame(
        {"Result": [0, 1], "x": [1, 1]}, index=pd.Index([1, 2], name="Trial")
    )


def test_version():
    assert __version__ == "0.1.0"


def test_faker(fake_df):
    assert pa.fake().equals(fake_df)


def test_curve(fake_df):
    df = pd.DataFrame(fake_df)
    dt.validate(pa.curve(df), pd.Series([0.5], index=pd.Index([1], name="x")))
