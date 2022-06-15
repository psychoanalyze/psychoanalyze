import pytest
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
