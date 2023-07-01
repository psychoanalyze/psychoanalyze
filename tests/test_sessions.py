import datetime

import pandas as pd
import pandas.api.types as ptypes
import pytest

from psychoanalyze import sessions


@pytest.fixture
def subjects():
    return pd.DataFrame({"Monkey": ["U"], "Surgery Date": ["2020-01-01"]})


def test_generate_sessions():
    assert sessions.generate(3) == [0, 1, 2]


def test_from_trials_csv(tmp_path):
    csv_dir = tmp_path / "data"
    csv_dir.mkdir()
    csv_path = csv_dir / "trials.csv"
    data = {field: [] for field in ["Monkey", "Date"]}
    df = pd.DataFrame(data)
    df.to_csv(csv_path)

    _sessions = sessions.from_trials_csv(csv_path, cache=False)
    assert set(_sessions.columns) == {"Monkey", "Date"}


def test_day_marks_from_monkey_two_sessions(subjects):
    _sessions = pd.DataFrame(
        {"Monkey": ["U", "U"], "Date": ["2020-01-02", "2020-01-03"]}
    )
    assert sessions.day_marks(subjects, _sessions, "U") == {
        1: "2020-01-02",
        2: "2020-01-03",
    }


def test_day_marks_from_monkey_one_session(subjects):
    _sessions = pd.DataFrame({"Monkey": ["U"], "Date": ["2020-01-02"]})

    assert sessions.day_marks(subjects, _sessions, "U") == {1: "2020-01-02"}


def test_load_n_trials(tmp_path):
    path = tmp_path / "trials.csv"
    pd.DataFrame(
        {"Trial ID": [1, 2, 3], "Result": [1] * 3},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {
                    "Monkey": ["U"] * 3,
                    "Date": [datetime.date(2000, 1, 1)] * 3,
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
    ).to_csv(path)
    pd.DataFrame(
        {"Surgery Date": pd.to_datetime(["1999-12-31"])},
        index=pd.Index(["U"], name="Monkey"),
    ).to_csv(tmp_path / "subjects.csv")
    _sessions = sessions.load(data_path=tmp_path)
    pd.testing.assert_frame_equal(
        _sessions,
        pd.DataFrame(
            {"n Trials": [3], "Block": [1]},
            index=pd.MultiIndex.from_frame(
                pd.DataFrame(
                    {
                        "Monkey": ["U"],
                        "Date": pd.to_datetime([datetime.date(2000, 1, 1)]),
                    }
                )
            ),
        ),
    )


def test_load(tmp_path):
    session_index = ["Monkey", "Date"]
    reference_stim = ["Amp2", "Width2", "Freq2", "Dur2"]
    channel_config = ["Active Channels", "Return Channels"]
    test_stim = ["Amp1", "Width1", "Freq1", "Dur1"]
    index = session_index + reference_stim + channel_config + test_stim + ["Result"]
    pd.DataFrame({field: [] for field in index}).to_csv(tmp_path / "trials.csv")
    pd.DataFrame(
        {"Surgery Date": ["2019-12-31"]}, index=pd.Index(["U"], name="Monkey")
    ).to_csv(tmp_path / "subjects.csv")
    _sessions = sessions.load(tmp_path)
    assert ptypes.is_datetime64_any_dtype(_sessions.index.get_level_values("Date"))


def test_load_monkey(tmp_path):
    path = tmp_path / "trials.csv"
    subj_path = tmp_path / "subjects.csv"
    pd.DataFrame(
        {
            "Monkey": ["U", "Y"],
            "Date": ["2020-01-01", "2020-01-01"],
            "Amp2": [0] * 2,
            "Width2": [0] * 2,
            "Freq2": [0] * 2,
            "Dur2": [0] * 2,
            "Active Channels": [0] * 2,
            "Return Channels": [0] * 2,
            "Block": [1] * 2,
            "Result": [1] * 2,
            "Amp1": [0] * 2,
            "Width1": [0] * 2,
            "Freq1": [0] * 2,
            "Dur1": [0] * 2,
        }
    ).to_csv(path)
    pd.DataFrame(
        {"Surgery Date": pd.to_datetime(["2019-12-31"])},
        index=pd.Index(["U"], name="Monkey"),
    ).to_csv(subj_path)
    _sessions = sessions.load(data_path=tmp_path, monkey="U")
    assert all(_sessions.index.get_level_values("Monkey") == "U")
