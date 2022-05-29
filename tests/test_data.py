import psychoanalyze as pa
import pytest
import datatest as dt


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
        subjects=subjects, n=8, y="Hit Rate", n_trials_per_stim_level=10
    )
    assert data.index.get_level_values("Subject").nunique() == 2
    assert set(data.index.names) == {"Subject", "Day", "x"}
    assert "Hit Rate" in set(data.columns)


@pytest.mark.parametrize("n", [2, 3])
def test_generate_n_subjects(n):
    subjects = pa.data.subjects(n_subjects=n)
    data = pa.data.generate(
        y="Threshold", n=10, subjects=subjects, n_trials_per_stim_level=10
    )
    assert {"Subject", "Day"} <= set(data.index.names)
    assert data.index.get_level_values("Subject").nunique() == n
    assert "Threshold" in set(data.columns)


def test_generate_n_trials(subjects):
    n = 10
    data = pa.data.generate(
        subjects=subjects, n=n, y="Threshold", n_trials_per_stim_level=10
    )
    assert "Threshold" in set(data.columns)
    assert len(data) == n * len(subjects) * 8
