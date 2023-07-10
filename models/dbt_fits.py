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

"""A dbt model for fitting psychometric curves."""

import random

import arviz as az
import bambi as bmb
import pandas as pd
from xarray import Dataset


def model(dbt, session) -> pd.DataFrame | Dataset:  # noqa: ARG001, ANN001
    """Fit dbt model for psychometric curve using pymc."""
    trials = dbt.ref("trials")

    trials = pd.DataFrame(
        {
            "Result": [random.choice([0, 1]) for _ in range(100)],
            "Intensity": [random.choice([0, 1, 2, 3, 4]) for _ in range(100)],
        },
    )

    model = bmb.Model("Result ~ Intensity", trials, family="bernoulli")
    fitted = model.fit()

    return az.summary(fitted, round_to=2)
