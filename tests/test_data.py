import psychoanalyze as pa
import pytest


@pytest.fixture
def subjects():
    return ["A", "B"]


def test_generate_threshold_data(subjects):
    data = pa.data.generate(subjects, 10, "Threshold", n_trials_per_stim_level=10)
    data = pa.data.thresholds(data)
    assert len(data) == 20
    assert "Threshold" in data.columns


def test_generate_threshold_data_dashboard(subjects):
    data = pa.data.generate(subjects, 10, "Threshold", n_trials_per_stim_level=10)
    data = pa.data.thresholds(data)
    assert len(data) == 20
    assert "Threshold" in data.columns


def test_generate_curve(subjects):
    data = pa.data.generate(
        subjects=subjects, n_sessions=8, y="Hit Rate", n_trials_per_stim_level=10
    )
    assert data.index.get_level_values("Subject").nunique() == 2
    assert set(data.index.names) == {"Subject", "Day", "x"}
    assert "Hit Rate" in set(data.columns)


@pytest.mark.parametrize("n", [2, 3])
def test_generate_n_subjects(n):
    subjects = pa.data.subjects(n_subjects=n)
    data = pa.data.generate(
        y="Threshold", n_sessions=10, subjects=subjects, n_trials_per_stim_level=10
    )
    assert {"Subject", "Day"} <= set(data.index.names)
    assert data.index.get_level_values("Subject").nunique() == n
    assert "Threshold" in set(data.columns)


def test_generate_10_trials(subjects):
    n_sessions = 10
    data = pa.data.generate(
        subjects=subjects,
        n_sessions=n_sessions,
        y="Threshold",
        n_trials_per_stim_level=10,
    )
    assert "Threshold" in set(data.columns)
    assert len(data) == n_sessions * len(subjects) * 8


def test_generate_11_trials(subjects):
    n_sessions = 10
    data = pa.data.generate(
        subjects=subjects,
        n_sessions=n_sessions,
        y="Threshold",
        n_trials_per_stim_level=11,
    )
    assert "Threshold" in set(data.columns)
    assert len(data) == n_sessions * len(subjects) * 8
    assert all(data["n"] == 11)


def test_standard_logistic():
    s = pa.data.logistic()
    assert min(s.index) == -6
    assert max(s.index) == 6
    assert min(s) > 0
    assert max(s) < 1