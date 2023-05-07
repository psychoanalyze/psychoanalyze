import psychoanalyze as pa
import pandas as pd
from scipy.special import expit  # type: ignore
import plotly.express as px  # type: ignore
import datetime


def test_from_trials():
    trials = pd.Series([], name="Result", index=pd.Index([], name="Intensity"))
    points = pa.points.from_trials(trials)
    assert "Hit Rate" in points.columns


def test_from_trials_sums_n_per_intensity_level():
    trials = pd.Series(
        [0, 0],
        name="Result",
        index=pd.Index([0, 1], name="Intensity"),
    )
    points = pa.points.from_trials(trials)
    assert all(
        points["n"]
        == pd.Series([1, 1], index=pd.Index([0, 1], name="Intensity"), name="n")
    )


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


def test_plot():
    s = pd.DataFrame(
        {"x": [], "n": [], "Hits": []},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame({level: [] for level in pa.schemas.points_index_levels})
        ),
        dtype=float,
    )
    fig = pa.points.plot(s)
    assert fig.layout.yaxis.title.text == "Hit Rate"
    assert fig.layout.xaxis.title.text == "x"


def test_generate():
    x = list(range(-3, 4))
    n = [10] * 8
    p = expit(x)
    points = pa.points.generate(x, n, p)
    assert all(points.index.values == x)
    assert points.name == "Hit Rate"


def test_datatable():
    data = pd.DataFrame(
        index=pd.MultiIndex.from_frame(
            pd.DataFrame({"Amp1": [0.1212345], "Hit Rate": [0.1234543], "n": [1]})
        )
    )
    datatable = pa.points.datatable(data)
    amp_column = [column for column in datatable.columns if column["name"] == "Amp1"]
    assert amp_column[0]["format"].to_plotly_json()["specifier"] == ".2f"


def test_combine_plots():
    plot1 = px.scatter(pd.DataFrame({"A": [1]}))
    plot2 = px.line(pd.DataFrame({"B": [1]}))
    fig = pa.points.combine_plots(plot1, plot2)
    assert len(fig.data) == 2


def test_no_dimension():
    session_cols = ["Monkey", "Date"]
    ref_stim_cols = ["Amp2", "Width2", "Freq2", "Dur2"]
    channel_config = ["Active Channels", "Return Channels"]
    test_stim_cols = ["Amp1", "Width1", "Freq1", "Dur1"]
    points = pd.DataFrame(
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
    dimension = pa.points.dimension(points)
    assert dimension is None


def test_fixed_magnitudes():
    points = pd.DataFrame(
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
    fixed_magnitude = pa.points.fixed_magnitude(points)
    assert fixed_magnitude == 0


def test_fit_no_data(mocker):
    mocker.stub("psignifit")
    points = pd.DataFrame({"n": [], "Hits": [], "x": []})
    fit = pa.points.fit(points)
    assert {"Threshold", "err+", "err-"} <= set(fit.index.values)


def test_fit_data(tmp_path):
    points = pd.DataFrame({"n": [0], "Hits": [0], "x": [0]})
    fit = pa.points.fit(
        points,
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
