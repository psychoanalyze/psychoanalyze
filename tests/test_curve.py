import psychoanalyze as pa
import pandas as pd
import datatest as dt


def test_generate():
    df = pa.curve.generate()
    assert len(df) == 7


def test_add_posterior():
    data = pd.DataFrame({"Hit Rate": [1]})
    posterior = pd.DataFrame({"p": [1]})
    output = pa.curve.add_posterior(data, posterior)
    assert len(output[output["Type"] == "Observed"])


def test_hit_rate():
    df = pd.DataFrame({"Hits": [5], "n": [10]})
    dt.validate(pa.curve.hit_rate(df), pd.Series([0.5]))


def test_xrange_index():
    x_min = 0
    x_max = 100
    index = pa.curve.xrange_index(x_min, x_max)
    assert max(index) == x_max
    assert min(index) == x_min
    assert index.name == "x"


def test_prep_psych_curve():
    curves_data = pd.DataFrame({"Hits": [1] * 3, "n": [1] * 3})
    x = pd.Index([1, 2, 3], name="x")
    y = "p"
    return pa.curve.prep_psych_curve(curves_data=curves_data, x=x, y=y)


def test_transform():
    pa.curve.transform(pd.Series(), y="p")
