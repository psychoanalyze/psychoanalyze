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
        {level_name: [] for level_name in pa.points.index_levels} | {"Result": []},
    ).to_csv(tmp_path / "trials.csv", index_label=False)

    trials = pa.trials.load(tmp_path / "trials.csv")
    assert list(trials.index.names) == pa.points.index_levels
    assert list(trials.columns) == ["Result"]


def test_from_store():
    store_data = pd.DataFrame(
        {"Result": [1]},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {"Monkey": ["U"], "Date": ["1-1-2001"]}
                | {level: [0] for level in pa.blocks.dims + pa.points.dims}
            )
        ),
    )
    store_data = store_data.to_dict(orient="split")
    store_data["index_names"] = pa.points.index_levels
    df = pa.trials.from_store(json.dumps(store_data))
    pa.trials.schema.validate(df)


def test_to_store():
    data_json = pa.trials.to_store(pa.trials.schema.example(1))
    assert "index_names" in json.loads(data_json).keys()
