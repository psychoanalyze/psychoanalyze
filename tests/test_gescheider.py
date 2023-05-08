import psychoanalyze as pa
import pandas as pd


def test_3_1():
    data = pd.Series(
        [0.04, 0.05, 0.20, 0.34, 0.53, 0.72, 0.94, 0.96, 0.99],
        index=pd.Index([2, 4, 6, 8, 10, 12, 14, 16, 18], name="Stimulus Intensity"),
        name="p(yes)",
    )
    layout = pa.gescheider.p3_1(data).layout
    assert layout.xaxis.title.text == "Stimulus Intensity"
    assert layout.yaxis.title.text == "p(yes)"
