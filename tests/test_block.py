import psychoanalyze as pa
import pandas as pd
import datatest as dt  # type: ignore


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
    df = pd.DataFrame({"Result": [0, 1]})
    curves = pa.blocks.from_trials(df)
    assert len(curves) == 1


def test_from_points(mocker):
    mocker.patch(
        "psychoanalyze.points.dimension", return_value=pd.DataFrame({"Dimension": []})
    )
    mocker.patch("psychoanalyze.points.fit", return_value=pd.Series(name="session"))
    df = pd.DataFrame(
        {"x": list(range(8)), "Hits": list(range(8))},
        index=pd.Index([1] * 8, name="session"),
    )
    df["n"] = 1000
    blocks = pa.blocks.from_points(df, ("session"))
    assert "Dimension" in list(blocks.columns)


def test_load(tmp_path):
    df = pd.DataFrame(
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
            "Result": [],
        }
    )
    df.to_csv(tmp_path / "points.csv")

    a
