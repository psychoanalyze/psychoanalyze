import psychoanalyze as pa
import pandas as pd


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
    df = pa.points.from_trials(df.reset_index())
    assert len(df) == 2
    assert list(df["n"].values) == [1, 1]


def test_amp_dimension():
    df = pd.DataFrame({"Amp1": [1, 2], "Width1": [1, 1]})
    assert pa.points.dimension(df) == "Amp"


def test_width_dimension():
    df = pd.DataFrame({"Amp1": [1, 1], "Width1": [1, 2]})
    assert pa.points.dimension(df) == "Width"


def test_both_dimensions():
    df = pd.DataFrame({"Amp1": [1, 2], "Width1": [1, 2]})
    assert pa.points.dimension(df) == "Both"


def test_fit(mocker):
    mocker.patch("cmdstanpy.CmdStanModel")
    df = pd.DataFrame({"Amp1": [], "n": [], "Hits": []})
    fit = pa.points.fit(df)
