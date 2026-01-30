
import polars as pl

import psychoanalyze.analysis.bayes as pa_bayes


def test_bayes():
    """Test plotting bayesian representation of psi data."""
    simulated = pl.DataFrame(
        {
            "x": [-4, -2, 0, 2, 4],
            "Hit Rate": [0.01, 0.19, 0.55, 0.81, 0.99],
        },
    )
    estimated = pl.DataFrame(
        {
            "Hit Rate": [-4, -2, 0, 2, 4],
            "value": [0.011, 0.2, 0.56, 0.80, 0.98],
        },
    )
    fig = pa_bayes.plot(simulated, estimated)
    assert fig.layout.xaxis.title.text == "x"
    assert fig.layout.yaxis.title.text == "Hit Rate"
