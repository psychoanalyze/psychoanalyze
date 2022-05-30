import pandas as pd
import psychoanalyze as pa
import pytest
import random


@pytest.fixture
def trials():
    return pa.trials.fake(100, set(range(8)))


def test_thresholds():
    data = pd.DataFrame({"Subject": ["A", "B"], "mu": [1, 2], "Day": [1, 2]})
    fig = pa.plot.thresholds(data)
    subjects = {trace["legendgroup"] for trace in fig.data}
    assert subjects == {"A", "B"}
    assert fig.layout.xaxis.title.text == "Day"
    assert fig.layout.yaxis.title.text == "mu"


def test_curves():
    n_subjects = 2
    subjects = list("ABCDEFG"[:n_subjects])
    subj_index = pd.MultiIndex.from_product([subjects, list(range(10))])
    index = pd.MultiIndex.from_product(
        [subjects, list(range(8)), list(range(10))], names=["Subject", "x", "Day"]
    )
    points = pd.DataFrame(
        {
            "Hit Rate": [random.random() for _ in index],
        },
        index=index,
    )
    fig = pa.plot.curves(points)
    assert fig.layout.xaxis.title.text == "x"
    assert fig.layout.yaxis.title.text == "Hit Rate"
    assert len(fig.data) == len(subj_index)


def test_standard_logistic():
    s = pa.data.logistic()
    df = s.to_frame()
    df["Type"] = "Generated"
    fig = pa.plot.logistic(df)
    assert fig.layout.xaxis.title.text == "x"
    assert fig.layout.yaxis.title.text == "Hit Rate"


def test_combine_logistics():
    s1 = pa.data.logistic(threshold=0)
    s2 = pa.data.logistic(threshold=1)
    df = pd.concat([s1, s2], keys=["0", "1"], names=["Type"])
    assert len(pa.plot.logistic(df.reset_index()).data) == 2


def test_bayes():
    simulated = pd.DataFrame(
        {
            "x": [-4, -2, 0, 2, 4],
            "Hit Rate": [0.01, 0.19, 0.55, 0.81, 0.99],
        }
    )
    index = pd.Index([-4, -2, 0, 2, 4], name="Hit Rate")
    estimated = pd.Series([0.011, 0.2, 0.56, 0.80, 0.98], index=index)
    fig = pa.plot.bayes(simulated, estimated)
    assert fig.layout.xaxis.title.text == "x"
    assert fig.layout.yaxis.title.text == "Hit Rate"
    assert len(fig.data) == 2
