"""Pandera schemas for psychoanalyze dataframes."""
from pandera import Column, DataFrameModel, DataFrameSchema, Index, MultiIndex
from pandera.typing import Series

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
        "Intensity": Column(float),
        "Hits": Column(int),
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


trials = DataFrameSchema(
    {"Result": Column(int, coerce=True)},
    index=MultiIndex(
        [
            Index(str, name="Monkey"),
            Index("datetime64", name="Date", coerce=True),
        ]
        + [Index(float, name=dim) for dim in block_stim_dims]
        + [Index(int, name=dim) for dim in block_channel_dims]
        + [Index(float, name=dim) for dim in point_dims],
    ),
    coerce=True,
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

    trial_id: Series[int]
    intensity: Series[float]
    hit_rate: Series[float]


class PsiAnimationFrame(DataFrameModel):

    """Pandera type for a single psychometric function animation frame."""

    intensity: Series[float]
    hit_rate: Series[float]
