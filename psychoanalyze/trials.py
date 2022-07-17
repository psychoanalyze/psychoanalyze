import pandas as pd
import numpy as np
import psychoanalyze as pa
from pathlib import Path
import random

dims = ["Amp1", "Width1", "Freq1", "Dur1"]


def generate(n, stim_levels=list(range(-3, 4))):
    return pd.DataFrame(
        {"Result": np.random.binomial(1, 0.5, n)},
        index=pd.Index(
            random.choices(stim_levels, k=n),
            name="x",
        ),
    )


def load(filepath: Path):
    return pd.read_csv(
        filepath, index_col=pa.sessions.dims + pa.blocks.dims + pa.trials.dims
    )
