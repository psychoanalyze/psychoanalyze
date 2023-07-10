# Copyright 2023 Tyler Schlichenmeyer

# This file is part of PsychoAnalyze.
# PsychoAnalyze is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# PsychoAnalyze is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# PsychoAnalyze. If not, see <https://www.gnu.org/licenses/>.

"""Data modules and general-purpose data transformation utilities.

Functions:

- [`psychoanalyze.data.load`][psychoanalyze.data.load]

Submodules:

- [`psychoanalyze.data.blocks`][psychoanalyze.data.blocks]
- [`psychoanalyze.data.points`][psychoanalyze.data.points]
- [`psychoanalyze.data.trials`][psychoanalyze.data.trials]
- [`psychoanalyze.data.sessions`][psychoanalyze.data.sessions]
- [`psychoanalyze.data.subjects`][psychoanalyze.data.subjects]
- [`psychoanalyze.data.types`][psychoanalyze.data.types]
"""
from pathlib import Path

import pandas as pd

from psychoanalyze.data import blocks, points, sessions, subjects


def load(
    data_dir: Path = Path("data"),
) -> dict[str, pd.DataFrame]:
    """Load all tables into dict."""
    return {
        "Sessions": sessions.load(data_dir),
        "Subjects": subjects.load(data_dir),
        "Blocks": blocks.load(data_dir),
        "Points": points.load(data_dir),
    }
