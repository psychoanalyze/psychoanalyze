import pandas as pd
import pytest
import datetime
import pandas.api.types as ptypes

import psychoanalyze as pa


@pytest.fixture
def subjects():
    return pd.DataFrame({"Monkey": ["U"], "Surgery Date": ["2020-01-01"]})


def test_generate_sessions():
    assert pa.sessions.generate(3) == [0, 1, 2]


def test_from_trials_csv(tmp_path):
    csv_dir = tmp_path / "data"
    csv_dir.mkdir()
    csv_path = csv_dir / "trials.csv"
    data = {field: [] for field in ["Monkey", "Date"]}
    df = pd.DataFrame(data)
    df.to_csv(csv_path)

    sessions = pa.sessions.from_trials_csv(csv_path, cache=False)
    assert set(sessions.columns) == {"Monkey", "Date"}


def test_day_marks_from_monkey_two_sessions(subjects):
    sessions = pd.DataFrame(
        {"Monkey": ["U", "U"], "Date": ["2020-01-02", "2020-01-03"]}
    )
    assert pa.sessions.day_marks(subjects, sessions, "U") == {
        1: "2020-01-02",
        2: "2020-01-03",
    }


def test_day_marks_from_monkey_one_session(subjects):
    sessions = pd.DataFrame({"Monkey": ["U"], "Date": ["2020-01-02"]})

    assert pa.sessions.day_marks(subjects, sessions, "U") == {1: "2020-01-02"}


def test_n_trials():
    sessions = pd.DataFrame(
        {"Day": [1], "Date": [datetime.date(2000, 1, 1)]}
    ).set_index("Date")
    trials = pd.DataFrame(
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
    )
    n_trials = pa.sessions.n_trials(sessions, trials)
    pd.testing.assert_frame_equal(
        n_trials,
        pd.DataFrame(
            {"Result": 3},
            index=pd.MultiIndex.from_frame(pd.DataFrame({"Monkey": ["U"], "Day": [1]})),
        ),
    )


def test_load():
    sessions = pa.sessions.load()
    assert ptypes.is_datetime64_any_dtype(sessions.index.get_level_values("Date"))


def test_load_monkey(tmp_path):
    path = tmp_path / "trials.csv"
    pd.DataFrame(
        {
            "Monkey": ["U", "Y"],
            "Date": ["2020-01-01", "2020-01-01"],
            "Day": [1, 1],
            "Result": [1, 1],
        }
    ).to_csv(path)
    sessions = pa.sessions.load(path=path, monkey="U")
    assert all(sessions.index.get_level_values("Monkey") == "U")
