
import pandas as pd

import psychoanalyze.analysis.bayes as pa_bayes
def test_bayes():
    """Test plotting bayesian representation of psi data."""
    simulated = pd.DataFrame(
        {
            "x": [-4, -2, 0, 2, 4],
            "Hit Rate": [0.01, 0.19, 0.55, 0.81, 0.99],
        },
    )
    index = pd.Index([-4, -2, 0, 2, 4], name="Hit Rate")
    estimated = pd.Series([0.011, 0.2, 0.56, 0.80, 0.98], index=index)
    fig = pa_bayes.plot(simulated, estimated)
    assert fig.layout.xaxis.title.text == "x"
    assert fig.layout.yaxis.title.text == "Hit Rate"
