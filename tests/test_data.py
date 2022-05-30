import psychoanalyze as pa
import pytest


@pytest.fixture
def subjects():
    return ["A", "B"]


X = list(range(8))


def test_generate_threshold_data(subjects):
    data = pa.data.generate(subjects, 10, "Threshold", n_trials_per_stim_level=10, X=X)
    data = pa.data.thresholds(data)
    assert len(data) == 20
    assert "Threshold" in data.columns


def test_generate_threshold_data_dashboard(subjects):
    data = pa.data.generate(subjects, 10, "Threshold", n_trials_per_stim_level=10, X=X)
    data = pa.data.thresholds(data)
    assert len(data) == 20
    assert "Threshold" in data.columns


def test_generate_curve(subjects):
    data = pa.data.generate(
        subjects=subjects, n_sessions=8, y="Hit Rate", n_trials_per_stim_level=10, X=X
    )
    assert data.index.get_level_values("Subject").nunique() == 2
    assert set(data.index.names) == {"Subject", "Day", "x"}
    assert "Hit Rate" in set(data.columns)


@pytest.mark.parametrize("n", [2, 3])
def test_generate_n_subjects(n):
    subjects = pa.data.subjects(n_subjects=n)
    data = pa.data.generate(
        y="Threshold", n_sessions=10, subjects=subjects, n_trials_per_stim_level=10, X=X
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
        X=X,
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
        X=X,
    )
    assert "Threshold" in set(data.columns)
    assert len(data) == n_sessions * len(subjects) * 8
    assert all(data["n"] == 11)


def test_standard_logistic():
    s = pa.data.logistic()
    assert min(s) > 0
    assert max(s) < 1


def test_nonstandard_logistic_mean():
    s = pa.data.logistic(threshold=1)
    assert min(s) > 0
    assert max(s) < 1


def test_nonstandard_logistic_slope():
    s_control = pa.data.logistic()
    s = pa.data.logistic(scale=2)
    assert max(s) < max(s_control)


# @patch("cmdstanpy.CmdStanModel.sample.summary")
def test_fit_curve():
    df = pa.data.generate(["A"], 1, "Hit Rate", 100, list(range(-4, 5))).reset_index()
    estimates = pa.data.fit_curve(df)
    # assert model.assert_called()
    assert len(estimates) == 9
