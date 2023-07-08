"""Simulate psychometric data."""
import random
from typing import Any

import numpy as np
import pandas as pd
from pandera import Column, DataFrameSchema, Index, check_output


def weibull(
    x: np.ndarray[Any, np.dtype[np.floating[Any]]],
    alpha: float,
    beta: float,
) -> float:
    """Calculate psi using Weibull function."""
    return 1 - np.exp(-((x / alpha) ** beta))


def gumbel(x: np.ndarray[Any, np.dtype[Any]], alpha: float, beta: float) -> float:
    """Calculate psi using gumbel function."""
    return 1 - np.exp(-(10 ** (beta * (x - alpha))))


def quick(x: float, alpha: float, beta: float) -> float:
    """Calculate psi using quick function."""
    return 1 - 2 ** (-((x / alpha) ** beta))


def log_quick(x: float, alpha: float, beta: float) -> float:
    """Calculate psi using log_quick function."""
    return 1 - 2 ** (-(10 ** (beta * (x - alpha))))


def run(n_trials: int) -> pd.Series:
    """Run a simulation."""
    return pd.Series(
        [random.random() for _ in range(n_trials)],
        index=pd.Index(list(range(n_trials)), name="TrialID"),
    )


trials_schema = DataFrameSchema(
    columns={"Intensity": Column(float), "Outcome": Column(str, required=False)},
    index=Index(int, name="TrialID"),
)


points_schema = DataFrameSchema(
    columns={
        "Intensity": Column(float),
        "n": Column(int),
        "Hits": Column(int),
        "Hit Rate": Column(float),
    },
)


def trials(n: int) -> pd.DataFrame:
    """Simulate trial data."""
    trials = pd.DataFrame.from_records(
        [
            {
                "TrialID": i,
                "Intensity": random.choice([0.0, 0.25, 0.5, 0.75, 1.0]),
            }
            for i in range(n)
        ],
    )
    return trials.set_index("TrialID")


def psi_simulated() -> pd.Series:
    """Simulate psi. Possible duplicate."""
    n = [10] * 5
    x = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    p = gumbel(x, 0.5, 1.0)
    return pd.Series(
        np.random.default_rng().binomial(n, p) / 10,
        pd.Index(x, name="Intensity"),
        name="Hit Rate",
    )


def psi_model() -> pd.Series:
    """See scipy docs for erf."""
    x = np.linspace(0, 1)
    return pd.Series(weibull(x, 0.5, 1), pd.Index(x, name="Intensity"), name="Hit")


def psi(
    psi_observed: pd.Series,
    psi_model: pd.Series,
    psi_simulated: pd.Series,
) -> pd.DataFrame:
    """Simulate psychometric data and combine with observed data & model predictions."""
    s = pd.concat(
        {"Model": psi_model, "Observed": psi_observed, "Simulated": psi_simulated},
        names=["Source"],
    )
    return s.reset_index()


@check_output(points_schema)
def hit_rates(trials: pd.DataFrame) -> pd.DataFrame:
    """Calculate hit rates from point data."""
    hits = trials.groupby("Intensity")["Outcome"].sum().rename("Hits")
    n = trials.groupby("Intensity")["Outcome"].count().rename("n")
    hit_rate = (hits / n).rename("Hit Rate")
    return pd.concat([hits, n, hit_rate], axis=1).reset_index()
