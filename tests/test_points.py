import psychoanalyze as pa
import pandas as pd
from scipy.special import expit
import json


def test_from_trials():
    df = pd.DataFrame(
        {"Result": [0, 1]},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {
                    "Monkey": ["U", "U"],
                    "Date": [1, 1],
                    "Amp2": [1, 1],
                    "Width2": [1, 1],
                    "Freq2": [1, 1],
                    "Dur2": [1, 1],
                    "Active Channels": [1, 1],
                    "Return Channels": [1, 1],
                    "Amp1": [1, 2],
                    "Width1": [1, 1],
                    "Freq1": [1, 1],
                    "Dur1": [1, 1],
                }
            )
        ),
    )
    df = pa.points.from_trials(df)
    assert len(df) == 2
    assert list(df["n"].values) == [1, 1]


def test_amp_dimension():
    df = pd.DataFrame(
        index=pd.MultiIndex.from_frame(pd.DataFrame({"Amp1": [1, 2], "Width1": [1, 1]}))
    )
    assert pa.points.dimension(df) == "Amp"


def test_width_dimension():
    df = pd.DataFrame(
        index=pd.MultiIndex.from_frame(pd.DataFrame({"Amp1": [1, 1], "Width1": [1, 2]}))
    )
    assert pa.points.dimension(df) == "Width"


def test_both_dimensions():
    df = pd.DataFrame(
        index=pd.MultiIndex.from_frame(pd.DataFrame({"Amp1": [1, 2], "Width1": [1, 2]}))
    )
    assert pa.points.dimension(df) == "Both"


def test_fit(mocker):
    mocker.patch("cmdstanpy.CmdStanModel")
    df = pd.DataFrame({"Amp1": [], "n": [], "Hits": []})
    pa.points.fit(df)


def test_plot():
    s = pd.DataFrame(
        {"Hits": [], "n": [], "Hit Rate": []},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {
                    "Monkey": [],
                    "Date": [],
                    "Amp2": [],
                    "Width2": [],
                    "Freq2": [],
                    "Active Channels": [],
                    "Return Channels": [],
                    "Amp1": [],
                    "Width1": [],
                    "Freq1": [],
                    "Dur1": [],
                }
            )
        ),
        dtype=float,
    )
    fig = pa.points.plot(s)
    assert fig.layout.yaxis.title.text == "Hit Rate"
    assert fig.layout.xaxis.title.text == "Amplitude (µA)"


def test_generate():
    x = list(range(-3, 4))
    n = [10] * 8
    p = expit(x)
    points = pa.points.generate(x, n, p)
    assert all(points.index.values == x)
    assert points.name == "Hit Rate"


def test_load(tmp_path):
    points = pa.points.load()
    assert "n" in points.columns


def test_datatable():
    data = pd.DataFrame(
        index=pd.MultiIndex.from_frame(
            pd.DataFrame({"Amp1": [0.1212345], "Hit Rate": [0.1234543], "n": [1]})
        )
    )
    datatable = pa.points.datatable(data)
    amp_column = [column for column in datatable.columns if column["name"] == "Amp1"]
    assert amp_column[0]["format"].to_plotly_json()["specifier"] == ".2f"


def test_from_store(mocker):
    mocker.patch(
        "psychoanalyze.trials.from_store",
        return_value=pd.DataFrame(
            {"Result": [1]},
            index=pd.MultiIndex.from_frame(
                pd.DataFrame(
                    {
                        "Monkey": ["U"],
                        "Date": ["1-1-2001"],
                        "Amp2": [0],
                        "Width2": [0],
                        "Freq2": [0],
                        "Dur2": [0],
                        "Active Channels": [0],
                        "Return Channels": [0],
                        "Amp1": [0],
                        "Width1": [0],
                        "Freq1": [0],
                        "Dur1": [0],
                    }
                )
            ),
        ),
    )
    store_data = pd.DataFrame(
        {"Result": [1]},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {
                    "Monkey": ["U"],
                    "Date": ["1-1-2001"],
                    "Amp2": [0],
                    "Width2": [0],
                    "Freq2": [0],
                    "Dur2": [0],
                    "Active Channels": [0],
                    "Return Channels": [0],
                    "Amp1": [0],
                    "Width1": [0],
                    "Freq1": [0],
                    "Dur1": [0],
                }
            )
        ),
    )

    store_data = store_data.to_dict(orient="split")
    store_data["index_names"] = (
        "Monkey",
        "Date",
        "Amp2",
        "Width2",
        "Freq2",
        "Dur2",
        "Active Channels",
        "Return Channels",
        "Amp1",
        "Width1",
        "Freq1",
        "Dur1",
    )
    df = pa.points.from_store(json.dumps(store_data))
    print(df.columns)
    pa.points.schema.validate(df)
