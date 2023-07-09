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

import pandas as pd

from psychoanalyze.data import blocks


def test_thresholds() -> None:
    """Tests threshold plot."""
    data = pd.DataFrame(
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
