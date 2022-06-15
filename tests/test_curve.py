import psychoanalyze as pa
import pandas as pd


def test_generate():
    assert len(pa.curve.generate()) == 7


def test_add_posterior():
    data = pd.DataFrame({"Hit Rate": [1]})
    posterior = pd.DataFrame({"p": [1]})
    output = pa.curve.add_posterior(data, posterior)
    assert len(output[output["Type"] == "Observed"])
