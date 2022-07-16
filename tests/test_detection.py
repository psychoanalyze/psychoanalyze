import psychoanalyze as pa
import pandas as pd


def test_load():
    df = pd.DataFrame(
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {
                    "Amp2": [0, 1, 0, 1],
                    "Width2": [0, 0, 1, 1],
                    "Amp1": [0, 0, 0, 0],
                    "Width1": [0, 0, 0, 0],
                }
            )
        ),
    )
    df = pa.detection.load(df)
    assert all(df[df["Reference Charge (nC)"] == 0])
