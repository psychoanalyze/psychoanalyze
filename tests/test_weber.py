
"""Test psychoanalyze.weber functions."""

from pathlib import Path

import polars as pl

from psychoanalyze.analysis import weber
from psychoanalyze.data import types


def test_aggregate() -> None:
    """Makes sure that thresholds at a given stimulus intensity are aggregated."""
    curve_data = pl.DataFrame(
        {
            "Monkey": ["U", "U"],
            "Dimension": ["Amp", "Amp"],
            "Reference Charge (nC)": [0, 0],
            "Difference Threshold (nC)": [0, 2],
        },
    )
    agg = weber.aggregate(curve_data)
    mean_val = curve_data["Difference Threshold (nC)"].mean()
    agg_val = agg.filter(
        (pl.col("Monkey") == "U") & (pl.col("Dimension") == "Amp"),
    )["Difference Threshold (nC)"][0]
    assert agg_val == mean_val


def test_load(tmp_path: Path) -> None:
    """Given weber_curves.csv, loads dataframe."""
    cols = {level_name: [] for level_name in types.block_index_levels} | {
        "Date": [],
        "Reference Charge (nC)": [],
        "location_CI_5": [],
        "location_CI_95": [],
        "Fixed_Param_Value": [],
        "Threshold_Charge_nC": [],
    }
    df = pl.DataFrame(cols).cast(
        {
            "location_CI_5": pl.Float64,
            "location_CI_95": pl.Float64,
            "Fixed_Param_Value": pl.Float64,
            "Threshold_Charge_nC": pl.Float64,
        },
    )
    df.write_csv(tmp_path / "weber_curves.csv")
    assert len(weber.load(tmp_path / "weber_curves.csv")) == 0
