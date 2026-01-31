
import polars as pl

from psychoanalyze.data import blocks


def test_thresholds() -> None:
    """Tests threshold plot."""
    data = pl.DataFrame(
        {
            "Subject": ["A", "B"],
            "5%": [1, 2],
            "50%": [1, 2],
            "95%": [1, 2],
            "Block": [1, 2],
        },
    )
    fig = blocks.plot_thresholds(data)
    subjects = {trace["legendgroup"] for trace in fig.data}
    assert subjects == {"A", "B"}
    assert fig.layout.xaxis.title.text == "Block"
    assert fig.layout.yaxis.title.text == "50%"


def test_fit_returns_inferencedata() -> None:
    """Fit returns posterior draws for block data."""
    trials_df = pl.DataFrame(
        {
            "Intensity": [0.0, 1.0, 2.0, 3.0],
            "Result": [0, 0, 1, 1],
        },
    )
    idata = blocks.fit(trials_df, draws=50, tune=50, chains=1, random_seed=1)
    summary = blocks.summarize_fit(idata)
    assert set(summary) >= {"intercept", "slope", "threshold"}
