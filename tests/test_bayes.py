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
