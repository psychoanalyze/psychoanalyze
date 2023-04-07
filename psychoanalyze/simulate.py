import random
import pandas as pd


def run(n_trials: int) -> pd.Series:
    """Run a simulation"""
    return pd.Series(
        [random.random() for _ in range(n_trials)],
        index=pd.Index(list(range(n_trials)), name="TrialID"),
    )
