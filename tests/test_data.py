import psychoanalyze as pa
import pytest
import pandas as pd
import datatest as dt  # type: ignore


@pytest.fixture
def subjects():
    return ["A", "B"]


@pytest.fixture
def X():
    return list(range(8))


def test_nonstandard_logistic_mean():
    s = pa.data.logistic(threshold=1)
    assert min(s) > 0
    assert max(s) < 1


def test_nonstandard_logistic_slope():
    s_control = pa.data.logistic()
    s = pa.data.logistic(scale=2)
    assert max(s) < max(s_control)


def test_params():
    x = pd.Index([])
    fit = pd.DataFrame({"5%": [], "50%": [], "95%": []})
    df = pa.data.reshape_fit_results(fit=fit, x=x, y="p")
    dt.validate(df.index, x)
    assert set(df.columns) <= {"err+", "err-", "p"}


def test_construct_index(mocker):
    mocker.patch(
        "psychoanalyze.data.reshape_fit_results", return_value=pd.DataFrame({"x": []})
    )
    days = [1, 2, 3]
    x = [1, 2, 3]
    index = pa.data.construct_index(subjects=None, days=days, x=x)
    assert index.names == ["Day", "x"]
    assert len(index) == len(x) * len(days)


def test_data_load(tmp_path):
    pd.DataFrame(
        {"Trial ID": [1, 2, 3], "Result": [1] * 3},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {
                    "Monkey": ["U"] * 3,
                    "Date": pd.to_datetime(["2000-01-01"] * 3),
                    "Amp2": [0] * 3,
                    "Width2": [0] * 3,
                    "Freq2": [0] * 3,
                    "Dur2": [0] * 3,
                    "Active Channels": [0] * 3,
                    "Return Channels": [0] * 3,
                    "Amp1": [2] * 3,
                    "Width1": [0] * 3,
                    "Freq1": [0] * 3,
                    "Dur1": [0] * 3,
                }
            )
        ),
    ).to_csv(tmp_path / "trials.csv")
    pd.DataFrame(
        {"Surgery Date": pd.to_datetime(["1999-12-31"])},
        index=pd.Index(["U"], name="Monkey"),
    ).to_csv(tmp_path / "subjects.csv")
    data = pa.data.load(tmp_path)
    assert data.keys() == {"Subjects", "Sessions", "Blocks", "Points"}
