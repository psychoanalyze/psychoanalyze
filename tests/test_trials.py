import pytest
import psychoanalyze as pa


@pytest.fixture
def subjects():
    return ["A", "B"]


@pytest.fixture
def X():
    return list(range(8))


def test_generate():
    assert len(pa.trial.generate(100)) == 100


@pytest.mark.parametrize("n_trials", [10, 11])
def test_generate_n_trials(n_trials, subjects, X):
    n_sessions = 10
    data = pa.data.generate(
        subjects=subjects,
        n_sessions=n_sessions,
        y="Threshold",
        n_trials_per_stim_level=n_trials,
        X=X,
    )
    assert "Threshold" in set(data.columns)
    assert len(data) == n_sessions * len(subjects) * 8
    assert all(data["n"] == n_trials)
