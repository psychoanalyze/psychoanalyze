import psychoanalyze as pa
import pandas as pd
import datatest as dt  # type: ignore
import os


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


def test_from_trials():
    index = pd.MultiIndex.from_frame(
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
    )
    trials = pd.DataFrame({"Result": []}, index=index)
    blocks = pa.blocks.from_trials(trials)
    assert len(blocks) == 0
    assert "Dimension" in blocks.columns


def test_from_points():
    points = pd.DataFrame(
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
    blocks = pa.blocks.from_points(points)
    assert {"Dimension", "Fixed Magnitude"} <= set(blocks.columns)
    assert "Monkey" in blocks.index.names
    # mocker.patch(
    #     "psychoanalyze.points.fit",
    #     return_value=pd.Series(
    #         index=pd.MultiIndex.from_frame(pd.DataFrame({"Monkey": [], "Amp1": []}))
    #     ),
    # )
    # df = pd.DataFrame(
    #     {"x": list(range(8)), "Hits": list(range(8))},
    #     index=pd.MultiIndex.from_frame(
    #         pd.DataFrame({"Amp1": [1] * 8, "Width1": [1] * 8})
    #     ),
    # )
    # df["n"] = 1000
    # pa.blocks.fit(df)


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


def test_load_no_fit(tmp_path):
    blocks = pa.blocks.load(tmp_path / "blocks.csv")
    assert set(blocks.columns) == {"Threshold", "Dimension", "Fixed Magnitude"}
    assert os.path.exists(tmp_path / "blocks.csv")


# def test_from_points():
#     points = pd.DataFrame(
#         {"n": [], "Hits": [], "x": []},
#         index=pd.MultiIndex.from_frame(
#             pd.DataFrame(
#                 {
#                     "Monkey": [],
#                     "Date": [],
#                     "Amp2": [],
#                     "Width2": [],
#                     "Freq2": [],
#                     "Dur2": [],
#                     "Active Channels": [],
#                     "Return Channels": [],
#                     "Amp1": [],
#                     "Width1": [],
#                     "Freq1": [],
#                     "Dur1": [],
#                 }
#             )
#         ),
#     )
#     fits = pa.blocks.fit(points)
#     assert "Threshold" in fits.columns
