import psychoanalyze as pa
import pandas as pd
import psignifit as ps
from scipy.special import expit
import json
import plotly.express as px
import datetime


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


def test_plot():
    s = pd.DataFrame(
        {"x": [], "n": [], "Hit Rate": []},
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


def test_load(tmp_path):
    pd.DataFrame(
        {"Trial ID": [1, 2, 3], "Result": [1] * 3},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {
                    "Monkey": ["U"] * 3,
                    "Date": pd.to_datetime(["2000-01-01"] * 3),
                    "Amp2": [0] * 3,
                    "Width2": [0] * 3,
                    "Freq2": [0] * 3,
                    "Dur2": [0] * 3,
                    "Active Channels": [0] * 3,
                    "Return Channels": [0] * 3,
                    "Amp1": [2] * 3,
                    "Width1": [0] * 3,
                    "Freq1": [0] * 3,
                    "Dur1": [0] * 3,
                }
            )
        ),
    ).to_csv(tmp_path / "trials.csv")
    pd.DataFrame(pa.schemas.trials.example(0).reset_index()).to_csv(
        tmp_path / "points.csv", index_label=False
    )
    points = pa.points.load(tmp_path)
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
    store_data = pd.DataFrame(
        {"Result": [1]},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {"Monkey": ["U"], "Date": ["1-1-2001"]}
                | {
                    level: [0]
                    for level in pa.schemas.block_dims + pa.schemas.point_dims
                }
            )
        ),
    )
    mocker.patch("psychoanalyze.trials.from_store", return_value=store_data)

    store_data = store_data.to_dict(orient="split")
    store_data["index_names"] = pa.schemas.points_index_levels
    df = pa.points.from_store(json.dumps(store_data))
    pa.schemas.points.validate(df)


def test_combine_plots():
    plot1 = px.scatter(pd.DataFrame({"A": [1]}))
    plot2 = px.line(pd.DataFrame({"B": [1]}))
    fig = pa.points.combine_plots(plot1, plot2)
    assert len(fig.data) == 2


def test_fit_prep():
    points_df = pa.schemas.points.example(0)
    ready_for_fit = pa.points.prep_fit(points_df, "Amp1")
    points_df = points_df.reset_index()
    assert ready_for_fit["X"] == len(points_df)
    assert list(ready_for_fit["x"]) == list(points_df["Amp1"].to_numpy())
    assert list(ready_for_fit["N"]) == list(points_df["n"].to_numpy())
    assert list(ready_for_fit["hits"]) == list(points_df["Hits"].to_numpy())


# def test_fit():
#     points = pd.DataFrame({"x": [], "n": [], "Hits": []})
#     fit = pa.points.fit(points)
#     assert fit.keys() <= {"Threshold", "width", "gamma", "lambda", "beta"}


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


def test_to_block():
    points = pd.DataFrame(
        {"n": [], "Hits": [], "x": []},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {
                    "Monkey": [],
                    "Date": [],
                    "Amp2": [],
                    "Width2": [],
                    "Freq2": [],
                    "Dur2": [],
                    "Active Channels": [],
                    "Return Channels": [],
                    "Amp1": [],
                    "Width1": [],
                    "Freq1": [],
                    "Dur1": [],
                }
            )
        ),
    )
    block = pa.points.to_block(points)
    assert set(block.index) <= {"Threshold", "Fixed Magnitude", "Dimension", "n Levels"}


def test_fit_no_data(mocker):
    mocker.stub("psignifit")
    points = pd.DataFrame({"n": [], "Hits": [], "x": []})
    fit = pa.points.fit(points)
    assert {"Threshold", "err+", "err-"} <= set(fit.index.values)


def test_fit_data(monkeypatch, tmp_path):
    monkeypatch.setattr(
        ps, "psignifit", lambda data, options: {"Fit": [None, None, None, None]}
    )
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
