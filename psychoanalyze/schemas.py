import pandera as pr
from pandera.typing import Series


session_dims = ["Monkey", "Date"]
block_stim_dims = ["Amp2", "Width2", "Freq2", "Dur2"]
block_channel_dims = ["Active Channels", "Return Channels"]
block_dims = block_stim_dims + block_channel_dims
point_dims = ["Amp1", "Width1", "Freq1", "Dur1"]

block_index_levels = session_dims + block_dims
points_index_levels = block_index_levels + point_dims


points = pr.DataFrameSchema(
    {
        "n": pr.Column(int),
        "Intensity": pr.Column(float),
        "Hits": pr.Column(int),
    }
)

blocks = pr.DataFrameSchema(
    columns={"Threshold": pr.Column(dtype=float), "width": pr.Column(dtype=float)},
    index=pr.MultiIndex(
        [
            pr.Index(str, name="Monkey"),
            pr.Index("datetime64", name="Date", coerce=True),
        ]
        + [pr.Index(float, name=dim) for dim in block_stim_dims]
        + [pr.Index(int, name=dim) for dim in block_channel_dims]
    ),
)


trials = pr.DataFrameSchema(
    {"Result": pr.Column(int, coerce=True)},
    index=pr.MultiIndex(
        [
            pr.Index(str, name="Monkey"),
            pr.Index("datetime64", name="Date", coerce=True),
        ]
        + [pr.Index(float, name=dim) for dim in block_stim_dims]
        + [pr.Index(int, name=dim) for dim in block_channel_dims]
        + [pr.Index(float, name=dim) for dim in point_dims]
    ),
    coerce=True,
)

psi_animation = pr.DataFrameSchema(
    {
        "Trial": pr.Column(int),
        "Intensity": pr.Column(float),
        "Hit Rate": pr.Column(float),
    }
)


class PsiAnimation(pr.DataFrameModel):
    trial_id: Series[int]
    intensity: Series[float]
    hit_rate: Series[float]


class PsiAnimationFrame(pr.DataFrameModel):
    intensity: Series[float]
    hit_rate: Series[float]
