import psychoanalyze as pa
import pandas as pd
import datatest as dt  # type: ignore
import pytest
import datetime


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


def test_load_pre_fitted(tmp_path):
    fullpath = tmp_path / "blocks.csv"
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
            "Threshold": [],
            "Dimension": [],
            "Fixed Magnitude": [],
        }
    ).to_csv(fullpath, index=False)
    blocks = pa.blocks.load(fullpath)
    assert set(blocks.columns) == {"Threshold", "Dimension", "Fixed Magnitude"}


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


# def test_load_no_fit(tmp_path, mocker):
#     mocker.patch(pa.points.load)
#     pd.DataFrame({"n": [], "Hits": [], "x": []}).to_csv(tmp_path / "trials.csv")
#     blocks = pa.blocks.load(tmp_path / "blocks.csv")
#     assert set(blocks.columns) <= {"Threshold", "Dimension", "Fixed Magnitude"}
#     assert os.path.exists(tmp_path / "blocks.csv")


# def test_fits(points_empty):
#     fits = pa.blocks.fits(points_empty)
#     assert fits.name == "Threshold"


# def test_fixed_magnitudes(points_empty):
#     fixed_magnitudes = pa.blocks.fixed_magnitudes(points_empty)
#     assert fixed_magnitudes.name == "Fixed Magnitudes"
