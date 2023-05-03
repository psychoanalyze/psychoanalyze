import random
import pandas as pd
import numpy as np
from pandera import check_output, DataFrameSchema, Column, Index


def weibull(x, alpha, beta):
    return 1 - np.exp(-((x / alpha) ** beta))


def gumbel(x, alpha, beta):
    return 1 - np.exp(-(10 ** (beta * (x - alpha))))


def quick(x, alpha, beta):
    return 1 - 2 ** (-((x / alpha) ** beta))


def log_quick(x, alpha, beta):
    return 1 - 2 ** (-(10 ** (beta * (x - alpha))))


def run(n_trials: int) -> pd.Series:
    """Run a simulation"""
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
    }
)


def trials(n: int) -> pd.DataFrame:
    df = pd.DataFrame.from_records(
        [
            {
                "TrialID": i,
                "Intensity": random.choice([0.0, 0.25, 0.5, 0.75, 1.0]),
            }
            for i in range(n)
        ]
    )
    return df.set_index("TrialID")


def psi_simulated():
    n = [10] * 5
    x = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    p = gumbel(x, 0.5, 1.0)
    return pd.Series(
        np.random.default_rng().binomial(n, p) / 10,
        pd.Index(x, name="Intensity"),
        name="Hit Rate",
    )


def psi_model(
    # x: pd.Index
) -> pd.Series:
    """see:
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.erf.html"""
    x = np.linspace(0, 1)
    return pd.Series(weibull(x, 0.5, 1), pd.Index(x, name="Intensity"), name="Hit")


def psi(psi_observed=None, psi_model=None, psi_simulated=None) -> pd.DataFrame:
    s = pd.concat(
        {"Model": psi_model, "Observed": psi_observed, "Simulated": psi_simulated},
        names=["Source"],
    )
    s.name = "Hit Rate"
    return s.reset_index()


@check_output(points_schema)
def hit_rates(trials: pd.DataFrame):
    hits = trials.groupby("Intensity")["Outcome"].sum().rename("Hits")
    n = trials.groupby("Intensity")["Outcome"].count().rename("n")
    hit_rate = (hits / n).rename("Hit Rate")
    return pd.concat([hits, n, hit_rate], axis=1).reset_index()
