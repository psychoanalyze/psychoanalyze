import datetime

import pandas as pd
import plotly.express as px
from scipy.special import expit

from psychoanalyze import points


def test_from_trials_sums_n_per_intensity_level():
    trials = pd.DataFrame(
        {
            "Result": [0, 0]
        },
        index=pd.Index([0, 1], name="Intensity")
    )
    _points = points.from_trials(trials)
    assert all(
        _points["n"]
        == pd.Series([1, 1], index=pd.Index([0, 1], name="Intensity"), name="n")
    )


def test_amp_dimension():
    df = pd.DataFrame(
        index=pd.MultiIndex.from_frame(pd.DataFrame({"Amp1": [1, 2], "Width1": [1, 1]}))
    )
    assert points.dimension(df) == "Amp"


def test_width_dimension():
    df = pd.DataFrame(
        index=pd.MultiIndex.from_frame(pd.DataFrame({"Amp1": [1, 1], "Width1": [1, 2]}))
    )
    assert points.dimension(df) == "Width"


def test_both_dimensions():
    df = pd.DataFrame(
        index=pd.MultiIndex.from_frame(pd.DataFrame({"Amp1": [1, 2], "Width1": [1, 2]}))
    )
    assert points.dimension(df) == "Both"


def test_plot():
    df = pd.DataFrame(
        {"Intensity": [], "Hit Rate": []}
    )
    fig = points.plot(df)
    assert fig.layout.yaxis.title.text == "Hit Rate"
    assert fig.layout.xaxis.title.text == "Intensity"


def test_generate():
    x = list(range(-3, 4))
    n = [10] * 8
    p = expit(x)
    _points = points.generate(x, n, p)
    assert all(_points.index.values == x)
    assert _points.name == "Hit Rate"


def test_datatable():
    data = pd.DataFrame(
        index=pd.MultiIndex.from_frame(
            pd.DataFrame({"Amp1": [0.1212345], "Hit Rate": [0.1234543], "n": [1]})
        )
    )
    datatable = points.datatable(data)
    amp_column = [column for column in datatable.columns if column["name"] == "Amp1"]
    assert amp_column[0]["format"].to_plotly_json()["specifier"] == ".2f"


def test_combine_plots():
    plot1 = px.scatter(pd.DataFrame({"A": [1]}))
    plot2 = px.line(pd.DataFrame({"B": [1]}))
    fig = points.combine_plots(plot1, plot2)
    assert len(fig.data) == 2


def test_no_dimension():
    session_cols = ["Monkey", "Date"]
    ref_stim_cols = ["Amp2", "Width2", "Freq2", "Dur2"]
    channel_config = ["Active Channels", "Return Channels"]
    test_stim_cols = ["Amp1", "Width1", "Freq1", "Dur1"]
    _points = pd.DataFrame(
        {"n": [], "Hits": []},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {
                    field: []
                    for field in session_cols
                    + ref_stim_cols
                    + channel_config
                    + test_stim_cols
                }
            )
        ),
    )
    dimension = points.dimension(_points)
    assert dimension is None


def test_fixed_magnitudes():
    _points = pd.DataFrame(
        {"n": [1, 1], "Hits": [0, 1]},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {
                    "Monkey": ["U"] * 2,
                    "Date": ["2020-01-01"] * 2,
                    "Amp2": [0] * 2,
                    "Width2": [0] * 2,
                    "Freq2": [0] * 2,
                    "Dur2": [0] * 2,
                    "Active Channels": [0] * 2,
                    "Return Channels": [0] * 2,
                    "Amp1": [0, 1],
                    "Width1": [0] * 2,
                    "Freq1": [0] * 2,
                    "Dur1": [0] * 2,
                }
            )
        ),
    )
    fixed_magnitude = points.fixed_magnitude(_points)
    assert fixed_magnitude == 0


def test_fit_data(tmp_path):
    _points = pd.DataFrame({"n": [0], "Hits": [0], "x": [0]})
    fit = points.fit(
        _points,
        save_to=tmp_path / "fit.csv",
        block=("U", datetime.date(2000, 1, 1), 0, 0, 0, 0, 0, 0),
    )
    assert set(fit.columns) == {
        "Threshold",
        "width",
        "gamma",
        "lambda",
        "err+",
        "err-",
    }
    assert "Date" in pd.read_csv(tmp_path / "fit.csv").columns
