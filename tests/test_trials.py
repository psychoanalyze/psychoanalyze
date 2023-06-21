import pytest
import pandas as pd
from psychoanalyze import trials, schemas
import json
from hypothesis import given


@pytest.fixture
def subjects():
    return ["A", "B"]


@pytest.fixture
def X():
    return list(range(8))


def test_from_store():
    store_data = pd.DataFrame(
        {"Result": [1]},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {"Monkey": ["U"], "Date": ["1-1-2001"]}
                | {
                    level: [0]
                    for level in schemas.block_dims + schemas.point_dims
                }
            )
        ),
    )
    store_data = store_data.to_dict(orient="split")
    store_data["index_names"] = schemas.points_index_levels
    df = trials.from_store(json.dumps(store_data))
    schemas.trials.validate(df)


def test_normalize():
    fields = {
        "Session": ["Monkey", "Block"],
        "Reference Stimulus": ["Amp2", "Width2", "Freq2", "Dur2"],
        "Channel Configuration": ["Active Channels", "Return Channels"],
        "Test Stimulus": ["Amp1", "Width1", "Freq1", "Dur1"],
    }
    data = {
        field: []
        for field in fields["Session"]
        + fields["Reference Stimulus"]
        + fields["Channel Configuration"]
        + fields["Test Stimulus"]
    }
    _trials = pd.DataFrame(data)
    normalized_data = trials.normalize(_trials)
    assert normalized_data.keys() == {
        "Session",
        "Reference Stimulus",
        "Channel Config",
        "Test Stimulus",
    }


def test_generate_block():
    block = trials.generate_block()
    assert set(block.columns) == {"Hits", "n"}
    assert block.index.name == "x"


@given(trials.schema.strategy())
def test_n(_trials: pd.Series):
    assert trials.n(_trials) == len(_trials)


def test_labels():
    assert trials.labels([0, 1]) == ["Miss", "Hit"]
