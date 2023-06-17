import pytest
import pandas as pd
import psychoanalyze as pa
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
                    for level in pa.schemas.block_dims + pa.schemas.point_dims
                }
            )
        ),
    )
    store_data = store_data.to_dict(orient="split")
    store_data["index_names"] = pa.schemas.points_index_levels
    df = pa.trials.from_store(json.dumps(store_data))
    pa.schemas.trials.validate(df)


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
    trials = pd.DataFrame(data)
    normalized_data = pa.trials.normalize(trials)
    assert normalized_data.keys() == {
        "Session",
        "Reference Stimulus",
        "Channel Config",
        "Test Stimulus",
    }


def test_generate_block():
    block = pa.trials.generate_block()
    assert set(block.columns) == {"Hits", "n"}
    assert block.index.name == "x"


@given(pa.trials.schema.strategy())
def test_n(trials: pd.Series):
    assert pa.trials.n(trials) == len(trials)


def test_labels():
    assert pa.trials.labels([0, 1]) == ["Miss", "Hit"]
