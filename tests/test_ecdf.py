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

from psychoanalyze.analysis import ecdf


def test_ecdf_location_no_data():
    blocks = pd.DataFrame({"location": []})
    ecdf_fig = ecdf.plot(blocks, "location")

    assert ecdf_fig.layout.xaxis.title.text == "location"


def test_ecdf_width_no_data():
    blocks = pd.DataFrame({"width": []})
    ecdf_fig = ecdf.plot(blocks, "width")

    assert ecdf_fig.layout.xaxis.title.text == "width"
