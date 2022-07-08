import psychoanalyze as pa
import pandas as pd
import datatest as dt


def test_weber_plot():
    y = "Reference Charge (nC)"
    x = "Difference Threshold (nC)"
    line = {x: [0, 1], y: [0, 1]}
    data = {
        "U": {"Amp": line, "Width": line},
        "Y": {"Amp": line, "Width": line},
    }
    data = pd.concat({k: pd.DataFrame(v).T for k, v in data.items()})
    data.index.names = ["Monkey", "Dimension"]
    data["err_y"] = 1

    fig = pa.weber.plot(data)

    assert len(fig.data) == 4
    assert fig.layout.xaxis.title.text == y
    assert fig.layout.yaxis.title.text == x
    assert all(trace["error_y"] for trace in fig.data)


def test_weber_aggregate():
    curve_data = pd.DataFrame(
        {
            "Reference Charge (nC)": [0, 0],
            "Difference Threshold (nC)": [0, 2],
        }
    )
    dt.validate(
        pa.weber.aggregate(curve_data),
        pd.DataFrame({"Reference Charge (nC)": [0], "Difference Threshold (nC)": [1]}),
    )
