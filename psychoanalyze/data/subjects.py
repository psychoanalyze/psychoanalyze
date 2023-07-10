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

"""Data transformation functions for subject-level data."""
import string
from pathlib import Path

import pandas as pd

from psychoanalyze.data import sessions


def load(data_path: Path) -> pd.DataFrame:
    """Load subject data from csv."""
    return pd.read_csv(
        data_path / "subjects.csv",
        index_col="Monkey",
        parse_dates=["Surgery Date"],
    )


def generate_letter_names(n_subjects: int) -> list[str]:
    """Generate a list of dummy subjects using capital letters in alph. order."""
    return list("ABCDEFG"[:n_subjects])


def generate_trials(
    n_trials: int,
    model_params: dict[str, float],
    n_days: int,
    n_subjects: int,
) -> pd.DataFrame:
    """Generate trial-level data, including subject-level info."""
    return pd.concat(
        {
            subj: sessions.generate_trials(n_trials, model_params, n_days)
            for subj in string.ascii_uppercase[:n_subjects]
        },
        names=["Subject"],
    )
