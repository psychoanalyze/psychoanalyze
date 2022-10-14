import pandas as pd

import psychoanalyze as pa


def test_generate_sessions():
    assert pa.sessions.generate(3) == [0, 1, 2]


def test_from_trials_csv(tmp_path):
    csv_dir = tmp_path / "data"
    csv_dir.mkdir()
    csv_path = csv_dir / "trials.csv"
    data = {field: [] for field in ["Monkey", "Date"]}
    df = pd.DataFrame(data)
    df.to_csv(csv_path)

    sessions = pa.sessions.from_trials_csv(csv_path)
    assert set(sessions.columns) == {"Monkey", "Date"}
