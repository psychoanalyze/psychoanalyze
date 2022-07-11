import psychoanalyze as pa
import pandas as pd


def test_load():
    df = pd.DataFrame({"Amp2": [0, 1, 0, 1], "Width2": [0, 0, 1, 1]})
    assert all(pa.detection.load(df)["Reference Charge (nC)"] == 0)
