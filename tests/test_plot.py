import pandas as pd
import psychoanalyze as pa
import pytest


@pytest.fixture
def trials():
    return pa.trials.fake(100, set(range(8)))


def test_thresholds():
    data = pd.DataFrame(
        {"Threshold": [1, 2], "Day": [1, 2]}, index=pd.Index(["A", "B"], name="Subject")
    )
    fig = pa.plot.thresholds(data)
    subjects = {trace["legendgroup"] for trace in fig.data}
    assert subjects == {"A", "B"}
    assert fig.layout.xaxis.title.text == "Day"
    assert fig.layout.yaxis.title.text == "Threshold"


def test_curves():
    points = pd.DataFrame({"x": [], "Hit Rate": []})
    fig = pa.plot.curves(points)
    assert fig.layout.xaxis.title.text == "x"


def test_fit():
    fit = pd.DataFrame({"Hit Rate": []})
    assert pa.plot.curve(fit)


def test_curve_points(trials):
    trials = trials
    curve = pa.curve(trials)
    fig = pa.plot.curve(curve)
    assert fig.layout.yaxis.title.text == "Hit Rate"
