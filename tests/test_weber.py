import psychoanalyze as pa
import pandas as pd
from datetime import datetime


def test_plot():
    y = "Reference Charge (nC)"
    x = "Difference Threshold (nC)"
    subjects = ["U", "Y"]
    line = {x: [0, 1], y: [0, 1]}
    data = {subject: {"Amp": line, "Width": line} for subject in subjects}
    data = pd.concat({k: pd.DataFrame(v).T for k, v in data.items()})
    data.index.names = ["Monkey", "Dimension"]
    data["err_y"] = 1
    data["Date"] = datetime.now()

    fig = pa.weber.plot(data)

    assert len(fig.data) == 8
    assert fig.layout.xaxis.title.text == y
    assert fig.layout.yaxis.title.text == x
    assert all(trace["error_y"] for trace in fig.data)


def test_aggregate():
    curve_data = pd.DataFrame.from_records(
        [
            {"Reference Charge (nC)": 0, "Difference Threshold (nC)": 0},
            {"Reference Charge (nC)": 0, "Difference Threshold (nC)": 2},
        ],
        index=pd.MultiIndex.from_frame(
            pd.DataFrame({"Monkey": ["U", "U"], "Dimension": ["Amp", "Amp"]})
        ),
    )
    df = pa.weber.aggregate(curve_data)
    assert df.at[df.index[0], "Difference Threshold (nC)"] == 1.0


def test_tmp():
    pass
