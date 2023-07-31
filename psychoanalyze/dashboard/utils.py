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

"""Helper functions for the dashboard."""

import base64
import io
import zipfile

import pandas as pd


def process_upload(contents: str, filename: str) -> pd.DataFrame:
    """Process a file upload.

    Params:
        contents: The contents of the uploaded file.
        filename: The name of the uploaded file.

    Returns:
        A dataframe of the uploaded file.
    """
    _, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    if "zip" in filename:
        with zipfile.ZipFile(io.BytesIO(decoded)) as z:
            trials = pd.read_csv(z.open("trials.csv"))
    else:
        trials = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    return trials
