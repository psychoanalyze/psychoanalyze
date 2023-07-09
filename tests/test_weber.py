# Copyright 2023 Tyler Schlichenmeyer

# This file is part of PsychoAnalyze.
# PsychoAnalyze is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# PsychoAnalyze is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with Foobar.
# If not, see <https://www.gnu.org/licenses/>.

"""Test psychoanalyze.weber functions."""
from pathlib import Path

import pandas as pd

from psychoanalyze.analysis import weber
from psychoanalyze.data import types


def test_aggregate() -> None:
    """Makes sure that thresholds at a given stimulus intensity are aggregated."""
    curve_data = pd.DataFrame.from_records(
        [
            {"Reference Charge (nC)": 0, "Difference Threshold (nC)": 0},
            {"Reference Charge (nC)": 0, "Difference Threshold (nC)": 2},
        ],
        index=pd.MultiIndex.from_frame(
            pd.DataFrame({"Monkey": ["U", "U"], "Dimension": ["Amp", "Amp"]}),
        ),
    )
    agg = weber.aggregate(curve_data)
    assert (
        agg.iloc[0, agg.columns.get_loc("Difference Threshold (nC)")]
        == curve_data["Difference Threshold (nC)"].mean()
    )


def test_load(tmp_path: Path) -> None:
    """Given weber_curves.csv, loads dataframe."""
    pd.DataFrame(
        {level_name: [] for level_name in types.block_index_levels}
        | {
            "Reference Charge (nC)": [],
            "location_CI_5": [],
            "location_CI_95": [],
            "Fixed_Param_Value": [],
            "Threshold_Charge_nC": [],
        },
    ).to_csv(tmp_path / "weber_curves.csv", index_label=False)
    assert len(weber.load(tmp_path / "weber_curves.csv")) == 0
