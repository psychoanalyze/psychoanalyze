import psychoanalyze as pa
import pytest
import datatest as dt


@pytest.fixture
def subjects():
    return ["A", "B"]


@pytest.fixture
def trials():
    return pa.data.trials(100, set(range(8)))


def test_faker(trials):
    assert all(trials["Result"].isin({0, 1}))


def test_faker_size(trials):
    assert len(trials) == 100


def test_faker_x_values(trials):
    dt.validate(trials["x"], set(range(8)))


def test_generate_threshold_data(subjects):
    data = pa.data.generate(subjects, 10, "Threshold")
    data = pa.data.thresholds(data)
    assert len(data) == 20
    assert "Threshold" in data.columns


def test_generate_threshold_data_dashboard(subjects):
    data = pa.data.generate(subjects, 10, "Threshold")
    data = pa.data.thresholds(data)
    assert len(data) == 20
    assert "Threshold" in data.columns


def test_generate_curve(subjects):
    data = pa.data.generate(subjects=subjects, n=8, y="Hit Rate")
    assert data.index.get_level_values("Subject").nunique() == 2
    assert set(data.index.names) == {"Subject", "Day", "x"}
    assert "Hit Rate" in set(data.columns)


@pytest.mark.parametrize("n", [2, 3])
def test_generate_n_subjects(n):
    subjects = pa.data.subjects(n_subjects=n)
    data = pa.data.generate(y="Threshold", n=10, subjects=subjects)
    assert {"Subject", "Day"} <= set(data.index.names)
    assert data.index.get_level_values("Subject").nunique() == n
    assert "Threshold" in set(data.columns)


def test_generate_n_trials(subjects):
    n = 10
    data = pa.data.generate(subjects=subjects, n=n, y="Threshold")
    assert "Threshold" in set(data.columns)
    assert len(data) == n * len(subjects) * 8
