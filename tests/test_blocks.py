import psychoanalyze as pa
import pandas as pd
import datatest as dt  # type: ignore
import pytest
import datetime
import numpy as np
import pandas.api.types as ptypes


@pytest.fixture
def points_empty():
    return pd.DataFrame(
        {"n": [], "Hits": []},
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


@pytest.fixture
def path(tmp_path):
    return tmp_path / "blocks.csv"


@pytest.fixture
def blocks():
    return pd.DataFrame(
        {
            "Monkey": ["U"],
            "Date": ["2022-01-01"],
            "Amp2": [0],
            "Width2": [0],
            "Freq2": [0],
            "Dur2": [0],
            "Active Channels": [0],
            "Return Channels": [0],
            "Threshold": [1],
            "Dimension": ["Amp"],
            "Fixed Magnitude": [0],
        }
    )


def test_generate():
    df = pa.blocks.generate()
    assert len(df) == 7


def test_add_posterior():
    data = pd.DataFrame({"Hit Rate": [1]})
    posterior = pd.DataFrame({"p": [1]})
    output = pa.blocks.add_posterior(data, posterior)
    assert len(output[output["Type"] == "Observed"])


def test_hit_rate():
    df = pd.DataFrame({"Hits": [5], "n": [10]})
    dt.validate(pa.blocks.hit_rate(df), pd.Series([0.5]))


def test_xrange_index():
    x_min = 0
    x_max = 100
    index = pa.blocks.xrange_index(x_min, x_max)
    assert max(index) == x_max
    assert min(index) == x_min
    assert index.name == "x"


def test_prep_psych_curve(mocker):
    curves_data = pd.DataFrame({"Hits": [1] * 3, "n": [1] * 3})
    x = pd.Index([1, 2, 3], name="x")
    y = "p"

    mocker.patch("psychoanalyze.points.fit")
    assert pa.blocks.prep_psych_curve(curves_data=curves_data, x=x, y=y)


def test_transform():
    pa.blocks.transform(pd.Series(), y="p")


def test_from_points(points_empty):
    blocks = pa.blocks.from_points(points_empty)
    assert blocks.index.names == [
        "Monkey",
        "Date",
        "Amp2",
        "Width2",
        "Freq2",
        "Dur2",
        "Active Channels",
        "Return Channels",
    ]


def test_plot_fits():
    fits = pd.DataFrame({"Threshold": [0], "width": [1]})
    fig = pa.blocks.plot_fits(fits)
    assert len(fig.data)


def test_load_pre_fitted(path, blocks):
    blocks.to_csv(path, index=False)
    blocks = pa.blocks.load(path)
    assert set(blocks.columns) == {"Threshold", "Dimension", "Fixed Magnitude"}
    dates = blocks.index.get_level_values("Date")
    assert ptypes.is_datetime64_any_dtype(dates)


def test_blocks_load_monkey(path, blocks):
    blocks.to_csv()


def test_from_points_amp_dim():

    amp_points_index = pd.MultiIndex.from_frame(
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
    )
    amp_points = pd.DataFrame(
        {"n": [1, 1], "Hits": [0, 1], "x": [0, 1]}, index=amp_points_index
    )
    width_points_index = pd.MultiIndex.from_frame(
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
                "Amp1": [0] * 2,
                "Width1": [0, 1],
                "Freq1": [0] * 2,
                "Dur1": [0] * 2,
            }
        )
    )
    width_points = pd.DataFrame(
        {"n": [1, 1], "Hits": [0, 1], "x": [0, 1]}, index=width_points_index
    )
    points = pd.concat([amp_points, width_points])
    blocks = pa.blocks.from_points(points, dim="Amp")
    assert len(blocks) == 1
    assert "Width1" in blocks.index.names


def test_blocks_day():
    index = pd.MultiIndex.from_frame(
        pd.DataFrame(
            {
                "Monkey": ["U"],
                "Date": [datetime.date(2001, 1, 1)],
                "Amp2": [0],
                "Width2": [0],
                "Freq2": [0],
                "Dur2": [0],
                "Active Channels": [0],
                "Return Channels": [0],
            }
        )
    )
    blocks = pd.DataFrame(index=index)
    intervention_dates = pd.DataFrame(
        {"Surgery Date": [datetime.date(2000, 12, 31)]},
        index=pd.Index(["U"], name="Monkey"),
    )
    days = pa.blocks.days(blocks, intervention_dates)
    pd.testing.assert_series_equal(days, pd.Series([1], name="Days", index=index))


def test_n_trials():
    trials = pd.DataFrame(
        {"Result": [1] * 3},
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {
                    "Monkey": ["U"] * 3,
                    "Date": [datetime.date(2000, 1, 1)] * 3,
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
    )
    assert pa.blocks.n_trials(trials).iloc[0] == 3
