import psychoanalyze as pa
import pytest


def test_generate_curve():
    data = pa.data.generate(subjects=["A", "B"], n=8, x="x", y="Hit Rate")
    assert data.index.get_level_values("Subject").nunique() == 2
    assert set(data.index.names) == {"Subject", "x"}
    assert set(data.columns) == {"Hit Rate"}


@pytest.mark.parametrize("n", [2, 3])
def test_generate_n_subjects(n):
    subjects = pa.data.subjects(n_subjects=n)
    data = pa.data.generate(y="Threshold", x="Day", n=10, subjects=subjects)
    assert set(data.index.names) == {"Subject", "Day"}
    assert data.index.get_level_values("Subject").nunique() == n
    assert set(data.columns) == {"Threshold"}


def test_generate_n_trials():
    data = pa.data.generate(subjects=["A", "B"], n=10, x="Day", y="Threshold")
    assert set(data.columns) == {"Threshold"}
