import psychoanalyze as pa
import pandas as pd


def test_amp_load():
    df = pd.DataFrame({"Dimension": ["Amp", "Width"]})
    df = pa.amp.load(df)
    assert all(df["Dimension"] == "Amp")
