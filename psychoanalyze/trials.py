import random
import pandas as pd
import numpy as np


def fake(n: int, x: set) -> pd.DataFrame:
    """Generate a small set of trial data"""
    X = random.choices(list(x), k=n)
    result = [np.random.binomial(1, x / max(X)) for x in X]
    return pd.DataFrame(
        {
            "Result": result,
            "x": X,
        }
    )
