import pandas as pd
import numpy as np


def generate(n, stim_levels=list(range(-4, 5))):
    return pd.DataFrame(
        {"Result": np.random.binomial(1, 0.5, n)},
        index=pd.Index(np.random.choice(stim_levels, size=n), name="x"),
    )
