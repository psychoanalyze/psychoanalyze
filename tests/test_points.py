import psychoanalyze as pa
import pandas as pd
from scipy.special import expit


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
    s = pd.Series(
        [], name="Hit Rate", index=pd.Index([], name="Amplitude (µA)"), dtype=float
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
