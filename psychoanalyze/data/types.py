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

"""Pandera schemas for psychoanalyze dataframes.

Contains data table schemas of the hierarchical entities described above.
"""
from pandera import (
    Column,
    DataFrameModel,
    DataFrameSchema,
    Index,
    MultiIndex,
    typing,
)

session_dims = ["Monkey", "Date"]
block_stim_dims = ["Amp2", "Width2", "Freq2", "Dur2"]
block_channel_dims = ["Active Channels", "Return Channels"]
block_dims = block_stim_dims + block_channel_dims
point_dims = ["Amp1", "Width1", "Freq1", "Dur1"]

block_index_levels = session_dims + block_dims
points_index_levels = block_index_levels + point_dims


points = DataFrameSchema(
    {
        "n": Column(int),
        "Hits": Column(int),
        "Hit Rate": Column(float),
        "logit(Hit Rate)": Column(float),
    },
    index=Index(float, name="Intensity", unique=True),
)

trials = DataFrameSchema(
    columns={
        "Intensity": Column(float),
        "Result": Column(int),
    },
)


blocks = DataFrameSchema(
    columns={"Threshold": Column(dtype=float), "width": Column(dtype=float)},
    index=MultiIndex(
        [
            Index(str, name="Monkey"),
            Index("datetime64", name="Date", coerce=True),
        ]
        + [Index(float, name=dim) for dim in block_stim_dims]
        + [Index(int, name=dim) for dim in block_channel_dims],
    ),
)


psi_animation = DataFrameSchema(
    {
        "Trial": Column(int),
        "Intensity": Column(float),
        "Hit Rate": Column(float),
    },
)


class PsiAnimation(DataFrameModel):
    """Pandera type for psychometric function animation dataset."""

    trial_id: typing.Series[int]
    intensity: typing.Series[float]
    hit_rate: typing.Series[float]


class PsiAnimationFrame(DataFrameModel):
    """Pandera type for a single psychometric function animation frame."""

    intensity: typing.Series[float]
    hit_rate: typing.Series[float]


class Blocks(DataFrameModel):
    """Blocks type for Pandera."""

    slope: float
    threshold: float


class Points(DataFrameModel):
    """Pandera data type."""

    n: int
    Hits: int
    block_id: int


class Trials(DataFrameModel):
    """Trials data type for pandera + mypy type checking."""

    result: int
    intensity: typing.Index[float]
