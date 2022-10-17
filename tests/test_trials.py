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
    stim_levels = tuple(range(-3, 4))
    trials = pa.trials.generate(100, stim_levels)
    assert len(trials) == 100
    assert set(trials.columns) == {"Result"}


def test_load(tmp_path):
    pd.DataFrame(
        {level_name: [] for level_name in pa.schemas.points_index_levels}
        | {"Result": []},
    ).to_csv(tmp_path / "trials.csv", index_label=False)

    trials = pa.trials.load(tmp_path / "trials.csv")
    assert list(trials.index.names) == pa.schemas.points_index_levels
    assert list(trials.columns) == ["Result"]


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


def test_to_store():
    data_json = pa.trials.to_store(pa.schemas.trials.example(1))
    assert "index_names" in json.loads(data_json).keys()


def test_normalize():
    fields = {
        "Session": ["Monkey", "Day"],
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
