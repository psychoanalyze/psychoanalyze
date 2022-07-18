import pytest
import pandas as pd
import psychoanalyze as pa
import json


@pytest.fixture
def subjects():
    return ["A", "B"]


@pytest.fixture
def X():
    return list(range(8))


def test_generate():
    data = pa.trials.generate(100)
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
    ).to_csv(tmp_path / "trials.csv", index_label=False)

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


def test_from_store():
    store_data = pd.DataFrame(
        {"Result": [1]},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {
                    "Monkey": ["U"],
                    "Date": ["1-1-2001"],
                    "Amp2": [0],
                    "Width2": [0],
                    "Freq2": [0],
                    "Dur2": [0],
                    "Active Channels": [0],
                    "Return Channels": [0],
                    "Amp1": [0],
                    "Width1": [0],
                    "Freq1": [0],
                    "Dur1": [0],
                }
            )
        ),
    )
    print(store_data)
    store_data = store_data.to_dict(orient="split")
    store_data["index_names"] = (
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
    )
    print(store_data)
    df = pa.trials.from_store(json.dumps(store_data))
    pa.trials.schema.validate(df)
