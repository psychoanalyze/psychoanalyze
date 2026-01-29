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

"""Bayesian analysis of psychophysical data."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot(simulated: pd.DataFrame, estimated: pd.Series) -> go.Figure:
    """Plot Psychometric curve to emphasize Bayesian posteriors."""
    combined = pd.concat(
        [simulated.reset_index(), estimated.reset_index()],
        keys=["Simulated", "Estimated"],
        names=["Type"],
    )
    return px.scatter(
        combined.reset_index(),
        x="x",
        y="Hit Rate",
        color="Type",
        template="plotly_white",
    )
