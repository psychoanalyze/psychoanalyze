import pytest
import pandas as pd
import psychoanalyze as pa


@pytest.fixture
def subjects():
    return ["A", "B"]


@pytest.fixture
def X():
    return list(range(8))


def test_generate():
    data = pa.trial.generate(100)
    assert len(data) == 100


def test_load(tmp_path):
    pd.DataFrame(
        {
            "Monkey": [],
            "Date": [],
            "Amp2": [],
            "Width2": [],
            "Freq2": [],
            "Dur2": [],
            "Active Channels": [],
            "Return Channels": [],
            "Amp1": [],
            "Width1": [],
            "Freq1": [],
            "Dur1": [],
            "Result": [],
        }
    ).to_csv(tmp_path / "trials.csv")

    trials = pa.trials.load(tmp_path / "trials.csv")
    assert list(trials.index.names) == [
        "Monkey",
        "Date",
        "Amp2",
        "Width2",
        "Freq2",
        "Dur2",
        "Active Channels",
        "Return Channels",
        "Amp1",
        "Width1",
        "Freq1",
        "Dur1",
    ]
    assert list(trials.columns) == ["Result"]
