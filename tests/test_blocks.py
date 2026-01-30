
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
