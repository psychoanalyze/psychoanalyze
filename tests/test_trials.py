"""Tests for psychoanalyze.points module."""

import json
from typing import Any

import pandas as pd
import pytest

from psychoanalyze import schemas, trials


@pytest.fixture()
def subjects() -> list[str]:
    """Subjects."""
    return ["A", "B"]


@pytest.fixture()
def x() -> list[int]:
    """Intensity values."""
    return list(range(8))


def test_from_store() -> None:
    """Given JSON-formatted data from a Dash store, returns a DataFrame."""
    store_data = pd.DataFrame(
        {"Result": [1]},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {"Monkey": ["U"], "Date": ["1-1-2001"]}
                | {level: [0] for level in schemas.block_dims + schemas.point_dims},
            ),
        ),
    )
    _store_data = store_data.to_dict(orient="split")
    _store_data["index_names"] = schemas.points_index_levels
    _trials = trials.from_store(json.dumps(store_data))
    schemas.trials.validate(_trials)


def test_normalize() -> None:
    """Given a denormalized dataframe, returns normalized data."""
    fields = {
        "Session": ["Monkey", "Block"],
        "Reference Stimulus": ["Amp2", "Width2", "Freq2", "Dur2"],
        "Channel Configuration": ["Active Channels", "Return Channels"],
        "Test Stimulus": ["Amp1", "Width1", "Freq1", "Dur1"],
    }
    data: dict[str, list[Any]] = {
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


def test_generate_block() -> None:
    """Test that generating block data results in the right schema."""
    block = trials.generate_block()
    assert set(block.columns) == {"Hits", "n"}
    assert block.index.name == "x"


def test_labels() -> None:
    """Given trial result integers, translates to labels."""
    assert trials.labels([0, 1]) == ["Miss", "Hit"]
